import pytweening
from easingutilities.easing.AbstractEase import AbstractEase
from easingutilities.easing.LinearEase import LinearEase


class BackEaseIn(AbstractEase):
    def __init__(self, factor=1.7):
        self.factor = factor

    def calculate_next_step(self, current_step, start_value, change_in_value, number_of_steps):
        position = LinearEase.calculate_next_step(current_step, start_value, change_in_value, number_of_steps)
        return pytweening.easeInBack(position, self.factor)
