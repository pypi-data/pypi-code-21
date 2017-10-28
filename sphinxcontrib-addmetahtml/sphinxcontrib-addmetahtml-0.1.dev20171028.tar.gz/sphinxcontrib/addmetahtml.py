#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sphinx.application import ExtensionError

def insert_content(app, pagename, templatename, context, doctree):
    if not app.config.addmetahtml_enabled:
        return

    metatags = context.get('metatags', '')
    metatags += app.config.addmetahtml_content
    context['metatags'] = metatags

def validate_config(app):
    if not app.config.addmetahtml_content:
        raise ExtensionError("Please set a value for 'addmetahtml_content'")

def setup(app):
    app.add_config_value('addmetahtml_enabled', True, 'html')
    app.add_config_value('addmetahtml_content', '', 'html')
    app.connect('builder-inited', validate_config)
    app.connect('html-page-context', insert_content)

    return
    {
        'version': '0.1'
    }
