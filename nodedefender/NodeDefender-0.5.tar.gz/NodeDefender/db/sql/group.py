from NodeDefender.db.sql import SQL
from datetime import datetime
from NodeDefender.db.sql.node import LocationModel
import NodeDefender
from flask import url_for

user_list = SQL.Table('user_list',
                     SQL.Column('group_id', SQL.Integer,
                               SQL.ForeignKey('group.id')),
                     SQL.Column('user_id', SQL.Integer,
                               SQL.ForeignKey('user.id'))
                    )
node_list = SQL.Table('node_list',
                     SQL.Column('group_id', SQL.Integer,
                               SQL.ForeignKey('group.id')),
                     SQL.Column('node_id', SQL.Integer,
                               SQL.ForeignKey('node.id'))
                    )

mqtt_list = SQL.Table('mqtt_list',
                     SQL.Column('group_id', SQL.Integer,
                               SQL.ForeignKey('group.id')),
                     SQL.Column('mqtt_id', SQL.Integer,
                               SQL.ForeignKey('mqtt.id'))
                    )

class GroupModel(SQL.Model):
    '''
    Representing one group containing iCPEs and Users
    '''
    __tablename__ = 'group'
    id = SQL.Column(SQL.Integer, primary_key=True)
    name = SQL.Column(SQL.String(50))
    email = SQL.Column(SQL.String(120))
    description = SQL.Column(SQL.String(250))
    date_created = SQL.Column(SQL.DateTime)
    users = SQL.relationship('UserModel', secondary=user_list, backref='groups')
    mqtts = SQL.relationship('MQTTModel', secondary=mqtt_list, backref='groups')
    nodes = SQL.relationship('NodeModel', secondary=node_list, backref='groups')
    location = SQL.relationship('LocationModel', uselist=False,
                               backref='group')

    messages = SQL.relationship('MessageModel', backref='group',
                               cascade='save-update, merge, delete')

    def __init__(self, name, email = None, description = None):
        self.name = name
        self.email = email
        self.description = str(description)
        self.date_created = datetime.now()
    
    def columns(self):
        return ['name', 'email', 'description']

    def to_json(self):
        if self.location:
            location = self.location.to_json()
        else:
            location = None
        return {'name' : self.name, 'email' : self.email, 'created' :
                str(self.date_created), 'description' : self.description,
                'users' : [user.email for user in self.users],
                'nodes' : [node.name for node in self.nodes],
                'location' : location,
                'url' : url_for('admin_view.admin_group', name =
                                NodeDefender.serializer.dumps(self.name))}
