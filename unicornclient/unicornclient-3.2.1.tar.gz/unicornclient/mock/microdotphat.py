import logging

def clear():
    logging.debug("clear")

def draw_tiny(display, text):
    logging.debug("draw_tiny " + str(display) + " " +str(text))

def fill(c): # pylint: disable=C0103
    logging.debug("fill " + str(c))

def scroll(amount_x=0, amount_y=0):
    logging.debug("scroll " + str(amount_x) + " " + str(amount_y))

def scroll_horizontal(amount=1):
    logging.debug("scroll_horizontal " + str(amount))

def scroll_to(position_x=0, position_y=0):
    logging.debug("scroll_to " + str(position_x) + " " + str(position_y))

def scroll_vertical(amount=1):
    logging.debug("scroll_vertical " + str(amount))

def set_brightness(brightness):
    logging.debug("set_brightness " + str(brightness))

def set_clear_on_exit(value):
    logging.debug("set_clear_on_exit " + str(value))

def set_col(x, col): # pylint: disable=C0103
    logging.debug("set_col " + str(x) + " " + str(col))

def set_decimal(index, state):
    logging.debug("set_decimal " + str(index) + " " + str(state))

def set_mirror(value):
    logging.debug("set_mirror " + str(value))

def set_pixel(x, y, c): # pylint: disable=C0103
    logging.debug("set_pixel " + str(x) + " " + str(y) + " " + str(c))

def set_rotate180(value):
    logging.debug("set_rotate180 " + str(value))

def show():
    logging.debug("show")

def write_char(char, offset_x=0, offset_y=0):
    logging.debug("write_char " + str(char) + " " + str(offset_x) + " " + str(offset_y))

def write_string(string, offset_x=0, offset_y=0, kerning=True):
    logging.debug("write_string " + str(string) + " " + str(offset_x) + " " + str(offset_y) + " " + str(kerning))
