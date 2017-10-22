#!/usr/bin/python3
# -*- coding: utf-8 -*-

import copy
from observablePy import Observable, observable_property
import lifepo4weredPy


class USBPowerSource(Observable):
    def __init__(self):
        super(USBPowerSource, self).__init__()
        self.instanceState = {
          "voltage": 0,
          "pluggedIn": False,
        }
        self.addObservableElement("voltage")
        self.addObservableElement("pluggedIn")

    @property
    def voltage(self):
        return lifepo4weredPy.read(lifepo4weredPy.variablesEnum.VIN)

    @property
    def pluggedIn(self):
        return lifepo4weredPy.read(lifepo4weredPy.variablesEnum.VIN) > 0

    def _diffuseChanges(self):
        voltage = self.voltage

        if (voltage != self.instanceState["voltage"]):
            previousState = copy.deepcopy(self.instanceState)

            self.instanceState["voltage"] = voltage
            self.instanceState["pluggedIn"] = voltage > 0

            self.diffuse(previousState, self.instanceState)
