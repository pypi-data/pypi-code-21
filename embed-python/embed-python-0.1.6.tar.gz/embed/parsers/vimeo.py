import re
from . import generic
from ..regex import vimeo_duration, vimeo_id


class Parser(generic.Parser):

    def get_embed_id(self):
        embed_id = None
        if re.search(vimeo_id, self.url, flags=re.IGNORECASE):
            embed_id = re.search(vimeo_id, self.url, flags=re.IGNORECASE).group(1)

        return embed_id

    def embed_duration(self):
        duration = re.search(vimeo_duration, self.content).group(1)
        return int(duration)
