from wtforms import StringField, SubmitField, BooleanField, PasswordField
from flask_wtf import FlaskForm as Form
from wtforms.validators import DataRequired, EqualTo

class LoginForm(Form):
    """The default login form"""
    email = StringField('Email Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me', default=False)
    submit = SubmitField('Submit')

class RegisterForm(Form):
    email = StringField('Email', validators=[DataRequired()])
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),
                                                    EqualTo('confirm_password')])
    confirm_password = PasswordField('Retype Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RegisterTokenForm(Form):
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),
                                                    EqualTo('confirm_password')])
    confirm_password = PasswordField('Retype Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class PasswordForm(Form):
    password = PasswordField('Password', validators=[DataRequired(),
                                                    EqualTo('confirm_password')])
    confirm_password = PasswordField('Retype Password', validators=[DataRequired()])
    submit = SubmitField('Submit')
