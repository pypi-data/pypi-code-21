from collections import deque

from pygametemplate.helper import load_class_assets
from pygametemplate.hotkey import Hotkey


class TextInput(object):
    class_assets_loaded = False
    instances = []
    active = False

    def __init__(self, game):
        if not self.class_assets_loaded:
            self.load_class_assets(game)

        self.focused = True
        self.accepting_text = False     # Showing whether text is currently being accepted
        self.text = ""              # The input text from the user
        self.max_characters = 0     # The maximum amount of allowed characters in an input text
        self.inputs = deque()   # Double-ended queue (deque) of inputs. Most recent at index 0.
        # Deques are slower to create than lists and use more memory, but are faster to prepend to.

        # Blinking cursor positioning
        self.cursor_position = 0    # 0 means at the start of self.text
        self.cursor_moved_recently = False
        self.cursor_last_moved_frame = 0     # The last frame at which the cursor was moved
        self.move_left_hotkey = Hotkey(self.game, "left")
        self.move_right_hotkey = Hotkey(self.game, "right")
        self.home_hotkey = Hotkey(self.game, "home")
        self.end_hotkey = Hotkey(self.game, "end")

        self.instances.append(self)

    def load_class_assets(self, game):
        load_class_assets(self, {"game": game})

    def destroy(self):
        self.instances.remove(self)

    def enable(self, max_characters):
        """Enables text input to be taken from the user."""
        # Maybe turn this into a function which creates a text field
        # at given coordinates or something
        self.text = ""
        self.max_characters = max_characters
        if self.active:
            for instance in self.instances:
                instance.accepting_text = False
                instance.focused = False
        else:
            setattr(TextInput, "active", True)
        self.accepting_text = True
        self.focused = True

    def disable(self, submit=True):
        """Disables text input from being taken from the user."""
        self.accepting_text = False
        self.focused = False
        self.cursor_position = 0
        if submit:
            self.inputs.appendleft(self.text)
        setattr(TextInput, "active", False)

    def display(self, font, colour, coordinates, antialias=True, background=None):
        if background is None:
            self.game.screen.blit(font.render(self.text, antialias, colour),
                                  coordinates)
        else:
            self.game.screen.blit(font.render(self.text, antialias, colour, background),
                                  coordinates)

        # Blinking cursor at end of text when text field is focused
        self.update_cursor_moved_recently()
        if (self.focused and
                (self.cursor_moved_recently or
                 self.game.frame % self.game.fps < self.game.fps/2)):
            # Above condition means 0.5s displaying, 0.5s not displaying
            self.game.screen.blit(
                font.render("|", True, colour),
                (coordinates[0]
                 + font.size(self.text[:self.cursor_position])[0]
                 - font.size(" ")[0]/2,     # Fixes cursor showing too far away from text
                 coordinates[1])
            )

    def check_focused(self, x, y, width, height):
        """
        Checks if the mouse was clicked in the described rectangle,
        which determines whether the text input text is focused
        """
        if self.game.input.buttons["leftmouse"].pressed:
            if self.game.input.mousein(x, y, width, height):
                self.focused = True
                setattr(TextInput, "active", True)
            else:
                self.focused = False
                setattr(TextInput, "active", False)

    def most_recent(self):
        """Returns the most recent input."""
        return self.inputs[0]

    def insert_character(self, character):
        self.text = (self.text[:self.cursor_position]
                     + character
                     + self.text[self.cursor_position:])
        self.set_cursor_position(self.cursor_position + 1)

    def delete_character(self, positioning):
        """
        Deletes a character next to the blinking cursor.
        `positioning` must be one of "previous" and "following"
        """
        if self.text:
            if positioning == "previous":
                if self.cursor_position != 0:
                    self.text = self.text[:self.cursor_position-1] + self.text[self.cursor_position:]
                    self.set_cursor_position(self.cursor_position - 1)
            elif positioning == "following":
                if self.cursor_position != len(self.text):
                    self.text = self.text[:self.cursor_position] + self.text[self.cursor_position+1:]
                    self.indicate_cursor_moved_recently()   # Deleting should also force the cursor to display
            else:
                raise ValueError("The `positioning` argument of TextInput.delete_character() "
                                 "must be either \"previous\" or \"following\".")

    def update_with(self, text="", previous_input_index=None):
        """
        Updates `self.text` to the given value.
        Uses a previous input if index is given.
        """
        if previous_input_index is None:
            self.text = text
        else:
            self.text = self.inputs[previous_input_index]
        self.cursor_position = len(self.text)   # Move cursor to end of line

    def set_cursor_position(self, cursor_position):
        self.cursor_position = cursor_position
        self.indicate_cursor_moved_recently()

    def indicate_cursor_moved_recently(self):
        self.cursor_moved_recently = True
        self.cursor_last_moved_frame = self.game.frame

    def update_cursor_moved_recently(self):
        if (self.cursor_moved_recently and
                self.game.frame - self.cursor_last_moved_frame > self.game.fps/2):
            self.cursor_moved_recently = False

    @classmethod
    def active_instance(self):
        """Returns the instance that is currently accepting text."""
        return next((instance for instance in self.instances
                     if instance.accepting_text and instance.focused))

    @classmethod
    def receive_single_characters(self, event):
        if self.active:
            active_instance = self.active_instance()
            if not (active_instance.game.input.buttons["leftctrl"].held or
                    active_instance.game.input.buttons["rightctrl"].held or
                    active_instance.game.input.buttons["alt"].held):
                if event.key == 8:  # Backspace
                    active_instance.delete_character("previous")
                elif event.key == 127:  # Delete
                    active_instance.delete_character("following")
                elif event.key in [13, 271]:    # Enter and numpad enter
                    active_instance.disable()
                # Moving blinking cursor
                elif event.key == 275:  # Right arrow key
                    if active_instance.cursor_position != len(active_instance.text):
                        active_instance.set_cursor_position(active_instance.cursor_position + 1)
                elif event.key == 276:  # Left arrow key
                    if active_instance.cursor_position != 0:
                        active_instance.set_cursor_position(active_instance.cursor_position - 1)
                elif event.key == 278:  # Home key
                    active_instance.set_cursor_position(0)
                elif event.key == 279:  # End key
                    active_instance.set_cursor_position(len(active_instance.text))
                # Inserting new characters
                elif len(active_instance.text) < active_instance.max_characters:
                    active_instance.insert_character(event.unicode)

    character_keys = (  # Keys that alter the appearance of self.text when it is displayed
        [n for n in range(44, 58)]
        + [n for n in range(96, 123)]
        + [n for n in range(256, 272)]
        + [8, 127, 39, 59, 60, 61, 91, 92, 93, 275, 276]
    )

    @classmethod
    def receive_multiple_characters(self):
        if self.active:
            if self.is_a_repeat_frame() and self.character_keys_held() == 1:
                button = next((button for button in self.game.input.buttons.values()
                               if button.held and button.number in self.character_keys))
                if button.time_held() > 0.5:
                    self.receive_single_characters(button.event)

    @classmethod
    def character_keys_held(self):
        def return_key(n):
            return self.keys[n]
        self.keys = self.game.pygame.key.get_pressed()
        return sum(map(return_key, self.character_keys))

    @classmethod
    def is_a_repeat_frame(self):
        """
        This code means that characters are written/deleted [actions_per_second]
        times per second when their key is held down. This is also the rate at
        which the blinking cursor moves when an arrow key is held down.
        """
        actions_per_second = 30     # Feels natural
        return self.game.frame % (self.game.fps/actions_per_second) == 0
