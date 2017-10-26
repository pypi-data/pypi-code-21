# -*- coding: utf-8 -*-
from . import generic


class Parser(generic.Parser):
    def get_embed_url(self):
        return self.meta_dict["twitter:player"].split('&')[0]
