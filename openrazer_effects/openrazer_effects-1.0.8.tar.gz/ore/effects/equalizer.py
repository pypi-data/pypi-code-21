from openrazer.client.devices.keyboard import RazerKeyboard
from ore.audio.capture import DeviceGraph
from ore.core.effects import KeyboardEffect
from ore.core.utils import find_keyboard, COLS, ROWS
from ore.registry.registry import register_effect


@register_effect
class Equalizer(KeyboardEffect):

    def get_name(self):
        return "Graphic Equalizer"

    def get_description(self):
        return "Green fire on midnight background, radiating from the middle."

    def get_cli_name(self):
        return "eq"

    def get_author(self):
        return "explodes"

    def __init__(self, audio_device="default", **kwargs):
        super().__init__(**kwargs)
        self.audio_device = audio_device
        self.keyboard = None
        self.graph = None

    def start(self):
        import pyaudio
        p = pyaudio.PyAudio()
        self.graph = DeviceGraph(p, self.audio_device, buckets=14)
        self.keyboard = find_keyboard()

        kb = self.keyboard
        self.init(kb)
        while True:
            kb.fx.advanced.matrix.reset()
            if not self.loop(self.keyboard):
                break
            kb.fx.advanced.draw()

    def init(self, kb: RazerKeyboard):
        kb.brightness = 100

    def loop(self, kb: RazerKeyboard):
        self.graph.read_row()
        values = self.graph.histogram.values[:11]

        matrix = kb.fx.advanced.matrix

        half = COLS // 2

        for col, p in enumerate(values):
            col = col * 2
            self.draw_column(matrix, col, p)
            self.draw_column(matrix, col+1, p)
            #self.draw_column(matrix, COLS - col - 1, p)

        return True

    def draw_column(self, matrix, col, p):
        limit = int((1 - p) * ROWS) - 1
        for row in range(ROWS - 1, limit, -1):
            color = self.color_for_volume(row, p)
            # print("m[{},{}] = {}".format(row, col, color))
            matrix[row, col] = color
        for row in range(limit, -1, -1):
            color = self.empty_color_for_volume(row, p)
            matrix[row, col] = color

    def color_for_volume(self, row, p):
        return (
            255 * (p ** 2),
            255 * (row / ROWS) * p,
            20 * (row / ROWS) * p,
        )

    def empty_color_for_volume(self, row, p):
        row = ROWS - row
        return (
            20 * (row / ROWS),
            64 * (p ** 2),
            128 * (row / ROWS),
        )


if __name__ == '__main__':
    effect = Equalizer("pulse")
    effect.start()
