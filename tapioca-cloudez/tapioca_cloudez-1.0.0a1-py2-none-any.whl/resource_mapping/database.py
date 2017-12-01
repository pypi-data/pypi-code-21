# -*- coding: utf-8 -*-

DATABASE_MAPPING = {
    'database_list': {
        'resource': 'database/',
        'docs': '',
        'methods': ['GET'],
    },
    'database_get': {
        'resource': 'database/{id}/',
        'docs': '',
        'methods': ['GET'],
    },
    'database_create': {
        'resource': 'database/',
        'docs': '',
        'methods': ['POST'],
    },
    'database_update': {
        'resource': 'database/{id}/',
        'docs': '',
        'methods': ['PUT'],
    },
    'database_delete': {
        'resource': 'database/{id}/',
        'docs': '',
        'methods': ['DELETE'],
    },
}
