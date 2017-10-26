####
# bomail.config.guiconfig
#
# User Interface configuration file.
####

import curses

import bomail.config.config as config

options_dict = config.options_dict


# --------------------------------------------------------------
# "Important" UI options from config file

threads_on = False
if "threads_on" in options_dict:
  threads_on = True

read_prog = options_dict["read_program"]
edit_prog = options_dict["edit_program"]

arrowkey_nav = False
if "arrowkey_navigation" in options_dict:
  arrowkey_nav = True

colorscheme = options_dict["colorscheme"]


# --------------------------------------------------------------
# "Other" UI options from config file

remove_newlines = options_dict["strip_newlines_in_msg_preview"]

lines_per_msg = int(options_dict["total_lines_per_msg"])
thread_lines_per_collapsed_msg = int(options_dict["threadview_total_lines_per_msg"])

datelen = int(options_dict["date_len"])
datepad = int(options_dict["date_pad"])
authorlen = int(options_dict["author_len"])
authorpad = int(options_dict["author_pad"])

horiz_line = False
if "hline_between_msgs" in options_dict:
  horiz_line = True

skip_line = False
if "skipline_between_msgs" in options_dict:
  skip_line = True

show_tags = False
if "show_tags" in options_dict:
  show_tags = True

inline_tags = False
if "tags_on_topline" in options_dict:
  inline_tags = True


# --------------------------------------------------------------
# Options for threads, i.e. "conversations"

# Right now "linear" is the only option (TODO: add "tree")
thread_view = "linear"


# --------------------------------------------------------------
# Tab view spacing and formatting

# Add extra blank lines if message uses fewer than lines_per_msg
# (True or False)
pad_msg_lines = True

# Format for displaying dates
# Y = year, m = month, d = day, a = day of week, H = hour, M = minute
datefmt = "%Y-%m-%d %a %H:%M"

# formatting for shortened stuff
short_authorlen = 16
short_subjectlen = 32


# --------------------------------------------------------------
# Thread view spacing and formatting
# (Same as above, but for viewing messages in a given thread.)

thread_pad_msg_lines = pad_msg_lines
thread_horiz_line = horiz_line
thread_skip_line = skip_line
thread_remove_newlines = remove_newlines
thread_show_tags = show_tags
thread_inline_tags = inline_tags

# --------------------------------------------------------------
# Color formatting.
# Color options are COLOR_BLACK, COLOR_RED, COLOR_GREEN, COLOR_YELLOW,
# COLOR_BLUE, COLOR_MAGENTA, COLOR_CYAN, and COLOR_WHITE.

# Choose builtin color profile light1, light2, dark1, dark2
# or define custom colors.

if colorscheme == "light1":
  background_color = curses.COLOR_WHITE
  author_color = curses.COLOR_BLACK
  bomail_color = curses.COLOR_RED
  foreground_color = curses.COLOR_CYAN
  tags_color = curses.COLOR_MAGENTA
  thread_color = curses.COLOR_MAGENTA

elif colorscheme == "light2":
  background_color = curses.COLOR_WHITE
  author_color = curses.COLOR_RED
  bomail_color = curses.COLOR_BLACK
  foreground_color = curses.COLOR_MAGENTA
  tags_color = curses.COLOR_CYAN
  thread_color = curses.COLOR_CYAN

elif colorscheme == "dark1":
  background_color = curses.COLOR_BLACK
  author_color = curses.COLOR_WHITE
  bomail_color = curses.COLOR_GREEN
  foreground_color = curses.COLOR_CYAN
  tags_color = curses.COLOR_YELLOW
  thread_color = curses.COLOR_MAGENTA

elif colorscheme == "dark2":
  background_color = curses.COLOR_BLACK
  author_color = curses.COLOR_GREEN
  bomail_color = curses.COLOR_WHITE
  foreground_color = curses.COLOR_MAGENTA
  tags_color = curses.COLOR_CYAN
  thread_color = curses.COLOR_CYAN

# Custom color profile
# To define, uncomment (delete initial '#') and choose colors
#background_color = curses.COLOR_BLACK
#author_color = curses.COLOR_GREEN
#bomail_color = curses.COLOR_WHITE
#foreground_color = curses.COLOR_MAGENTA
#tags_color = curses.COLOR_CYAN
#thread_color = curses.COLOR_CYAN

# all color profiles share these attribute settings
bomail_attr  = curses.A_BOLD
author_attr  = 0  # nothing special for authors, currently
cursor_attr = curses.A_STANDOUT
quote_attr  = curses.A_DIM


# --------------------------------------------------------------
# Key bindings

QUIT_KEY      = "q"

UP_KEY        = "k"
DOWN_KEY      = "j"
WAY_UP_KEY    = "K"
WAY_DOWN_KEY  = "J"
RIGHT_KEY     = "l"
LEFT_KEY      = "h"
WAY_RIGHT_KEY = "L"
WAY_LEFT_KEY  = "H"

if arrowkey_nav:
  UP_KEY        = "KEY_UP"
  DOWN_KEY      = "KEY_DOWN"
  WAY_UP_KEY    = "KEY_SUP"    # note curses and terminals don't actually support this!
  WAY_DOWN_KEY  = "KEY_SDOWN"  # or this!
  RIGHT_KEY     = "KEY_RIGHT"
  LEFT_KEY      = "KEY_LEFT"
  WAY_RIGHT_KEY = "KEY_SRIGHT"
  WAY_LEFT_KEY  = "KEY_SLEFT"


MARK_KEY      = "x"
MARK_ALL_KEY  = "X"

VIEW_KEY      = "v"
EDIT_DRAFT_KEY = "e"

OPEN_KEY      = "o"
SCHEDULE_KEY  = "s"
CLOSE_KEY     = "c"
TRASH_KEY     = "t"

GET_KEY       = "g"
WRITE_KEY     = "w"
SEND_KEY      = "S"

ADD_TAGS_KEY  = "a"
REMOVE_TAGS_KEY = "d"

UNDO_KEY      = "u"
REDO_KEY      = "r"

TAB_LEFT_KEY  = "["
TAB_RIGHT_KEY = "]"
EDIT_TAB_KEY  = "e"
ADD_TAB_KEY   = "+"
REMOVE_TAB_KEY = "-"
MOVE_TAB_LEFT_KEY = "{"
MOVE_TAB_RIGHT_KEY = "}"

# keys in thread window
THREAD_QUIT_KEY = "q"
THREAD_EXPAND_KEY = "L"
THREAD_COLLAPSE_KEY = "H"
THREAD_TOGGLE_MSG_KEY = "e"
THREAD_MSG_UP_KEY = "K"
THREAD_MSG_DOWN_KEY = "J"
THREAD_ALL_OPEN_KEY = "O"
THREAD_ALL_SCHEDULE_KEY  = "S"
THREAD_ALL_CLOSE_KEY     = "C"
THREAD_ALL_TRASH_KEY     = "T"
THREAD_ALL_ADD_TAGS_KEY  = "A"
THREAD_ALL_REMOVE_TAGS_KEY = "D"


# --------------------------------------------------------------
# Don't change these, they are constants for formatting code.

DEFAULT_CLR_PAIR = 1
BOMAIL_CLR_PAIR = 2
AUTHOR_CLR_PAIR = 3
AUTHOR_HIGHLIGHT_CLR_PAIR = 4
TAGS_CLR_PAIR = 5
THREAD_CLR_PAIR = 6

