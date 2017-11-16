# -*- coding: utf-8 -*-
"""上传文件的服务端
Gunicorn provides many command-line options – see gunicorn -h. For example,
to run a Flask application with 4 worker processes (-w 4)
binding to localhost port 4000 (-b 127.0.0.1:4000):

.. code-block::

    gunicorn -w 4 -b 127.0.0.1:4000 simple_upload:app

When source change, unicorn can add --reload option

"""
import logging

from flask import Flask, request
from flask.views import MethodView


# 可以把下面的配置写到配置文件
DEBUG = False
# 以下配置可以在环境变量SIMPLE_UPLOAD_SETTINGS
RANDOM_KEY = ''
CLIENT_PREFIX = ''
SERVER_PREFIX = ''

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('SIMPLE_UPLOAD_SETTINGS', silent=True)

app.logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)


class UploadError(Exception):
    pass


class UploadExtension(object):
    def __init__(self, app):
        self.client_prefix = app.config['CLIENT_PREFIX']
        self.server_prefix = app.config['SERVER_PREFIX']
        self.logger = app.logger
        self.logger.info('client_prefix: %s, server_prefix: %s',
                         self.client_prefix,
                         self.server_prefix)
        assert self.client_prefix and self.server_prefix

    def save(self, f, path):
        if not path.startswith(self.client_prefix):
            msg = 'File {} not starts with {}'.format(path, self.client_prefix)
            raise UploadError(msg)
        server_path = self.server_prefix + path[len(self.client_prefix):]
        f.save(server_path)
        msg = 'Save success! local-{}, server-{}'.format(path, server_path)
        self.logger.warn(msg)
        return msg


ue = UploadExtension(app)


@app.before_request
def before_request():
    # 鉴权
    r = request.args.get('r') or request.form.get('r')
    if r != app.config['RANDOM_KEY']:
        return 'no permission'


@app.errorhandler(UploadError)
def handle_upload_error(error):
    msg = str(error)
    app.logger.warn(msg)
    return msg


class UploadView(MethodView):
    def get(self):
        app.logger.error('GET return ok')
        return 'ok'

    def post(self):
        f = request.files.get('f')
        path = request.form.get('path')
        if not f:
            return 'field f is required'
        if not path:
            return 'field path is required'
        return ue.save(f, path)


app.add_url_rule('/', view_func=UploadView.as_view('upload'))
