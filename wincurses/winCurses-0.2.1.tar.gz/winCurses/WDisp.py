import curses
from .Win import *

class WDisp(Win):
    tags = {
            'b'  : curses.A_BOLD,
            'u'  : curses.A_UNDERLINE,
            'cw' : (convert_color, curses.COLOR_WHITE),
            'cm' : (convert_color, curses.COLOR_MAGENTA),
            'cb' : (convert_color, curses.COLOR_BLUE),
            'cc' : (convert_color, curses.COLOR_CYAN),
            'cr' : (convert_color, curses.COLOR_RED),
            'cg' : (convert_color, curses.COLOR_GREEN),
            'cy' : (convert_color, curses.COLOR_YELLOW),
            }

    def __init__(self, *args, **kwargs):
        """ Creates a Disp window, used to display scrollable tagged text, which
        have an history and some advanced abilities
        
        Arguments are the same as winCurses.Win ones
        """
        Win.__init__(self, *args, **kwargs)

        self.raw_hist    = []
        self.format_hist = []
        self.offset      = 0

    def resize(self):
        """ Called when the window needs the be resized """
        Win.resize(self)
        self.reload_history(False)

    def reload_history(self, update=True):
        self.format_hist = []
        for line in self.raw_hist:
            self.disp(line, False)
        self.refresh(update)

    def change_offset(self, mov, absolute=False):
        """ Modifies the offset

        mov      -- value to add/substract to the offset
        absolute -- if True, mov is not substracted to the offset, but can take
                    2 possible values :
                     *  0 : go to the first line
                     * -1 : go to the last (current) line; resets the offset
        """
        max_offset = len(self.format_hist) - self.max_lines
        max_offset = (max_offset if max_offset > 0 else 0)

        if absolute:
            if mov == 0:
                self.offset = max_offset
            elif mov == -1:
                self.offset = 0
        else:
            self.offset -= mov

        if self.offset < 0:
            self.offset = 0
        elif self.offset > max_offset:
            self.offset = max_offset

        self.refresh()

    def disp(self, txt, hist_save=True):
        """ Displays a line of tagged text

        txt       -- tagged text to display
        hist_save -- boolean, indicates if the line should be saved in history
                     (True), or if it is just a refresh and if it needs to be
                     ignored (False)

        Text in txt can be tagged using some primitive tagging system, in order
        for the user not to use the complicated curses attribute system

        Allowed tags are :
            <b>  bold
            <u>  underlined
            <c_> colored text. The '_' will be replaced by the first char in the
                 color name (lowercase). Allowed collors are White, Blue, Cyan,
                 Green, Yellow, Red, Magenta. Black isn't allowed, as the 
                 background is already black.
        """
        def save_buffs():
            attrs = 0
            for i in line_attrs:
                if type(i) == tuple:
                    i = i[0](*i[1:])
                attrs |= i
            self.format_hist[-1].append((beg_pos, line_buff, attrs), )

        line_buff   = ""
        attr_buff   = ""
        line_attrs  = set()
        beg_pos     = 0
        cur_pos     = 0
        escaped     = False
        in_tags     = False
        closing_tag = False

        self.format_hist.append([])

        if hist_save:
            self.raw_hist.append(txt)

        # Interprets the line : filling the buffer
        for c in txt:
            # End of line : save, reset and new line
            if cur_pos >= self.line_length:
                save_buffs()
                self.format_hist.append([])
                line_buff = ""
                cur_pos   = 0
                beg_pos   = 0
            # Escape char
            if not escaped and c == '\\':
                escaped = True
                continue
            # Begin of tag : save and reset
            elif not escaped and c == '<':
                in_tags = True
                save_buffs()
                line_buff = ""
                beg_pos = cur_pos
                continue
            # End of tag : change attrs, reset
            elif not escaped and c == '>':
                if attr_buff.lower() in self.tags:
                    attr = self.tags[attr_buff.lower()]
                    if not closing_tag:
                        line_attrs.add(attr)
                    elif attr in line_attrs:
                        line_attrs.remove(attr)
                in_tags     = False
                closing_tag = False
                attr_buff   = ""
                continue
            else:
                if in_tags:
                    if not attr_buff and c == '/':
                        closing_tag = True
                    else:
                        attr_buff += c
                    continue
                else:
                    line_buff += c
            
            # Resets escaped
            if escaped:
                escaped = False

            cur_pos += 1
        save_buffs()

        # Only refreshes display if no offset
        if self.offset:
            return

        if hist_save:
            self.refresh()
        
    def refresh(self, update=True, get_root_lock=True):
        """ Redraws the last "compiled" lines of content, to fill the window """
        self.clear()

        line = 1
        for i in range(-min(len(self.format_hist), self.max_lines) - self.offset, -self.offset):
            for (pos, txt, attrs) in self.format_hist[i]:
                self.window.addstr(line, pos + 1, txt, attrs)
            line += 1

        Win.refresh(self, update, get_root_lock)
