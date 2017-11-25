#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Module gitwebui
"""

__version_info__ = (0, 1, 0)
__version__ = '.'.join([str(val) for val in __version_info__])

__namepkg__ = "gitwebui"
__desc__ = "GitWebUi module"
__urlpkg__ = "https://github.com/fraoustin/gitwebui.git"
__entry_points__ = {
        'console_scripts': [
            'gitwebui = gitwebui.main:main',
        ],
    }
