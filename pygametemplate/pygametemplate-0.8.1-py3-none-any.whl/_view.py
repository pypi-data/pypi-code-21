"""Module containing the base View class."""
class View(object):

    def __init__(self, game):
        """Create an instance of this view. This loads the view's assets."""
        self.game = game
        self.load()

    def load(self):
        """Load all assets required by this view."""
        raise NotImplementedError

    def unload(self):
        """Unload all assets required by this view."""
        raise NotImplementedError

    def logic(self):
        """Perform logic for this view."""
        raise NotImplementedError

    def draw(self):
        """Draw all drawables for this view."""
        raise NotImplementedError
