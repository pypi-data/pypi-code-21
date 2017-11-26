from wtforms import StringField, BooleanField, SelectField, SubmitField, validators
from flask_wtf import FlaskForm as Form

class LocationForm(Form):
    Street = StringField("Steet", [validators.DataRequired()])
    City = StringField("City", [validators.DataRequired()])
    Geolat = StringField("Latitude", [validators.DataRequired()])
    Geolong = StringField("Longitude", [validators.DataRequired()])
    Submit = SubmitField()

class iCPEForm(Form):
    Alias = StringField('Alias', [validators.InputRequired()])
    Comment = StringField('Comment', validators=[])
    Submit = SubmitField()

class SensorForm(Form):
    Alias = StringField('Alias', [validators.InputRequired()])
    Submit = SubmitField()

class NodeCreateForm(Form):
    Name = StringField('Name', [validators.DataRequired()])
    Group = StringField('Group')
    Mac = StringField('Mac')
    Street = StringField('Street', [validators.DataRequired()])
    City = StringField('City', [validators.DataRequired()])
    Submit = SubmitField('Add')
