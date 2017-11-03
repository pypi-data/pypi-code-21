#!/usr/bin/env python

from .parser import process_show_page, process_title
from .downloader import Downloader
from .exceptions import SeasonNotFound, EpisodeNotFound


class EZTVShow(object):

    BASE_URL = "https://eztv.ag"

    def __init__(self, name, link):
        self._dl = Downloader()
        self._name = name
        self._link = link
        self._show = {}

    def _build_url(self):
        bundle = [self.BASE_URL, self._link]
        return "/".join(bundle)

    @property
    def name(self):
        return self._name

    @property
    def link(self):
        return self._link

    def load_tv_show(self):
        url = self._build_url()
        content = self._dl(url)
        self._show['name'] = self._name

        for title, magnet, torrent, mirror in process_show_page(content):
            name, season, episode, quality = process_title(title)
            if season not in self._show.keys():
                self._show[season] = {}
            if episode not in self._show[season].keys():
                self._show[season][episode] = {}
            if quality not in self._show[season][episode].keys():
                self._show[season][episode][quality] = [magnet, torrent, mirror]

    def season(self, season):
        if not any(self._show):
            return self._show
        season = '{:02d}'.format(season)
        if season not in self._show.keys():
            raise SeasonNotFound("S{0} not found".format(season))

        return self._show[season]

    def seasons(self):
        return self._show

    def episode(self, episode, season, quality='480p'):
        if not any(self._show):
            return self._show
        episode = '{:02d}'.format(episode)
        season = '{:02d}'.format(season)
        if season not in self._show.keys():
            raise SeasonNotFound("Season {0} not found".format(season))
        if episode not in self._show[season].keys():
            raise EpisodeNotFound("E{0} S{1} not found".format(episode, season))

        return self._show[season][episode][quality]
