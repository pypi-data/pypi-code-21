# Stolen from: https://gist.github.com/th0ma5w/9883420

from easingutilities.easing.AbstractEase import AbstractEase


class LinearEase(AbstractEase):
    @classmethod
    def calculate_next_step(cls, current_step, start_value, change_in_value, number_of_steps):
        return (change_in_value * current_step / number_of_steps + start_value) - 1
