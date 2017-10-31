"""Module containing the core functions of pygametemplate."""
import os
import sys
import traceback
from datetime import datetime
import ctypes

import pygame

from pygametemplate.exceptions import CaughtFatalException, PygameError


TEST = bool(int(os.environ.get("TEST", "0")))


PATH = os.getcwd()

def path_to(*path):
    """Return the complete absolute path of the path given."""
    return os.path.join(PATH, *"/".join(path).split("/"))


LOG_FILE = path_to("log.txt")

def log(*error_message, fatal=True):
    """Takes 1 or more variables and concatenates them to create the error message."""
    error_message = "".join(map(str, error_message))
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write("{} - {}.\n".format(datetime.utcnow(), error_message))
        log_file.write(traceback.format_exc() + "\n")

    if fatal:
        if TEST:
            raise   # pylint: disable=misplaced-bare-raise
        text = ("An error has occurred:\n\n    {}.\n\n\n"
                "Please check log.txt for details.").format(error_message)
        ctypes.windll.user32.MessageBoxW(0, text, "Error", 0)
        raise CaughtFatalException(sys.exc_info()[1])

    # TODO: Add some code here to show an error message in game


# Asset loading
def load_image(file_name, fix_alphas=True):
    """Load the image from the file with the given `file_name`.

    Setting `fix_alphas` to False allows the image to be able to fade.
    """
    # TODO: Add stuff for loading images of the correct resolution
    # depending on the player's resolution settings.
    image_path = path_to("assets/images", file_name)
    try:
        image = pygame.image.load(image_path)
    except PygameError:
        msg = "Image file not found: {}".format(file_name)
        raise FileNotFoundError(msg)

    if fix_alphas:
        return image.convert_alpha()  # Fixes per pixel alphas permanently
    return image.convert()


def load_font(font_name, font_size, file_extension=".ttf"):
    """Load the font with the given `font_name` with the given `font_size`."""
    font_path = path_to("assets/fonts", font_name + file_extension)
    try:
        return pygame.font.Font(font_path, font_size)
    except FileNotFoundError:
        msg = "Font file not found: {}{}".format(font_name, file_extension)
        raise FileNotFoundError(msg)
