#!/usr/bin/python3
# -*- coding: utf-8 -*-

import lifepo4weredPy
from .LedStateEnum import ledStateEnum


class Led():
    @property
    def state(self):
        return ledStateEnum(lifepo4weredPy.read(
                            lifepo4weredPy.variablesEnum.LED_STATE))

    def on(self):
        lifepo4weredPy.write(lifepo4weredPy.variablesEnum.LED_STATE,
                             lifepo4weredPy.LED_STATE_ON)

    def off(self):
        lifepo4weredPy.write(lifepo4weredPy.variablesEnum.LED_STATE,
                             lifepo4weredPy.LED_STATE_OFF)

    def pulse(self):
        lifepo4weredPy.write(lifepo4weredPy.variablesEnum.LED_STATE,
                             lifepo4weredPy.LED_STATE_PULSING)

    def flash(self):
        lifepo4weredPy.write(lifepo4weredPy.variablesEnum.LED_STATE,
                             lifepo4weredPy.defines.LED_STATE_FLASHING)
