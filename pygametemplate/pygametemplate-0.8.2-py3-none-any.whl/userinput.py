from pygametemplate.button import Button


class Input(object):
    """
    Class for holding all variables and functions to do with receiving
    keyboard input from the user.
    """
    def __init__(self, game):
        self.game = game

        self.mouse_pos = (0, 0)
        self.buttons = {name: Button(self.game, number) for name, number in (
            ("default", 0),     # Any keys that only exist on select keyboards (e.g. volume/media buttons)
            # Mouse inputs
            ("leftmouse", 1), ("middlemouse", 2), ("rightmouse", 3),

            ("backspace", 8), ("tab", 9), ("enter", 13),
            ("pausebreak", 19), ("escape", 27),
            (" ", 32), ("'", 39), (",", 44), ("-", 45), (".", 46), ("/", 47),

            # Numbers across the top
            ("0", 48), ("1", 49), ("2", 50), ("3", 51), ("4", 52),
            ("5", 53), ("6", 54), ("7", 55), ("8", 56), ("9", 57),

            (";", 59), ("\\", 60), ("=", 61), ("[", 91),
            ("#", 92), ("]", 93), ("`", 96),

            # Alphabet keys
            ("a", 97), ("b", 98), ("c", 99), ("d", 100), ("e", 101),
            ("f", 102), ("g", 103), ("h", 104), ("i", 105), ("j", 106),
            ("k", 107), ("l", 108), ("m", 109), ("n", 110), ("o", 111),
            ("p", 112), ("q", 113), ("r", 114), ("s", 115), ("t", 116),
            ("u", 117), ("v", 118), ("w", 119), ("x", 120), ("y", 121), ("z", 122),

            ("delete", 127),

            # Numpad
            ("numpad0", 256), ("numpad1", 257), ("numpad2", 258),
            ("numpad3", 259), ("numpad4", 260), ("numpad5", 261),
            ("numpad6", 262), ("numpad7", 263), ("numpad8", 264),
            ("numpad9", 265), ("numpad.", 266), ("numpad/", 267),
            ("numpad*", 268), ("numpad-", 269), ("numpad+", 270),
            ("numpadenter", 271),

            # Arrow keys
            ("up", 273), ("down", 274), ("right", 275), ("left", 276),

            ("insert", 277), ("home", 278), ("end", 279),
            ("pageup", 280), ("pagedown", 281),

            # F keys
            ("f1", 282), ("f2", 283), ("f3", 284), ("f4", 285),
            ("f5", 286), ("f6", 287), ("f7", 288), ("f8", 289),
            ("f9", 290), ("f10", 291), ("f11", 292), ("f12", 293),

            # Key modifiers
            ("numlock", 300), ("capslock", 301), ("scrolllock", 302),
            ("rightshift", 303), ("leftshift", 304),
            ("rightctrl", 305), ("leftctrl", 306),
            ("altgr", 307), ("alt", 308),

            ("leftwindows", 311), ("rightwindows", 312), ("prntscr", 316), ("menu", 319)
        )}

    def reset(self):
        for button in self.buttons.values():
            button.reset()

    def buttondown(self, event):
        if hasattr(event, "key"):
            number = event.key
        else:
            number = event.button
        button = next((button for button in self.buttons.values() if button.number == number))
        button.press()
        button.event = event

    def buttonup(self, number):
        next((button for button in self.buttons.values() if button.number == number)).release()

    def mousein(self, x, y, width, height):
        """Determines if the mouse is in the given rectangle."""
        return (x < self.mouse_pos[0] < x + width and
                y < self.mouse_pos[1] < y + height)
