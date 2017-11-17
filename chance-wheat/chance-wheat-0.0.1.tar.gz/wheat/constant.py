# -*- coding: utf-8 -*-
# Author: heheqiao <614400597@qq.com>
PACKAGES = [
    'chance-paddy', 'chance-orm', 'chance-config', 'chance-mock-logger'
]

PACKAGE_VERSION = {
    'chance-paddy': '1.2.0',
    'chance-orm': '1.2.1',
    'chance-config': '0.0.1',
    'chance-mock-logger': '0.0.3',
    'test': '0.0.1'
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
