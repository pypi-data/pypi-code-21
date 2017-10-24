# coding: UTF-8

"""
.. module:: Config
   :platform: Unix
   :synopsis: Configuration of the monitor loaded from object

.. moduleauthor:: Richard Lowe <richard@modislab.com>

"""

import os


def load_config():
    """Load config from environment

    """
    mode = os.environ.get('MODE')

    try:
        if mode == 'PRODUCTION':
            from .production import ProductionConfig
            return ProductionConfig
        else:
            from .development import DevelopmentConfig
            return DevelopmentConfig
    except ImportError:
        from .default import Config
        return Config
