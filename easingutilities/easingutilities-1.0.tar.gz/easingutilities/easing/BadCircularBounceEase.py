from easingutilities.easing.AbstractEase import AbstractEase
from easingutilities.easing.BounceEaseOut import BounceEaseOut
from easingutilities.easing.LinearEase import LinearEase
from easingutilities.easing.SinusoidalEase import SinusoidalEase


# Demo of how to use the strategy pattern to mix easing strategies
# This is properly not the right way to do this so don't use this class...

class BadCircularBounceEase(AbstractEase):
    @classmethod
    def calculate_next_step(cls, current_step, start_value, change_in_value, number_of_steps):
        progress = LinearEase().calculate_next_step(current_step, start_value, change_in_value, number_of_steps)

        quintic = SinusoidalEase().calculate_next_step(current_step, start_value, change_in_value, number_of_steps)
        bounce = BounceEaseOut().calculate_next_step(current_step, start_value, change_in_value, number_of_steps)

        if progress > 0.2 and abs(quintic - bounce) < 0.1:  # This is very dangerous
            return bounce
        else:
            return quintic
