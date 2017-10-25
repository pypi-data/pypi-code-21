#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf_storage import (
    MultipleFileField, FileField, FileDisplayField, StorageForm
)


class RegistrationForm(StorageForm):
    website = StringField('website')
    personal_apply = FileField()
    business_license = MultipleFileField()
    submit = SubmitField('確 認')


class ProfileForm(FlaskForm):
    website = StringField('website')
    personal_apply = FileDisplayField()
    business_license = FileDisplayField()
