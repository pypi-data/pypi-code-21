from pygametemplate import log


class System(object):
    def __init__(self, game):
        self.game = game
        try:
            display_info = self.game.pygame.display.Info()
            self.MONITOR_WIDTH = display_info.current_w
            self.MONITOR_HEIGHT = display_info.current_h
        except Exception:
            log("Failed to initialise system object")
