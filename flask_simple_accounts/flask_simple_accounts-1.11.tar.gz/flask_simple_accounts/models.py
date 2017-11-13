import datetime

from . import helper
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    #__tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, index=True)
    salt = db.Column(db.String)
    password_hash = db.Column(db.String)
    email_verification = db.relationship("EmailVerification", uselist=False, back_populates="user")
    registered_on = db.Column(db.DateTime)

    is_authenticated = db.Column(db.Boolean)
    is_active = db.Column(db.Boolean)
    is_anonymous = db.Column(db.Boolean)

    def __init__(self, password):
        self.email = None
        self.salt = helper.generate_salt()
        self.password_hash = helper.hash_password(password, self.salt)
        self.email_verified = False
        self.registered_on = datetime.datetime.now()

        # fields required for flask_login
        self.is_authenticated = False
        self.is_active = False
        self.is_anonymous = True

    def get_id(self):
        # function required for flask_login
        return str(self.email)

    def mark_user_as_authenticated(self, callback=None):
        self.is_authenticated = True
        self.is_anonymous = False

        if callback:
            callback()

    def mark_user_as_anonymous(self, callback=None):
        self.is_authenticated = False
        self.is_anonymous = True

        if callback:
            callback()


class EmailVerification(db.Model):
    #__tablename__ = 'email_verifications'

    id = db.Column(db.Integer, primary_key=True)

    time_created = db.Column(db.DateTime())
    code = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='email_verification')
    unverified_email = db.Column(db.String(120), unique=True, index=True)

    def __init__(self, code, user, unverified_email):
        self.code = code
        self.user = user
        self.unverified_email = unverified_email
        self.time_created = datetime.datetime.now()

