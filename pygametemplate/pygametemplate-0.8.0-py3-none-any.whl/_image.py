"""Module containing the Image class for easily adding/removing images from RAM."""
from pygametemplate import load_image


class Image:

    def __init__(self, image_file_name):
        self.file = image_file_name
        self.image = None

    def load(self):
        """Load the image into RAM."""
        self.image = load_image(self.file)

    def unload(self):
        """Unload the image from RAM."""
        self.image = None

    def display(self, surface, coordinates, area=None, special_flags=0):
        """Display the image on the given surface."""
        if self.image is None:
            self.load()
        surface.blit(self.image, coordinates, area, special_flags)
