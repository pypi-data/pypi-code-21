from NodeDefender import bcrypt
from NodeDefender.db.sql import SQL
from datetime import datetime

class UserModel(SQL.Model):
    '''
    Table of Users

    Users is a part of a Group
    Password is encrypted
    '''
    __tablename__ = 'user'
    id = SQL.Column(SQL.Integer, primary_key=True)
    firstname = SQL.Column(SQL.String(30))
    lastname = SQL.Column(SQL.String(40))
    email = SQL.Column(SQL.String(191), unique=True)
    password = SQL.Column(SQL.String(191))
    
    enabled = SQL.Column(SQL.Boolean())
    date_confirmed = SQL.Column(SQL.DateTime)
    date_created = SQL.Column(SQL.DateTime)
    
    date_last_login = SQL.Column(SQL.DateTime)
    date_current_login = SQL.Column(SQL.DateTime)
    last_login_ip = SQL.Column(SQL.String(100))
    current_login_ip = SQL.Column(SQL.String(100))
    login_count = SQL.Column(SQL.Integer)
   
    technician = SQL.Column(SQL.Boolean)
    administrator = SQL.Column(SQL.Boolean)
    superuser = SQL.Column(SQL.Boolean)
    
    messages = SQL.relationship('MessageModel', backref='user',
                              cascade='save-update, merge, delete')

    def __init__(self, email):
        self.email = email
        self.firstname = None
        self.lastname = None
        self.password = None
        self.active = False
        self.date_confirmed = None
        self.date_created = datetime.now()

        self.technician = False
        self.administrator = False
        self.superuser = False
    
    def columns(self):
        return ['firstname', 'lastname']

    def to_json(self):
        return {'firstName': self.firstname,
                'lastName' : self.lastname,
                'email' : self.email,
                'role' : self.get_role(),
                'enabled' : self.enabled,
                'dateCreated' : str(self.date_created),
                'dateConfirmed' : str(self.date_confirmed)}

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def verify_password(self, password):
        if bcrypt.check_password_hash(self.password, password):
            return True
        else:
            return False

    def get_role(self):
        if self.superuser:
            return 'superuser'
        elif self.administrator:
            return 'administrator'
        elif self.technician:
            return 'technician'
        else:
            return 'observer'

    def set_role(self, role):
        if role.lower() == 'observer':
            self.technician = False
            self.administrator = False
            self.superuser = False
        elif role.lower() == 'technician':
            self.technician = True
            self.administrator = False
            self.superuser = False
        elif role.lower() == 'administrator':
            self.technician = True
            self.administrator = True
            self.observer = False
        elif role.lower() == 'superuser':
            self.technician = True
            self.administrator = True
            self.superuser = True
        else:
            raise AttributeError('Wrong kind of role')

    def has_role(self, role):
        try:
            return getattr(self, role.lower())
        except AttributeError:
            return None
