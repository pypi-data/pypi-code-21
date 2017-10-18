import time
from . import utils
from . import parsers
from .url import Url
from .request import Request
from .image import Image
from .thread import async_process
from .exceptions import EmbedException
from .configs import get_request_method
from urllib.parse import urljoin


class Embed:
    _last_fetched_url = None
    _last_fetched_method = None
    _parser_class = None
    _entered_url = None
    _parsed = None
    _timings = {
        'fetch_time': None,
        'image_time': None,
        'total_time': None
    }
    
    url = None
    image = None

    def __init__(self, url):
        start_time = time.time()
        self._entered_url = url
        self.validate_headers()
        self.fetch_content(get_request_method(self.url.get_provider(), self._parser_class.Parser.fetch_method))
        self._timings['total_time'] = time.time() - start_time

    def validate_headers(self):
        response = Request(self.url.origin_url if self.url is not None else self._entered_url).get_headers()

        if response and response.get_content_type() and not response.is_content_type_valid():
            raise EmbedException(
                response.status_code,
                "Content type is not supported" if response.status_code == 200 else response.message
            )

        if response:
            self.parse_url(response.url)
        else:
            self.parse_url(self.url.origin_url if self.url is not None else self._entered_url)

    def fetch_content(self, method):
        fetch_method = None
        start_time = time.time()

        if self._last_fetched_url != self.url.origin_url:
            self.validate_headers()
            fetch_method = get_request_method(self.url.get_provider())

        if fetch_method is not None:
            method = fetch_method

        self._last_fetched_url = self.url.get_origin_url()
        response = getattr(Request(self.url.origin_url), method)()
        self.parse_url(response.url)

        if response and (self._last_fetched_method is None or self._last_fetched_method != 'selenium'):
            self._last_fetched_method = method
            self._parsed = self._parser_class.Parser(self.url.get_origin_url(), response.content)

            if not self._parsed.is_meta_valid():
                fetch = self._parsed.get_fetch_method()

                if not fetch[0] and not fetch[1]:
                    raise EmbedException(400, "Invalid url")

                if fetch[1]:
                    self.url.origin_url = urljoin(self.url.origin_url, fetch[1].strip("\'"))
                    # self.parse_url(fetch[1])

                if fetch[0]:
                    self.fetch_content(fetch[0])

            self._timings['fetch_time'] = time.time() - start_time
            self.process_images()

        if not self._parsed or not self._parsed.is_meta_valid():
            if response:
                raise EmbedException(400, 'Bad request')
            else:
                raise EmbedException(response.status_code, response.message)

    def parse_url(self, url):
        self.url = Url(self._entered_url, origin_url=url)

        if not self.url.is_valid():
            raise EmbedException(400, 'Url is not valid')

        self._parser_class = parsers.get_parser(self.url.get_provider_name())

    def process_images(self):
        start_time = time.time()
        best_image = self._parsed.get_image()

        if best_image:
            self.image = Image(best_image[0])

        if not self.image or not self.image.is_valid():
            meta_images = self._parsed.get_meta_images([best_image[1]] if best_image else [])
            self.process_other_images(meta_images)

        if not self.image or not self.image.is_valid():
            body_images = self._parsed.get_body_images()

            if body_images['with_extension']:
                self.process_other_images(body_images['with_extension'])

            if not self.image or not self.image.is_valid() and body_images['without_extension']:
                self.process_other_images(body_images['without_extension'])

        if self.image and not self.image.is_valid():
            self.image = None

        self._timings['image_time'] = time.time() - start_time

    def process_other_images(self, other_images, chunks_of=4):
        if other_images:
            chunks = utils.to_chunks(other_images, chunks_of)

            for chunk in chunks:
                images = async_process(chunk, Image, workers=4)
                self.image = self.find_best_image(images)

                if self.image and self.image.is_valid():
                    break

    @staticmethod
    def find_best_image(images):
        best_image = None
        best_height = best_width = 200

        for img in images:
            if img.is_valid() and img.get_width() > best_width and img.get_height() > best_height:
                best_image = img
                best_height = img.get_height()
                best_width = img.get_width()

        return best_image

    @property
    def title(self):
        return self._parsed.get_title()

    @property
    def description(self):
        return self._parsed.get_description()

    @property
    def embed(self):
        return self._parsed.get_embed()

    @property
    def author(self):
        return self._parsed.get_author()

    @property
    def time_taken(self):
        return self._timings['total_time']

    @property
    def timings(self):
        return self._timings

    @property
    def properties(self):
        return {
            'url': self.url.get_properties(),
            'title': self.title,
            'description': self.description,
            'image': self.image.get_properties() if self.image else None,
            'embed': self.embed,
            'author': self.author,
            'time_taken': self.time_taken
        }
