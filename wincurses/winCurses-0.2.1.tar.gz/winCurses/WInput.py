from threading import Thread
from time import sleep
from curses import *
from .Win import *


class WInput(Win, Thread):
    def __init__(self, *args, **kwargs):
        """ Creates an Input window, in which text can be entered and keypresses
        will be handled.
        In order to handle events, each Input will have its own process (so it
        have to be started with my_input.start() and can be stopped with
        my_input.terminate().

        It takes the same arguments as winCurses.Win.__init__, but can also take
        functions to handle events, that will overload existing Input methods
        (all this methods start with "on_"). This functions can be passed as
        kwarg values, with the method name for key. For instance :

            Input(..., on_return=lambda x:print(x))

        Optionnal arguments are :

        loop_delay -- (in seconds, defaut to 10ms) delay between checks for new
                      keypresses
        nodelay    -- (boolean, default True) indicates if the read is in
                      nodelay mode (which means a non-blocking read)
        password   -- If set to True, will display input content as stars
                      instead of the real input content
        """
        Thread.__init__(self, daemon=True)

        clean_kwargs = {}

        # Overload on_* methods
        for (k, v) in kwargs.items():
            if k.startswith('on') and k in self.__dir__():
                self.__setattr__(k, v)
            else:
                clean_kwargs[k] = v

        # Fixed height
        if 'dim' in clean_kwargs:
            clean_kwargs['dim'].y = 3
            clean_kwargs['dim'].relative_y = False
        else:
            args[2].y = 3
            args[2].relative_y = False

        self.loop_delay = clean_kwargs.pop("loop_delay", 0.05)
        self.nodelay    = clean_kwargs.pop("nodelay", True)
        self.password   = clean_kwargs.pop('password', False)

        Win.__init__(self, *args, **clean_kwargs)

        self.window.keypad(True)
        self.window.nodelay(self.nodelay)

        self.input_buff    = ""
        self.cursor_offset = 0
        self.buff_pos      = 0

    def run(self):
        """ The main loop executed in this process
        It will be ran when my_input.start() is called
        """
        def move_cursor(move):
            if 0 <= self.cursor_offset + move < self.line_length and self.cursor_offset + move <= len(self.input_buff):
                self.cursor_offset += move

        def add_char(char):
            self.input_buff = self.input_buff[:self.buff_pos] + char + self.input_buff[self.buff_pos:]
            self.buff_pos   += 1
            move_cursor(1)

        def rm_char(pos):
            if pos < len(self.input_buff):
                self.input_buff = self.input_buff[:pos] + self.input_buff[pos+1:]

        def reset_line():
            self.input_buff    = ""
            self.buff_pos      = 0
            self.cursor_offset = 0

        accent      = False
        escape_mode = False
        typing      = False

        while True:
            self.root._lock.acquire()
            ch = self.window.getch()
            self.root._lock.release()

            if ch < 0:
                sleep(self.loop_delay)
                continue
            # Special keys
            if ch == KEY_RESIZE:
                self.root.resize()
                self.root.refresh()
                continue
            elif ch == KEY_LEFT:
                self.buff_pos -= (1 if self.buff_pos > 0 else 0)
                move_cursor(-1)
            elif ch == KEY_RIGHT:
                self.buff_pos += (1 if self.buff_pos < len(self.input_buff) else 0)
                move_cursor(1)
            elif ch == KEY_DC:
                rm_char(self.buff_pos)
            # Accents & region-specific chars
            elif ch == 195:
                accent = True
                continue
            elif accent:
                add_char(chr(ch + 64))
                accent = False
            # Carriage return
            elif ch == 10:
                self.on_return(self.input_buff)
                reset_line()
            # Escape mode
            # Here for historical reasons
            # Maybe one day, it will be usefull (cf VI)
            elif ch == 27:
                escape_mode = not escape_mode
                continue
            # Erase whole line
            elif ch == 21:
                reset_line()
            # Normal alphabetical char
            elif 32 <= ch <= 126:
                add_char(chr(ch))
            # Backspace (special code or 127, or 8, in ASCII)
            elif ch == KEY_BACKSPACE or ch == 127 or ch == 8:
                if self.input_buff and self.buff_pos > 0:
                    rm_char(self.buff_pos - 1)
                    self.buff_pos -= 1
                    move_cursor(-1)
            elif 0 <= ch <= 31:
                if ch == 1:
                    self.buff_pos = self.cursor_offset = 0
                elif ch == 5:
                    self.buff_pos      = len(self.input_buff)
                    self.cursor_offset = (len(self.input_buff) if len(self.input_buff) < self.line_length else self.line_length - 1)
                else:
                    self.on_spec_key('CTRL_' + chr(64 + ch))
                    continue
            else:
                self.on_spec_key(ch)

            if bool(self.input_buff) != typing:
                typing = bool(self.input_buff)
                self.on_typing(typing)

            self.refresh()

    def refresh(self, update=True, get_root_lock=True):
        """ Refreshes the visual content of the input """
        self.clear()
        if len(self.input_buff) < self.line_length:
            line_offset = 0
        else:
            line_offset = self.buff_pos - self.cursor_offset

        display_text = self.input_buff[line_offset:line_offset + self.line_length - 1]
        if self.password:
            display_text = '*' * len(display_text)
        self.window.addstr(1, 1, display_text)
        self.window.move(1, self.cursor_offset + 1)
        Win.refresh(self, update, get_root_lock)

    def resize(self):
        Win.resize(self)
        if self.cursor_offset >= self.line_length:
            self.cursor_offset = self.line_length - 1

    def set_focus(self):
        """ Gives the focus to this windows
        All the event will be handled in the focused window
        There can be only one
        """
        self.root.focus = self

    def set_content(self, string, buff_pos=None):
        self.input_buff    = string
        self.buff_pos      = buff_pos or len(string)
        self.cursor_offset = (self.buff_pos if self.buff_pos < self.line_length else self.line_length - 1)

    def on_spec_key(self, key):
        """ Called when a special key is hit
        Can be overloaded

        key -- special key code
        """
        pass

    def on_return(self, buff):
        """ Called when <RETURN> is hit
        Can be overloaded

        buff -- content of the input buffer when return is pressed
        """
        pass

    def on_typing(self, boolean):
        """ Called when the input buff is written in or emptied

        boolean -- True if someone has started typing, False if the buffer has
                   just been emptied
        """
        pass

class KeyTypeError(Exception):
    def __init__(self, key_name, key_type):
        """ Creates a KeyTypeError exceptions, which describes an unknown or
        unhandled keys

        key_name -- the string/object describing the key
        key_type -- the type (should be str, but who knows...)
        """
        self.key_name = key_name
        self.key_type = key_type

    def __str__(self):
        return("Key %s %s cannot be handled" % (str(self.key_name), str(self.key_type)))
