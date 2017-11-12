import fnmatch
import re
import logging

from typing import Union
from collections import Iterable
from pygtrie import PrefixSet
from urllib.parse import urlparse, ParseResult
from bs4 import BeautifulSoup

from cobweb.link_extractor.bloom_filter import BloomFilter


class LinkExtractor:

    REGEX_UNIX = "unix"
    REGEX_REGULAR = "regular"

    PROBABILISTIC = "probabilistic"
    TRIE = "trie"
    HASH = "hash"

    def __init__(
            self,
            follow: Union[Iterable, str] = ("*",),
            exclude: Union[Iterable, str] = tuple(),
            regex_type=REGEX_UNIX,
            mode=HASH,
            domain_only=True
    ):

        self._current_page_url = None
        self._follow_patterns = None
        self._exclude_patterns = None

        self.domain_only = domain_only
        self.allowed_schemes = {
            "http",
            "https",
        }

        self.regex_type = regex_type
        self.follow_patterns = follow
        self.exclude_patterns = exclude

        self.mode = mode
        # Any object with both '__contains__' and 'add' methods defined can be used here
        if mode == LinkExtractor.PROBABILISTIC:
            self.seen = BloomFilter()
        elif mode == LinkExtractor.HASH:
            self.seen = set()
        elif mode == LinkExtractor.TRIE:
            self.seen = PrefixSet()

    @property
    def logger(self):
        return logging.getLogger("cobweb.link_extractor")

    @property
    def current_page_url(self):
        return self._current_page_url

    @current_page_url.setter
    def current_page_url(self, value: str):
        self._current_page_url = urlparse(value)

    @property
    def follow_patterns(self):
        return self._follow_patterns

    @follow_patterns.setter
    def follow_patterns(self, value):
        follow_patterns = value if not isinstance(value, str) else [value]
        self._follow_patterns = [
            self.get_regex(pattern)
            for pattern in follow_patterns
        ]

    @property
    def exclude_patterns(self):
        return self._exclude_patterns

    @exclude_patterns.setter
    def exclude_patterns(self, value):
        exclude_patterns = value if not isinstance(value, str) else [value]
        self.exclude_patterns = [
            self.get_regex(pattern)
            for pattern in exclude_patterns
        ]

    def get_regex(self, string: str):
        return re.compile(fnmatch.translate(string)) if self.regex_type == self.REGEX_UNIX else re.compile(string)

    def is_valid_domain(self, href: str) -> bool:
        """
        checks whether the given string satisfy the 'domain_only' setting
        :param href: str
        :return: bool
        """
        parsed = urlparse(href)
        if parsed.scheme and parsed.scheme not in self.allowed_schemes:
            return False
        if self.domain_only:
            return not parsed.netloc or parsed.netloc == self.current_page_url.netloc
        else:
            return parsed.scheme and parsed.netloc

    def match_follow_patterns(self, link):
        return any([
                pattern.match(link)
                for pattern in self.follow_patterns
        ])

    def match_exclude_patterns(self, link):
        return any([
            pattern.match(link)
            for pattern in self.exclude_patterns
        ])

    def is_satisfying_link(self, link: str) -> bool:
        """
        checks whether the given link satisfy 'follow' and 'exclude' preferences
        :param link: str
        :return: bool
        """
        return self.match_follow_patterns(link) and not self.match_exclude_patterns(link)

    def get_full_url(self, href: ParseResult):
        if not href.scheme:
            href = href._replace(scheme=self.current_page_url.scheme)
        if not href.netloc:
            href = href._replace(netloc=self.current_page_url.netloc)
        if href.path.startswith("./"):
            href = href._replace(path=href.path[2:])
        return href.geturl()

    def filter_valid_links(self, all_links: set):
        valid_links = set()
        for link in all_links:
            if link.has_attr("href") and self.is_valid_domain(link["href"]):
                url = self.get_full_url(urlparse(link["href"]))
                if self.is_satisfying_link(url):
                    valid_links.add(url)
                    self.seen.add(url)
        self.logger.debug("valid links count: %s", len(valid_links))
        if self.mode == self.PROBABILISTIC:
            self.logger.info("current error probability %s", self.seen.count_error_probability())
        return valid_links

    def extract(self, response):
        self.current_page_url = response.url
        data = BeautifulSoup(response.content, "html.parser")
        all_links = data.find_all("a")
        self.logger.debug("found %s new links", len(all_links))
        return self.filter_valid_links(all_links)
