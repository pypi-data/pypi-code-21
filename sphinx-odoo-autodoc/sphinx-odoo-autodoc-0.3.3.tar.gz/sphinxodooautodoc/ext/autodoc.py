#! /usr/bin/env python
# -*- coding: utf-8 -*-

import imp
import os
import sys


def setup(app):
    """
    Setup function used by sphinx, when loading sphinxodooautodoc as sphinx extension
    """
    app.add_config_value('sphinxodooautodoc_addons', [], True)
    app.add_config_value('sphinxodooautodoc_root_path', '', True)
    app.add_config_value('sphinxodooautodoc_addons_path', [], True)
    app.connect('builder-inited', load_modules)

    return {'version': '0.3.3'}


def load_modules(app):
    def load_odoo_modules(addons):
        for module_name in addons:
            info = odoo.modules.module \
                .load_information_from_description_file(module_name)
            try:
                f, path, descr = imp.find_module(
                    module_name,
                    odoo.tools.config['addons_path'].split(',')
                )
            except ImportError:
                # skip non module directories
                continue
            # we use odoo.__name__ which can be 'openerp' or 'odoo' (in 10.0)
            # since we alias the import of odoo.
            mod = imp.load_module(
                '%s.addons.%s' % (odoo.__name__, module_name),
                f, path, descr)
            setattr(odoo.addons, module_name, mod)
            setattr(getattr(odoo.addons, module_name),
                    '__doc__', info['description'])

    addons = app.env.config.sphinxodooautodoc_addons
    addons_path = ','.join(app.env.config.sphinxodooautodoc_addons_path)

    if(app.env.config.sphinxodooautodoc_root_path):
        sys.path.append(app.env.config.sphinxodooautodoc_root_path)
    try:
        import odoo
    except ImportError:
        import openerp
        odoo = openerp

    if not addons_path:
        addons_path = os.environ.get('ODOO_ADDONS_PATH', '')

    if addons_path:
        odoo.tools.config.parse_config([
            '--addons-path=%s' % addons_path,
        ])

    load_odoo_modules(addons)
