import click
from flask_restful import Api


@click.command()
def start():
    from flask import Flask
    from ..web import add_api
    from ...config import config as c
    """ start task database web service """
    app = Flask(__name__)
    api = Api(app)
    add_api(api)
    app.run(host=c['host'], port=c['port'], debug=c['debug'])
