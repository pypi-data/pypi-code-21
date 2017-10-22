#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .helpers import SetHelper
from observablePy import Observable, observable_property
import copy


class Lifepo4wered(Observable):
    def __init__(self):
        super(Lifepo4wered, self).__init__()
        self.instanceState = {
            "batteryVoltage": 0,
            "batteryRate": 0.0,
            "usbPowerSourceVoltage": 0,
            "usbPowerSourcePluggedIn": False,
            "touchState": -1
        }
        self._previousInstanceState = {}

        self.addObservableElement("state")

    def _diffuseChanges(self):
        if self.hasObservers():
            areSame = SetHelper.areSame(self._previousInstanceState,
                                        self.instanceState)
            if areSame is False:
                self.diffuse(self._previousInstanceState, self.instanceState)
                self._previousInstanceState = copy.deepcopy(self.instanceState)
