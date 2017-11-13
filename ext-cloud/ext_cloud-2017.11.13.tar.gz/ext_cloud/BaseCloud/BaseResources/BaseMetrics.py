class BaseMetricscls:

    def __init__(self, name, value, time=None):
        self.__name = name
        self.__value = value
        if time is None:
            import time
            self.__timestamp = int(time.time())
        else:
            self.__timestamp = time

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value

    @property
    def timestamp(self):
        return self.__timestamp
