# -*- coding: utf-8 -*-
# situation (c) Ian Dennis Miller

from flask_diamond import Diamond, db
import os
import json


class DebugApp(Diamond):
    pass


def create_app():
    application = DebugApp()
    application.facet("configuration")
    application.facet("logs")
    application.facet("database")
    application.facet("marshalling")
    return(application.app)


def reset_db():
    db.drop_all()
    db.create_all()


def quick():
    tmp_settings()
    app = create_app()
    reset_db()
    return(app)


def tmp_settings():
    os.environ["SETTINGS_JSON"] = json.dumps({
        'LOG': '/tmp/out.log',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/dev.db'
    })
