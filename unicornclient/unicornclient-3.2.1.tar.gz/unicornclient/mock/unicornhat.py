import logging

AUTO = 'auto'

def set_layout(layout):
    logging.debug("set_layout " + str(layout))

def rotation(r): # pylint: disable=C0103
    logging.debug("rotation " + str(r))

def brightness(b): # pylint: disable=C0103
    logging.debug("brightness " + str(b))

def get_shape():
    return (4, 8)

def clear():
    logging.debug("clear")

def set_pixel(x, y, r, g, b): # pylint: disable=C0103
    logging.debug("set_pixel " + str((x, y, r, g, b)))

def show():
    logging.debug("show")
