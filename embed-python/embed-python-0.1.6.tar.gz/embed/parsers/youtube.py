import re
import isodate
from . import generic
from ..regex import youtube_id


class Parser(generic.Parser):

    def get_embed_id(self):
        embed_id = None
        if re.search(youtube_id, self.url, flags=re.IGNORECASE):
            embed_id = re.search(youtube_id, self.url, flags=re.IGNORECASE).group(1)
        return embed_id

    def embed_duration(self):
        if "duration" in self.meta_dict:
            return int(isodate.parse_duration(self.meta_dict["duration"]).total_seconds())
        else:
            return None
