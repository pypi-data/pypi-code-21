from pygametemplate.hotkey import Hotkey


class Console(object):

    def __init__(self, game, *, toggle_fps_hotkey=None):
        """Create a Console instance.

        `toggle_fps_hotkey` defaults to Ctrl+F.
        """
        self.game = game
        toggle_fps_hotkey = toggle_fps_hotkey or Hotkey(self.game, "f", ctrl=True)

        self.font = self.game.pygame.font.SysFont("consolas", 15)
        self.text_colour = (255, 255, 255)  # white

        self.show_fps = False
        self.fps_coordinates = (game.width - self.font.size("FPS: 000")[0], 0)

        self.hotkeys = {    # (hotkey condition, function)
            "toggle fps": (toggle_fps_hotkey.pressed, self.toggle_fps)
        }

    def logic(self):
        for condition, function in self.hotkeys.values():
            if condition():
                function()

    def draw(self):
        if self.show_fps:
            self.display_fps()

    def toggle_fps(self):
        self.show_fps = not self.show_fps

    def display_fps(self):
        fps_text = "FPS: {}".format(int(self.game.clock.get_fps()))
        fps_image = self.font.render(fps_text, True, self.text_colour)
        self.game.screen.blit(fps_image, self.fps_coordinates)
