#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from google.cloud import storage
from flask import current_app
from flask_login import current_user


def build_filename(filename):
    """
    :return: /path/timestamp/filename"""
    if '/' not in filename:
        filename = '/' + filename
    path, name = filename.rsplit('/', 1)
    return '%s/%s/%s-%s' % (path, current_user.id, datetime.utcnow().strftime("%Y%m%d%H%M%S%f"), name) # noqa


def get_blob(filename):
    bucket_name = current_app.config['STORAGE_BUCKET_NAME']
    bucket = storage.Client().get_bucket(bucket_name)
    return bucket.blob(filename)


def upload_file(filename, file_stream):
    # TODO add permission control logic
    blob = get_blob(build_filename(filename))
    blob.upload_from_string(file_stream)
    url = blob.public_url
    current_app.logger.debug('return of upload is %s', url)
    return url
