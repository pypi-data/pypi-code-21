from NodeDefender.db.sql import SQL
from NodeDefender.db.sql.icpe import iCPEModel
from datetime import datetime
import NodeDefender

mqtt_icpe = SQL.Table('mqtt_icpe',
                     SQL.Column('mqtt_id', SQL.Integer, SQL.ForeignKey('mqtt.id')),
                     SQL.Column('icpe_id', SQL.Integer, SQL.ForeignKey('icpe.id')))


class MQTTModel(SQL.Model):
    __tablename__ = 'mqtt'
    id = SQL.Column(SQL.Integer, primary_key=True)
    host = SQL.Column(SQL.String(128))
    port = SQL.Column(SQL.Integer)
    username = SQL.Column(SQL.String(64))
    password = SQL.Column(SQL.String(64))
    

    icpes = SQL.relationship('iCPEModel', secondary=mqtt_icpe,
                            backref=SQL.backref('mqtt', lazy='dynamic'))
    date_created = SQL.Column(SQL.DateTime)

    def __init__(self, host, port, username = None, password = None):
        self.host = host
        self.port = int(port)
        self.username = username
        self.password = password
        self.date_created = datetime.now()

    def online(self):
        return NodeDefender.db.mqtt.online(self.host, self.port)

    def to_json(self):
        return {'id' : str(self.id), 'host' : self.host, 'port' : self.port,
                'date_created' : str(self.date_created),
                'online' : True, 'username ' : None, 'password' : None,
                'groups' : [group.name for group in self.groups],
                'icpes' : [icpe.mac_address for icpe in self.icpes]}
