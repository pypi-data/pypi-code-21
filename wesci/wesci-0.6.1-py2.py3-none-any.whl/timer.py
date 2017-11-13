import time


class Duration(object):
    DURATION_DECIMAL_POINTS = 2

    def __init__(self):
        super(Duration, self).__init__()
        self.__duration = 0

    def get_ms(self):
        return self.__duration

    # duration converted to ms
    def set(self, duration):
        self.__duration = round(duration * 1000.0,
                                Duration.DURATION_DECIMAL_POINTS)


class Timer(object):
    def __init__(self):
        super(Timer, self).__init__()
        self.duration = Duration()
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.duration.set(time.time() - self.start_time)

    def duration_ms(self):
        return self.duration.get_ms()
