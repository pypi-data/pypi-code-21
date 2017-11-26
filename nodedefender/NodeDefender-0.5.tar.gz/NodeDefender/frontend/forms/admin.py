from wtforms import StringField, BooleanField, SelectField, SubmitField, validators
from flask_wtf import FlaskForm as Form

def loggingchoices():
    '''
    utility for AdminServerForm
    '''
    for index, choice in enumerate(['debug', 'info', 'warning', 'error',
                                    'critical']):
        yield index, choice

def sqlchoices():
    '''
    utility for AdminServerForm
    '''
    for index, choice in enumerate(['local', 'mysql']):
        yield index, choice

def confparser(section, parameter):
    conf = read_server()
    return conf[section][parameter]

class GeneralForm(Form):
    '''
    Port = StringField('Server Port', [validators.DataRequired(
                        message='port')], default = confparser('BASE', 'port'))
    Debug = BooleanField('Debug Mode',[validators.DataRequired(\
                        message='debug')], default = eval(confparser('BASE', 'debug')))
    Logging = SelectField('Log Level',[validators.DataRequired(message='logging')]\
                          , default = confparser('BASE', 'logging'), \
                          choices = [(key, value) for key, value in loggingchoices()])
    SQLDriver = SelectField('SQL Driver',[validators.DataRequired(message='sqldriver')],\
                            default = confparser('BASE', 'sqldriver'),
                            choices = [(key, value) for key, value in sqlchoices()])
    Submit = SubmitField('Update')
    '''
class DatabaseServerForn(Form):
    SQL = StringField()
    TrackModifications = BooleanField()


class CreateUserForm(Form):
    Firstname = StringField('First name')
    Lastname = StringField('Last name')
    Email = StringField('Email')
    Submit = SubmitField('Create')

class CreateGroupForm(Form):
    Name = StringField('Group Name')
    Email = StringField('Email')
    Description = StringField('Description')
    Submit = SubmitField('Create')

class CreateMQTTForm(Form):
    IPAddr = StringField("IP Address")
    Port = StringField("Port Number")
    Username = StringField("Username")
    Password = StringField("Password")
    Submit = SubmitField("Create")


class UserSettings(Form):
    Firstname = StringField("Firstname")
    Lastname = StringField("Lastname")
    Email = StringField("Email")
    Submit = SubmitField("Update")

class UserPassword(Form):
    Password = StringField("Password")
    Submit = SubmitField("Update")

class UserGroupAdd(Form):
    Name = StringField("Group Name")
    Submit = SubmitField("Update")
