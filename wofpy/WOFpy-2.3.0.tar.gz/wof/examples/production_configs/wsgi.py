#!/usr/bin/env python

from runserver import app as application
application.secret_key = 'Thisismysecretkey'
