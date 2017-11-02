class Hotkey(object):
    def __init__(self, game, button_name, ctrl=False, shift=False, alt=False):
        self.game = game
        self.button_name = button_name
        self.button = self.game.input.buttons[button_name]
        self.ctrl = ctrl
        self.shift = shift
        self.alt = alt

    def pressed(self):
        """Returns True if the hotkey was just pressed."""
        return self.button.pressed and self.modifiers_satisfied()

    def held(self):
        """Returns True if the hotkey is held."""
        return self.button.held and self.modifiers_satisfied()

    def released(self):
        """Returns True if the hotkey was just released."""
        return self.button.released and self.modifiers_satisfied()

    def modifiers_satisfied(self):
        return (self.ctrl_satisfied() and
                self.shift_satisfied() and
                self.alt_satisfied())

    def modifier_active(self, modifier_name):
        return (self.game.input.buttons[modifier_name].held and
                self.game.input.buttons[modifier_name].time_held() > self.button.time_held())

    def ctrl_satisfied(self):
        return self.ctrl == (self.modifier_active("leftctrl") or self.modifier_active("rightctrl"))

    def shift_satisfied(self):
        return self.shift == (self.modifier_active("leftshift") or self.modifier_active("rightshift"))

    def alt_satisfied(self):
        return self.alt == self.modifier_active("alt")
