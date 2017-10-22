import lifepo4weredPy


class WakeTimer():
    @property
    def wakeUp(self):
        return lifepo4weredPy.read(lifepo4weredPy.variablesEnum.WAKE_TIME)

    @wakeUp.setter
    def wakeUp(self, value):
        lifepo4weredPy.write(lifepo4weredPy.variablesEnum.WAKE_TIME, value)
