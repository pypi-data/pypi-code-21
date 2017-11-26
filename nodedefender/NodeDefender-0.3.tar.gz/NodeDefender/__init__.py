from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os
from datetime import datetime
import NodeDefender.config
from NodeDefender.factory import CreateApp, CreateLogging, CreateCelery, Serializer
from gevent import monkey
monkey.patch_all()

# General Info
hostname = os.uname().nodename
release = 'Alpha-2'
date_loaded = datetime.now()

# Initialize the Flask- Application
app = CreateApp()

# Setup logging
logger, loggHandler = CreateLogging(app)

# Initialize SocketIO
try:
    socketio = SocketIO(app, message_queue=app.config['CELERY_BROKER_URI'],
                    async_mode='gevent')
except KeyError:
    socketio = SocketIO(app, async_mode='gevent')

# Initialize Celery
celery = CreateCelery(app)

# For the Authentication
LoginMan = LoginManager()
LoginMan.init_app(app)
LoginMan.login_view = 'auth_view.authenticate'
LoginMan.login_message_category = "info"

bcrypt = Bcrypt(app)

serializer = Serializer(app)

# Report that startup is successfull
logger.info('NodeDefender Succesfully started')
import NodeDefender.decorators
import NodeDefender.db
import NodeDefender.mqtt
import NodeDefender.icpe
import NodeDefender.mail
import NodeDefender.frontend
