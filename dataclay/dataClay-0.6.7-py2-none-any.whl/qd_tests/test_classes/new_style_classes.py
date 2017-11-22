from dataclay.managers.classes import DataClayObject, dclayMethod


class GenericObject(DataClayObject):
    """
    @dclayProperty propInt int
    @dclayProperty propFloat float
    @dclayProperty propBool bool
    """
    @dclayMethod(a=int, b=int, return_=int)
    def func(self, a, b):
        return a+b

    @dclayMethod(a='list<anything>', return_='anything')
    def do_max(self, a):
        import numpy as np
        return np.array([max(r) for r in a])

    @dclayMethod()
    def assign_props(self):
        self.propInt = 42
        self.propFloat = 4.2
        self.propBool = True

    @dclayMethod(return_='anything')
    def retrieve_props(self):
        print self.propInt
        print self.propFloat
        print self.propBool
        return self.propInt, self.propFloat, self.propBool

    @dclayMethod(propInt=int, propFloat=float, propBool=bool)
    def set_props(self, propInt, propFloat, propBool):
        self.propInt = propInt
        self.propFloat = propFloat
        self.propBool = propBool
