"""Local settings."""
from defcon.plugins import base
import os

SECRET_KEY = 'cepowqjcenwqcnewqoinwqowq'
DEBUG = True


ALERTMANAGER_API = 'http://alertmanager.crto.in/api/v1/'
JIRA_URL = 'https://jira.criteois.com/'
JIRA_USERNAME = os.environ.get('JIRA_USERNAME')
JIRA_PASSWORD = os.environ.get('JIRA_PASSWORD')

PLUGINS_PRODUCTION = [
    # Some static statuses.
    {
        'plugin': 'static',
        'name': 'static test',
        'config': {
            'statuses': [
                base.Status('Test status', 5, 'http://foo/#5'),
                base.Status('Other test', 2, 'http://bar/#1')
            ]
        }
    },
    # For a specific job.
    {
        'plugin': 'alertmanager',
        'name': 'alertmanager-labels',
        'config': {
            'labels': {'perimeter': 'hosting'},
            'defcon': 2,
        }
    },
    # For a specific receiver.
    {
        'plugin': 'alertmanager',
        'name': 'alertmanager-receiver',
        'config': {
            'receiver': 'default',
            'defcon': 2,
        }
    },
]
APLUGINS_PRODUCTION = [
    # Jira
    {
        'plugin': 'jira',
        'name': 'jira-outages',
        'config': {
            'url': JIRA_URL,
            #'username': JIRA_USERNAME,
            #'password': JIRA_PASSWORD,
            'jql': (
                'project = BES'
            ),
            'max_results': 1,
            'defcon': 2,
        }
    },

]

DEFCON_COMPONENTS = {
    'production': {
        'name': 'Production',
        'description': 'All the production perimeter.',
        'link': 'https://github.com/iksaif/defcon/wiki/production',
        'contact': 'escalation@iksaif.net',
        'plugins': PLUGINS_PRODUCTION,
    },
    'observability': {
        'name': 'Observability',
        'description': '',
        'link': 'https://github.com/iksaif/defcon/wiki/observability',
        'contact': 'obs@iksaif.net',
        'plugins': [],
    },
    'storage': {
        'name': 'Storage',
        'description': 'Storage Chef Perimeter',
        'link': 'https://github.com/iksaif/defcon/wiki/storage',
        'contact': 'storage@iksaif.net',
        'plugins': [],
    },
}

DEFCON_PLUGINS = [
    'defcon.plugins.static.StaticPlugin',
    'defcon.plugins.alertmanager.AlertmanagerPlugin',
    'defcon.plugins.jira.JiraPlugin',
]
