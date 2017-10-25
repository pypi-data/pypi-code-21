#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import current_app
from flask_wtf import FlaskForm
from .fields import MultipleFileField, FileField


class StorageForm(FlaskForm):
    def upload(self):
        """save files to google storage"""
        file_fields = [
            field for field in self if isinstance(field, FileField) and
            not isinstance(field, MultipleFileField)
        ]
        multi_file_fields = [
            field for field in self if isinstance(field, MultipleFileField)
        ]
        current_app.logger.debug('file_fields are %s', file_fields)

        for field in file_fields:
            self._fields[field.name].data = field.upload()

        for field in multi_file_fields:
            self._fields[field.name].data = list(field.upload())
