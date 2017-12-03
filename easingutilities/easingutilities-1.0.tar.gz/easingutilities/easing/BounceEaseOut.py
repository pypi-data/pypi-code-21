import pytweening
from easingutilities.easing.LinearEase import LinearEase
from easingutilities.easing.AbstractEase import AbstractEase


class BounceEaseOut(AbstractEase):
    @classmethod
    def calculate_next_step(cls, current_step, start_value, change_in_value, number_of_steps):
        position = abs(current_step/number_of_steps)
        return pytweening.easeOutBounce(position)
