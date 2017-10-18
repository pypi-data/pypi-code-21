import io
import json

from .json_encoder import Frozen, PrettyJSONEncoder


class PixelsInfo(object):
    def __init__(self, indexes_to_colors, pixel_indexes):
        self.indexes_to_colors = indexes_to_colors
        self.pixel_indexes = pixel_indexes

    def to_json(self, pretty: bool = False):
        colors_info_json = dict([(k, str(v)) for (k, v) in self.indexes_to_colors.items()])
        pixel_map = [Frozen(row) for row in self.pixel_indexes] if pretty else self.pixel_indexes
        return {
            "palette": colors_info_json,
            "pixel_map": pixel_map
        }

    def write_pixels_info(self, file: str, pretty: bool):
        with io.open(file, 'w', encoding='utf8') as file:
            if pretty:
                json_str = json.dumps(self.to_json(True), indent=4, cls=PrettyJSONEncoder)
            else:
                json_str = json.dumps(self.to_json(), separators=(',', ':'))

            file.write(json_str)
