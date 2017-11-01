import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import steam_api
from flask import Flask, request


# FLASK_APP=tests/auth.py python -m flask run
app = Flask(__name__)


@app.route('/')
def login():
    url = steam_api.auth.get_login_url('http://localhost:5000/process')
    return '<a href={link}>login</a>'.format(link=url)


@app.route('/process')
def process():
    res = steam_api.auth.get_steam_id(**request.args)
    print request.args
    if res['valid']:
        return res['id']
    else:
        return 'false'

