from setuptools import setup

import flask_notifyAll

version = flask_notifyAll.__version__
description = 'Simple tool which will provide sms and email notifications'

setup_info = {
    'name': 'flask_notifyAll',
    'version': version,
    'license': 'MIT',
    'author': 'Mike Yusko',
    'url': 'https://github.com/MichaelYusko/flask-notifyAll',
    'author_email': 'freshjelly12@yahoo.com',
    'description': description,
    'packages': ['flask_notifyAll'],
    'keywords': ["flask", "sms", "notifications", "email", "send"],
    'install_requires': ['twilio==6.3.0'],
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License'
    ],
}


setup(**setup_info)
