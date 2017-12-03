import math

from easingutilities.easing.AbstractEase import AbstractEase


class SinusoidalEase(AbstractEase):
    @classmethod
    def calculate_next_step(self, current_step, start_value, change_in_value, number_of_steps):
        return self.ease(current_step, start_value, change_in_value, number_of_steps) - 1

    # Stolen from: https://gist.github.com/th0ma5w/9883420
    @classmethod
    def ease(cls, current_time, start_value, change_in_value, duration):
        return -change_in_value / 2 * (math.cos(math.pi * current_time / duration) - 1) + start_value
