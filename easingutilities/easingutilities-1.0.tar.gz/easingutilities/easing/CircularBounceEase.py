from easingutilities.easing.AbstractEase import AbstractEase
from easingutilities.easing.BounceEaseOut import BounceEaseOut
from easingutilities.easing.CircularEaseIn import CircularEaseIn
from easingutilities.easing.LinearEase import LinearEase


class CircularBounceEase(AbstractEase):

    # Shows how two easing strategies can be combined
    # Much better approach than BadCircularBounceEase
    @classmethod
    def calculate_next_step(self, current_step, start_value, change_in_value, number_of_steps):
        half = number_of_steps/2
        tenth = number_of_steps/10
        if current_step < half:
            return CircularEaseIn.calculate_next_step(current_step, start_value, change_in_value, half) / 2
        else:
            return (BounceEaseOut.calculate_next_step(current_step - half, 1, change_in_value, half) / 2) + 0.5

