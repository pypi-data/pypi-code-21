# coding: UTF-8

"""
.. module:: monitor
   :platform: Unix
   :synopsis: Entry point for lock monitor. Intended to be ran as a daemon service that facilitates communication
between readers and host. Primary task beyond communication is validation.

.. moduleauthor:: Richard Lowe <richard@modislab.com>

"""

from .monitor import Monitor

__all__ = ['Monitor']
