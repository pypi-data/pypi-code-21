import math

from easingutilities.easing.LinearEase import LinearEase
from easingutilities.easing.AbstractEase import AbstractEase


# Ported from: https://github.com/warrenm/AHEasing/tree/master/AHEasing

class BounceEase(AbstractEase):

    @classmethod
    def calculate_next_step(cls, current_step, start_value, change_in_value, number_of_steps):
        position = LinearEase.calculate_next_step(current_step, start_value, change_in_value, number_of_steps)
        return cls.bounce_ease_in_out(position)

    @classmethod
    def bounce_ease_in_out(cls, p):
        if p < 0.5:
            return 0.5 * cls.bounce_ease_in(p * 2)
        else:
            return 0.5 * cls.bounce_ease_out(p * 2 - 1) + 0.5

    @classmethod
    def bounce_ease_in(cls, p):
        return 1 - cls.bounce_ease_out(1 - p)

    @classmethod
    def bounce_ease_out(cls, p):
        if p < 4 / 11.0:
            return (121 * p * p) / 16.0
        elif p < 8 / 11.0:
            return (363 / 40.0 * p * p) - (99 / 10.0 * p) + 17 / 5.0
        elif p < 9 / 10.0:
            return (4356 / 361.0 * p * p) - (35442 / 1805.0 * p) + 16061 / 1805.0
        else:
            return (54 / 5.0 * p * p) - (513 / 25.0 * p) + 268 / 25.0
