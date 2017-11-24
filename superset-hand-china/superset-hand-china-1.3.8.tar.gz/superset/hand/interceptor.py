from flask import request, g
from flask_babel import Babel, gettext as _
import requests
import json
import logging
from flask_login import login_user, logout_user

def intercept(self):

    # set multi language
    from superset import app
    config = app.config
    c = request.args.get("lang")
    if c != None:
        config['BABEL_DEFAULT_LOCALE'] = c
        babel = Babel(app)

    # remember the url before login
    if str(g.user).startswith('<flask_login.AnonymousUserMixin'):
        app.config['request_url'] = request.url

    # oauth authorization
    logging.info("url = " + request.path)
    logging.info("user_token = " + str(request.args.get('user_token')))

    # login by access_token
    if config['OAUTH2_AUTHORIZE'] and request.args.get('user_token') != None:
        user_token = request.args.get('user_token')
        headers = {
            "Authorization": 'bearer ' + user_token
        }
        try:
            user_text = requests.get(config['OAUTH2_CHECK_TOKEN_URL'], headers=headers)
            try:
                username = json.loads(user_text.text)['username']
                try:
                    user = self.appbuilder.sm.find_user(username)
                    login_user(user, remember=False)
                except Exception as e:
                    return '<h2>user is not exist</h2>'
            except Exception as e:
                return '<h2>user_token is invalidate<h2>'
        except Exception as e:
            return '<h2>connect failed, please reconnect</h2>'

    return 'success'

   