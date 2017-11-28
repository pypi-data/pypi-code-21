# -*- coding: utf-8 -*-
# situation (c) Ian Dennis Miller

from flask_diamond import Diamond


class DebugApp(Diamond):
    pass


def create_app():
    application = DebugApp()
    application.facet("configuration")
    application.facet("logs")
    application.facet("database")
    application.facet("marshalling")
    # application.facet("blueprints")
    # application.facet("accounts")
    # application.facet("signals")
    # application.facet("forms")
    # application.facet("error_handlers")
    # application.facet("request_handlers")
    # application.facet("administration")
    return(application.app)
