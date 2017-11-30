# -*- coding: utf-8 -*-
# Author: heheqiao <614400597@qq.com>
PACKAGE_VERSION = {
    'chance-paddy': '1.2.1',
    'chance-orm': '1.2.2',
    'chance-config': '0.0.4',
    'chance-mock-logger': '0.0.1',
}

CONF_RULES = {
    'like shown here.': 'like shown here.\nimport sphinx_rtd_theme',
    "html_theme = 'alabaster'": "html_theme = 'sphinx_rtd_theme'",
    '# html_theme_options = {}':
        (
            '# html_theme_options = {}\nhtml_theme_path = '
            '[sphinx_rtd_theme.get_html_theme_path()]'
        )
}
