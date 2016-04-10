import binascii
import hashlib
from flask import Flask, request, g, redirect, url_for, abort, render_template, send_from_directory
from PIL import Image
import sqlite3
import os
import time

DEBUG              = True
BASE_DIR           = '/home/guido/Data/flaskgur/'
UPLOAD_DIR         = BASE_DIR + 'pics'
DATABASE           = BASE_DIR + 'flaskgur.db'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
BASE_PATH          = '/flaskgur/'

app = Flask(__name__)
app.config.from_object(__name__)

def init_db():
    with app.app_context():
        db = connect_db()
        with app.open_resource(BASE_DIR+'schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Make sure extension is in the ALLOWD_EXTENSIONS set
def check_extension(extension):
    return extension in ALLOWED_EXTENSIONS

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# Return a list of the last 25 uploaded images	
def get_last_pics():
    cur = g.db.execute('select filename from pics order by id desc limit 25')
    filenames = [row[0] for row in cur.fetchall()]
    return filenames

def get_related_pics(filename):
    pics = get_last_pics()
    pics.pop(pics.index(filename))
    return pics

# Insert filename into database	
def add_pic(filename):
    g.db.execute('insert into pics (filename) values (?)', [filename])
    g.db.commit()

# Generate thumbnail image
def gen_thumbnail(filename):
    height = width = 200
    original = Image.open(os.path.join(app.config['UPLOAD_DIR'], filename))
    thumbnail = original.resize((width, height), Image.ANTIALIAS)
    thumbnail.save(os.path.join(app.config['UPLOAD_DIR'], 'thumb_'+filename))
	
# Taken from flask example app
@app.before_request
def before_request():
    try:
       g.db = connect_db()
    except sqlite3.OperationalError:
        init_db()
        g.db = connect_db()

# Taken from flask example app
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
        
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', basepath=BASE_PATH), 404

@app.route(BASE_PATH)
def index():
    return render_template('index.html', pics=get_last_pics(), basepath=BASE_PATH)

@app.route(BASE_PATH + 'upload', methods=['POST'])
def upload_pic():
    file = request.files['file']
    try:
        extension = file.filename.rsplit('.', 1)[1].lower()
        if file and check_extension(extension):
            # Salt and hash the file contents
            filename = '{}.{}'.format(hashlib.md5('{}{}'.format(str(binascii.hexlify(file.read())),
                                                                str(int(time.time()))).encode()).hexdigest(),
                                      extension)
            file.seek(0) # Move cursor back to beginning so we can write to disk
            file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
            add_pic(filename)
            gen_thumbnail(filename)
            return redirect(url_for('show_pic', filename=filename, basepath=BASE_PATH))
        else: # Bad file extension
            abort(404)
    except IndexError:
        abort(404)

@app.route(BASE_PATH + 'show')
def show_pic():
    filename = request.args.get('filename', '')
    return render_template('index.html',
                           filename=filename,
                           basepath=BASE_PATH,
                           pics=get_related_pics(filename))

@app.route(BASE_PATH + 'pics/<filename>')
def return_pic(filename):
    return send_from_directory(app.config['UPLOAD_DIR'], filename)
	
if __name__ == '__main__':
    try:
        with open(DATABASE, 'rb') as f:
            f.readline()
    except:
        init_db()
    app.run(debug=DEBUG, host='0.0.0.0')