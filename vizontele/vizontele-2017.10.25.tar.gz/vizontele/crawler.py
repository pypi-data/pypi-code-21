import vizontele
from .diziay import DiziayCrawler
from .dizibox import DiziboxCrawler
from .dizilab import DizilabCrawler
from .dizimag import DizimagCrawler
from .dizimek import DizimekCrawler
from .dizipub import DizipubCrawler
from .dizist import DizistCrawler
from .sezonlukdizi import SezonlukDiziCrawler
from ._720pizle import _720pizleCrawler

dizisites = {
    "dizilab": DizilabCrawler,
    "dizipub": DizipubCrawler,
    "sezonlukdizi": SezonlukDiziCrawler,
    "dizimag": DizimagCrawler,
    "dizibox": DiziboxCrawler,
    "diziay": DiziayCrawler,
    "dizist": DizistCrawler,
    "dizimek": DizimekCrawler,
}

moviesites = {
    "720pizle": _720pizleCrawler
}


class DiziCrawler:
    def __init__(self, site, dizi_url, season_number, episode_number):
        self.site = site
        if self.site in list(dizisites.keys()):
            self.dizicrawler = dizisites[self.site]()
        elif self.site == '':
            self.dizicrawler = None

        self.episode = {"dizi_url": vizontele.slugify(dizi_url),
                        "season": season_number,
                        "episode": episode_number}

    def get_sources(self):
        """
        Runs the crawler and returns the episode with found video and subtitle links
        :return: episode dict
        """
        if self.dizicrawler is not None:
            self.episode = self.dizicrawler.get_sources(self.episode)
        else:
            # Site is not specified, lets check them all
            for site in list(dizisites.keys()):
                self.dizicrawler = dizisites[site]()
                self.episode = self.dizicrawler.get_sources(self.episode)
                if 'video_links' in self.dizicrawler.episode and len(
                        self.dizicrawler.episode['video_links']) > 0:
                    break

        return self.episode


class MovieCrawler:
    def __init__(self, site, movie_url):
        self.site = site
        if self.site in list(moviesites.keys()):
            self.moviecrawler = moviesites[self.site]()
        elif self.site == '':
            self.moviecrawler = None

        self.movie = {"movie_url": vizontele.slugify(movie_url)}

    def get_sources(self):
        """
        Runs the crawler and returns the episode with found video and subtitle links
        :return: episode dict
        """
        if self.moviecrawler is not None:
            self.movie = self.moviecrawler.get_sources(self.movie)
        else:
            # Site is not specified, lets check them all
            for site in list(moviesites.keys()):
                self.moviecrawler = moviesites[site]()
                self.movie = self.moviecrawler.get_sources(self.movie)
                if 'video_links' in self.moviecrawler.movie and len(
                        self.moviecrawler.movie['video_links']) > 0:
                    break

        return self.movie