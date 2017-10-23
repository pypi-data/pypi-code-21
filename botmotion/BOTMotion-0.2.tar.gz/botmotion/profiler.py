import math


class Position_Profiler():
    def __init__(self, current_pos):
        self.__tick_inc = 10
        self.__max_pos = 4000
        self.__min_pos = 2100
        self.__current_pos = current_pos

    def next_pos(self):
        if self.__current_pos >= self.__max_pos:
            self.__tick_inc = -1*abs(self.__tick_inc)
        elif self.__current_pos <= self.__min_pos:
            self.__tick_inc = abs(self.__tick_inc)

        self.__current_pos += self.__tick_inc
        return self.__current_pos

class Velocity_Profiler():
    def __init__(self, max_velocity, min_velocity, rpm_inc):
        self.__rpm_inc = rpm_inc
        self.__max_velocity = max_velocity
        self.__min_velocity = min_velocity
        self.__current_velocity = 0
        self.__counter = 0

    def ramp_next_velocity(self):
        if self.__current_velocity > self.__max_velocity:
            self.__rpm_inc = -1*abs(self.__rpm_inc)
        elif self.__current_velocity < self.__min_velocity:
            self.__rpm_inc = abs(self.__rpm_inc)

        self.__current_velocity += self.__rpm_inc
        return self.__current_velocity

    def sinus_next_velocity(self):
        if self.__current_velocity >= 2*math.pi:
            self.__current_velocity = 0
        self.__current_velocity += self.__rpm_inc
        return math.sin(self.__current_velocity)*self.__max_velocity




