#!/usr/bin/env python

from .utils import whatdoyoumean
from .downloader import Downloader
from .show import EZTVShow
from .database import Database
from .parser import process_countdown_page


class EZTVMan(object):

    BASE_URL = "https://eztv.ag"
    COUNTDOWN_REL_URL = "countdown/"

    def __init__(self):
        self._db = Database()
        self._dl = Downloader()

    def show(self, name):
        show_names = self._db.names
        if name not in show_names:
            whatdoyoumean(show_names, name)
            return None

        rel_link = [link for show, link in self._db.SHOWS if name == show]

        return EZTVShow(name, rel_link[0])

    def shows(self):
        return self._db.SHOWS

    def airing(self, when='today'):
        pass

    def countdown(self, name):
        show_names = self._db.names
        if name not in show_names:
            whatdoyoumean(show_names, name)
            return None

        countdown_url = "/".join([self.BASE_URL, self.COUNTDOWN_REL_URL])

        content = self._dl(countdown_url)
        if content:
            for show, date, countdown in process_countdown_page(content):
                if name == show:
                    return (date, countdown)

        print("{} is airing at this moment".format(name))
        return None
