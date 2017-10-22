#!/usr/bin/python3
# -*- coding: utf-8 -*-

import copy
import lifepo4weredPy
from observablePy import Observable, observable_property
from .TouchStateEnum import touchStateEnum


class Touch(Observable):
    def __init__(self):
        super(Touch, self).__init__()
        self.instanceState = {
            "state": touchStateEnum.unknown,
        }

        self.addObservableElement("state")

    @property
    def state(self):
        return touchStateEnum(lifepo4weredPy.read(
                               lifepo4weredPy.variablesEnum.TOUCH_STATE))

    def _diffuseChanges(self):
        state = self.state

        if (state != self.instanceState["state"]):
            previousState = copy.deepcopy(self.instanceState)

            self.instanceState["state"] = state

            self.diffuse(previousState, self.instanceState)
