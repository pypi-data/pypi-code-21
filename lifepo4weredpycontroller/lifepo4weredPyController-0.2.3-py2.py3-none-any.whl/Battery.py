#!/usr/bin/python3
# -*- coding: utf-8 -*-

from observablePy import Observable, observable_property
import lifepo4weredPy
import copy

BATTERY_FULL = 3392  # mVolt


class Battery(Observable):
    def __init__(self):
        super(Battery, self).__init__()
        self.instanceState = {
            "voltage": 0,
            "rate": 0.0,
        }

        self.addObservableElement("voltage")
        self.addObservableElement("rate")

    def clear(self):
        self.instanceState["voltage"] = 0
        self.instanceState["rate"] = 0.0

    @property
    def voltage(self):
        return lifepo4weredPy.read(lifepo4weredPy.variablesEnum.VBAT)

    @property
    def rate(self):
        return self._computeRate(self.voltage)

    def _computeRate(self, actualVoltage):
        shutdownVoltage = lifepo4weredPy.read(
                                lifepo4weredPy.variablesEnum.VBAT_SHDN)

        batteryNomalizedVolt = (actualVoltage
                                if actualVoltage < BATTERY_FULL
                                else BATTERY_FULL) - shutdownVoltage

        if (batteryNomalizedVolt <= 0):
            return 0
        else:
            return batteryNomalizedVolt / (BATTERY_FULL - shutdownVoltage)

    def _diffuseChanges(self):
        voltage = self.voltage

        if (voltage != self.instanceState["voltage"]):
            previousState = copy.deepcopy(self.instanceState)

            self.instanceState["voltage"] = voltage
            self.instanceState["rate"] = self._computeRate(voltage)

            self.diffuse(previousState, self.instanceState)
