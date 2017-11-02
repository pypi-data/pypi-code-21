import time


class Button(object):
    """Class representing keyboard keys."""
    def __init__(self, game, number):
        self.game = game

        self.number = number
        self.event = None   # The last event that caused the button press

        self.pressed = 0    # If the button was just pressed
        self.held = 0       # If the button is held
        self.released = 0   # If the button was just released
        self.press_time = 0.0

    def press(self):
        self.pressed = 1
        self.held = 1
        self.press_time = time.time()

    def release(self):
        self.held = 0
        self.released = 1

    def reset(self):
        self.pressed = 0
        self.released = 0

    def time_held(self) -> float:
        """Return the amount of time this button has been held for in seconds."""
        if not self.held:
            return 0.0
        return time.time() - self.press_time
