# -*- coding: utf-8 -*-

def set_config_fields(app):
    
    """  Add custom who can read/right fields in the schema so we can know the documents rights 
    
        :param app the eve application
    """
    
    account_definition = {
        'type': 'list',
        'default': [],
        'schema': {
            'type': 'objectid',
            'data_relation': {
                'resource': app.config['ACCOUNT_RESOURCE'],
                'field': '_id',
            },
        }
    }
    domain = app.config['DOMAIN']
    for resource in domain:
        if resource != app.config['ACCOUNT_RESOURCE'] and resource not in app.config['RESOURCE_BLACKLIST']:
            domain[resource]['schema'][app.config['ACL_FIELDS_READ']] = account_definition
            domain[resource]['schema'][app.config['ACL_FIELDS_WRITE']] = account_definition


