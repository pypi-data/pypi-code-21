from NodeDefender.db.sql import SQL
from datetime import datetime
from flask import url_for
from NodeDefender import serializer

class iCPEModel(SQL.Model):
    '''
    iCPE attached to a Node
    '''
    __tablename__ = 'icpe'
    id = SQL.Column(SQL.Integer, primary_key=True)
    node_id = SQL.Column(SQL.Integer, SQL.ForeignKey('node.id'))
    name = SQL.Column(SQL.String(64))

    mac_address = SQL.Column(SQL.String(12), unique=True)
    serial_number = SQL.Column(SQL.String(32))

    ip_dhcp = SQL.Column(SQL.Boolean)
    ip_address = SQL.Column(SQL.String(32))
    ip_subnet = SQL.Column(SQL.String(32))
    ip_gateway = SQL.Column(SQL.String(32))

    firmware = SQL.Column(SQL.String(12))
    hardware = SQL.Column(SQL.String(8))
    
    telnet = SQL.Column(SQL.Boolean)
    ssh = SQL.Column(SQL.Boolean)
    http = SQL.Column(SQL.Boolean)
    snmp = SQL.Column(SQL.Boolean)

    enabled =  SQL.Column(SQL.Boolean)
    date_created = SQL.Column(SQL.DateTime)
    last_online = SQL.Column(SQL.DateTime)
    sensors = SQL.relationship('SensorModel', backref='icpe',
                              cascade='save-update, merge, delete')
    notesticky = SQL.Column(SQL.String(150))
    heat = SQL.relationship('HeatModel', backref="icpe",
                           cascade="save-update, merge, delete")
    power = SQL.relationship('PowerModel', backref="icpe",
                           cascade="save-update, merge, delete")
    events = SQL.relationship('EventModel', backref="icpe",
                           cascade="save-update, merge, delete")

    messages = SQL.relationship('MessageModel', backref='icpe',
                               cascade='save-update, merge, delete')

    def __init__(self, mac_address):
        self.mac_address = mac_address.upper()
        self.enabled = False
        self.date_created = datetime.now()

    def __repr__(self):
        return '<Name %r, Mac %r>' % (self.name, self.mac_address)

    def columns(self):
        return ['name', 'mac_address', 'serial_number', 'ip_dhcp', 'ip_address',
                'ip_subnet', 'ip_gateway', 'firmware', 'hardware', 'telnet',
                'ssh', 'http', 'snmp', 'enabled', 'last_online']

    def to_json(self):
        if self.node:
            node = self.node.name
        else:
            node = 'Not assigned'

        icpe = {'name' : self.name,
                'mac_address' : self.mac_address,
                'ip_address' : self.ip_address,
                'date_created' : str(self.date_created),
                'sensors' : str(len(self.sensors)),
                'mqtt' : [mqtt.to_json() for mqtt in self.mqtt],
                'node' : node,
                'url' : url_for('node_view.nodes_node',
                                name=serializer.dumps(self.node.name))}
        return icpe

class SensorModel(SQL.Model):
    '''
    ZWave Sensor, child of iCPE
    '''
    __tablename__ = 'sensor'
    id = SQL.Column(SQL.Integer, primary_key=True)
    icpe_id = SQL.Column(SQL.Integer, SQL.ForeignKey('icpe.id'))
    
    name = SQL.Column(SQL.String(64))
    sensor_id = SQL.Column(SQL.String(4))
    date_created = SQL.Column(SQL.DateTime)

    vendor_id = SQL.Column(SQL.String(16))
    product_type = SQL.Column(SQL.String(16))
    product_id = SQL.Column(SQL.String(16))
    vendor_name = SQL.Column(SQL.String(64))
    product_name = SQL.Column(SQL.String(64))
    device_type = SQL.Column(SQL.String(48))
    library_type = SQL.Column(SQL.String(48))

    sleepable = SQL.Column(SQL.Boolean)
    wakeup_interval = SQL.Column(SQL.Integer)

    commandclasses = SQL.relationship('CommandClassModel', backref='sensor',
                                cascade='save-update, merge, delete')
    heat = SQL.relationship('HeatModel', backref="sensor",
                           cascade="save-update, merge, delete")
    power = SQL.relationship('PowerModel', backref="sensor",
                           cascade="save-update, merge, delete")
    events = SQL.relationship('EventModel', backref="sensor",
                           cascade="save-update, merge, delete")

    messages = SQL.relationship('MessageModel', backref='sensor',
                               cascade='save-update, merge, delete')


    def __init__(self, sensor_id, sensorinfo = None):
        self.sensor_id = str(sensor_id)
        self.date_created = datetime.now()
        if sensorinfo:
            for key, value in sensorinfo.items():
                setattr(self, key.lower(), value)

            self.name = self.product_name

    def columns(self):
        return ['sensor_id', 'vendor_id', 'product_type', 'product_id',
                'generic_class', 'specific_class', 'sleepable',
                'wakeup_interval', 'name']

    def to_json(self):
        return {'name' : self.name, 'sensor_id' : self.sensor_id,\
                'icpe' : self.icpe.mac_address,\
                'vendor_name' : self.vendor_name,
                'product_name' : str(self.productname)}

class CommandClassModel(SQL.Model):
    __tablename__ = 'commandclass'
    id = SQL.Column(SQL.Integer, primary_key=True)
    sensor_id = SQL.Column(SQL.Integer, SQL.ForeignKey('sensor.id'))
    number = SQL.Column(SQL.String(2))
    name = SQL.Column(SQL.String(20))
    types = SQL.relationship('CommandClassTypeModel', backref="commandclass",
                            cascade="save-update, merge, delete")
    supported = SQL.Column(SQL.Boolean)
    web_field = SQL.Column(SQL.Boolean)
    events = SQL.relationship('EventModel', backref="commandclass",
                           cascade="save-update, merge, delete")

    def __init__(self, number, name):
        self.number = str(number)[:2]
        self.name = name
        self.supported = False

    def commandclasstypes(self):
        return [ctype.number for ctype in self.types]

    def to_json(self):
        return {'name' : self.name, 'number' : self.number, 'webField' :
                self.web_field, 'supported' : self.supported, 'sensor' :
                self.sensor.sensor_id, 'icpe' : self.sensor.icpe.mac_address}

    def columns(self):
        return ['number', 'name']

class CommandClassTypeModel(SQL.Model):
    __tablename__ = 'commandclasstype'
    id = SQL.Column(SQL.Integer, primary_key=True)
    commandclass_id = SQL.Column(SQL.Integer, SQL.ForeignKey('commandclass.id'))
    number = SQL.Column(SQL.String(2))
    name = SQL.Column(SQL.String(40))
    supported = SQL.Column(SQL.Boolean)
    web_field = SQL.Column(SQL.Boolean)
    events = SQL.relationship('EventModel', backref="commandclasstype",
                           cascade="save-update, merge, delete")

    def __init__(self, number):
        self.number = str(number)[:2]
        self.supported = False
