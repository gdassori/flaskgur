#!/bin/bash
cd /home/guido/dev/flaskgur
venv/bin/uwsgi --enable-threads -s 127.0.0.1:9992 --wsgi-file /home/guido/dev/flaskgur/flaskgur.py --process 2 >> ~/logs/flaskgur.log 2>> ~/logs/flaskgur.log
