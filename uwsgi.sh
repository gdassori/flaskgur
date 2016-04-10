#!/bin/bash
cd /home/guido/dev/flaskgur
/usr/local/bin/uwsgi -s 127.0.0.1:9992 --wsgi-file /home/guido/dev/flaskgur/app.py --process 2 >> ~/logs/flaskgur.log 2>> ~/logs/flaskgur.log
