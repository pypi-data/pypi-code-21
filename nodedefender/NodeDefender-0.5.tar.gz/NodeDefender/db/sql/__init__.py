from NodeDefender import app
from flask_sqlalchemy import SQLAlchemy

if not app.config['DATABASE']:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    SQL = SQLAlchemy(app)
else:
    SQL = SQLAlchemy(app)

from NodeDefender.db.sql.group import GroupModel
from NodeDefender.db.sql.user import UserModel
from NodeDefender.db.sql.node import NodeModel, LocationModel
from NodeDefender.db.sql.icpe import iCPEModel, SensorModel,\
        CommandClassModel, CommandClassTypeModel
from NodeDefender.db.sql.data import PowerModel, HeatModel, EventModel
from NodeDefender.db.sql.conn import MQTTModel
from NodeDefender.db.sql.message import MessageModel

if not app.config['DATABASE']:
    SQL.create_all()
