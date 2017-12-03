import pytweening
from easingutilities.easing.AbstractEase import AbstractEase
from easingutilities.easing.LinearEase import LinearEase


class CircularEaseOut(AbstractEase):

    @classmethod
    def calculate_next_step(self, current_step, start_value, change_in_value, number_of_steps):
        position = LinearEase.calculate_next_step(current_step, start_value, change_in_value, number_of_steps)
        return pytweening.easeOutCirc(position)
