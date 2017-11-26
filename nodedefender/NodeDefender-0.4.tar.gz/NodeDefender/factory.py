import logging
from flask import Flask
from flask_moment import Moment
from celery import Celery
from itsdangerous import URLSafeSerializer
from flask_wtf.csrf import CSRFProtect
import os
import sys
import NodeDefender.config.factory
import NodeDefender

csfr = CSRFProtect()
moment = Moment()

def CreateApp():
    app = Flask(__name__)
    mode = NodeDefender.config.general.run_mode()

    if mode == 'Production':
        app.config.from_object('NodeDefender.config.factory.ProductionConfig')
    elif mode == 'Development':
        app.config.from_object('NodeDefender.config.factory.DevelopmentConfig')
    elif mode == 'Testing':
        app.config.from_object('NodeDefender.config.factory.TestingConfig')
    else:
        raise ValueError("Mode {} not known".format(mode))

    app.template_folder = "templates"
    app.static_folder = "templates/frontend/static"
    moment.init_app(app)
    return app

def CreateLogging(app = None):
    app = app or CreateApp()
    if not app.config['LOGGING']:
        loggHandler = logging.StreamHandler(sys.stdout)
    else:
        if app.config['LOGGING_TYPE'] == 'local':
            loggHandler = logging.FileHandler(app.config['LOGGING_NAME'])
        elif app.config['LOGGING_TYPE'] == 'syslog':
            loggHandler = logging.handler.\
                    SysLogHandler(address = (app.config['LOGGING_SERVER'],
                                             int(app.config['LOGGING_PORT'])))
    level = NodeDefender.config.logging.level()
    if level:
        loggHandler.setLevel(level.upper())
    else:
        loggHandler.setLevel("DEBUG")
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    loggHandler.setFormatter(formatter)

    logger = logging.getLogger("NodeDefender")
    logger.setLevel(logging.INFO)
    logger.addHandler(loggHandler)
    return logger, loggHandler

def CreateCelery(app = None):
    app = app or CreateApp()
    if not NodeDefender.config.celery.enabled():
        NodeDefender.logger.info("Concurrency disabled")
        return False

    try:
        celery = Celery(app.name, broker=app.config['CELERY_BROKER_URI'],
                   backend=app.config['CELERY_BACKEND_URI'])
    except KeyError:
        celery = Celery(app.name)
        NodeDefender.logger.info("Concurreny configuration error")
        return False
    
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    NodeDefender.logger.info("Concurrency successfully enabled")
    return celery

class Serializer:
    def __init__(self, app):
        self.serializer = URLSafeSerializer(app.config['SECRET_KEY'])
        self.salt = app.config['SECRET_SALT']

    def loads(self, token):
        return self.serializer.loads(token)

    def dumps(self, string):
        return self.serializer.dumps(string)

    def loads_salted(self, token):
        return self.serializer.loads(token, salt=self.salt)

    def dumps_salted(self, string):
        return self.serializer.dumps(string, salt=self.salt)
