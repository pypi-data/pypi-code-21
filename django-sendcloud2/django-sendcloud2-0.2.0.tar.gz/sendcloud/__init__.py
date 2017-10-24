# -*- encoding: utf8 -*-

# clone and modify from freeyoung@github.com/django-sendcloud

from sendcloud.email import EmailBackend

# sample
SENDCLOUD = {
    'email': {
        'api_user': '',
        'api_key': '',
    },
    'sms': {
        'sms_user': '',
        'sms_key': '',
        'muted': True
    },
}
