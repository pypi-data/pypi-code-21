#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    COPYRIGHT (C) 2016 by Sebastian Stigler

    NAME
        gpio.py -- gpio dummy

    DESCRIPTION
        This module will be used if the ``RPi.GPIO`` is not available.
        The functions will only create a logmessage.

    FIRST RELEASE
        2016-05-31  Sebastian Stigler  sebastian.stigler@hs-aalen.de

"""

import logging
import sys

from colorama import Fore, Back, Style

_logger = logging.getLogger(__name__)

BOARD = 'BOARD'
BCM = 'BCM'
OUT = 'OUT'
LOW = 'LOW'
HIGH = 'HIGH'

LEDS = [-1 for _ in range(27)]


def _update_leds():
    txt = []
    for entry in LEDS:
        if entry == 1:
            txt.append(Style.BRIGHT + Fore.RED + Back.GREEN + 'X')
        elif entry == 0:
            txt.append(Style.NORMAL + Fore.BLACK + Back.GREEN + '.')
        else:
            txt.append(Style.BRIGHT + Fore.YELLOW + Back.CYAN + ',')
    sys.stdout.write(''.join(txt) + Style.RESET_ALL)
    sys.stdout.write('\r' * len(txt))
    sys.stdout.flush()


def setmode(mode):
    """Set the pin mode"""
    _logger.debug('Mode is set to {mode}'.format(mode=mode))


def setup(pin, direction, pull=None):
    """Set the pin direction"""
    _logger.debug('Pin {pin} is configured as {direction}PUT'.format(
        pin=pin, direction=direction))
    if direction == 'OUTPUT' and 1 <= pin <= 27:
        global LEDS
        LEDS[pin-1] = 0
        _update_leds()


def setwarnings(state):
    """Set warnings on or off"""
    _logger.debug('Warnings are set to {state}'.format(state=repr(state)))


def output(pin, state):
    """Set pin state"""
    _logger.debug('Pin {pin} is set to {state}'.format(pin=pin, state=state))
    global LEDS
    if state == HIGH and 1 <= pin <= 27:
        LEDS[pin-1] = 1
    if state == LOW and 1 <= pin <= 27:
        LEDS[pin-1] = 0
    _update_leds()

# vim: ft=python ts=4 sta sw=4 et ai
