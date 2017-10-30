import time

from pygametemplate import log


class Button(object):
    """Class representing keyboard keys."""
    def __init__(self, game, number):
        self.game = game
        try:
            self.number = number
            self.event = None   # The last event that caused the button press

            self.pressed = 0    # If the button was just pressed
            self.held = 0       # If the button is held
            self.released = 0   # If the button was just released
            self.press_time = 0.0
        except Exception:
            log("Failed to initialise button variable")

    def press(self):
        self.pressed = 1
        self.held = 1
        self.press_time = time.time()

    def release(self):
        self.held = 0
        self.released = 1

    def reset(self):
        try:
            self.pressed = 0
            self.released = 0
        except Exception:
            log("Failed to reset button")

    def time_held(self):
        try:
            if self.held:
                return time.time() - self.press_time
            else:
                return 0.0
        except Exception:
            log("Failed to get button held time")
