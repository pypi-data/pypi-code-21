# coding: UTF-8

"""
.. module:: Platform detection
   :platform: Unix
   :synopsis: Checks to see what platform the monitor is running on.

.. moduleauthor:: Richard Lowe <richard@modislab.com>

"""

from .platform_detect import isRaspberryPi, isBeagleBoneBlack

__all__ = ['isRaspberryPi', 'isBeagleBoneBlack']
