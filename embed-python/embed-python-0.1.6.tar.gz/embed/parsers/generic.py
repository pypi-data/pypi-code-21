import re
import html
from urllib.parse import urljoin
from itertools import zip_longest
from .. import regex
from ..url import Url


class Parser:
    fetch_method = 'request_advance'
    url = None
    content = None
    meta_dict = {}
    image_source = None
    image_folder_name = ['fileadmin']

    _body_images_with_extension_regex = regex.body_image_with_extension
    _body_images_without_extension_regex = regex.body_image_without_extension

    def __init__(self, url, content):
        self.url = url
        self.content = content
        self.meta_dict = self.parse_meta(content)

    def is_robot(self):
        return "robots" in self.meta_dict

    def get_title(self):
        title = ''

        if 'og:title' in self.meta_dict and html.unescape(self.meta_dict['og:title']) != "":
            title = self.meta_dict['og:title']
        elif 'twitter:title' in self.meta_dict and html.unescape(self.meta_dict['twitter:title']) != "":
            title = self.meta_dict['twitter:title']
        elif re.search(regex.title, self.content, flags=re.IGNORECASE):
            title = re.search(regex.title, self.content, flags=re.IGNORECASE).group(1)

        return html.unescape(html.unescape(title)).strip()

    def get_description(self):
        description = ''

        if 'og:description' in self.meta_dict and html.unescape(self.meta_dict['og:description']) != "":
            description = self.meta_dict['og:description']
        elif 'twitter:description' in self.meta_dict and html.unescape(self.meta_dict['twitter:description']) != "":
            description = self.meta_dict['twitter:description']
        elif 'description' in self.meta_dict and html.unescape(self.meta_dict['description']) != "":
            description = self.meta_dict['description']

        return html.unescape(html.unescape(description)).strip()

    def get_image(self):
        image = None

        if 'og:image' in self.meta_dict and html.unescape(self.meta_dict['og:image']) != "":
            image = self.fix_url(self.meta_dict['og:image']), 'og:image'
        if 'twitter:image' in self.meta_dict and html.unescape(self.meta_dict['twitter:image']) != "":
            image = self.fix_url(self.meta_dict['twitter:image']), 'twitter:image'
        if 'twitter:image:src' in self.meta_dict and html.unescape(self.meta_dict['twitter:image:src']) != "":
            image = self.fix_url(self.meta_dict['twitter:image:src']), 'twitter:image:src'

        return image

    def get_embed(self):
        try:
            if "twitter:player" in self.meta_dict and self.meta_dict["twitter:player"] != '""':
                embed_url = self.get_embed_url()
                embed_type = self.meta_dict["og:type"]
                embed_width = self.meta_dict["twitter:player:width"] if "twitter:player:width" in self.meta_dict else 640
                embed_height = self.meta_dict["twitter:player:height"] if "twitter:player:height" in self.meta_dict else 385
                embed_ratio = (round((float(embed_height) / float(embed_width)) * 100, 2))
                embed_code = '<iframe src="' + embed_url + '" frameborder="0" allowtransparency="true" width="' + \
                             str(embed_width) + '" height="' + str(embed_height) + '" allowfullscreen></iframe>'
                return {
                    "id": self.get_embed_id(),
                    "url": embed_url,
                    "type": embed_type,
                    'duration': self.embed_duration(),
                    "height": int(embed_height),
                    "width": int(embed_width),
                    "ratio": embed_ratio,
                    "html_code": embed_code
                }
        except KeyError:
            return None

    def get_embed_url(self):
        return self.meta_dict["twitter:player"]

    def get_author(self):
        author = {'name': None, 'url': None}

        if "author" in self.meta_dict:
            author['name'] = self.meta_dict["author"]
        elif "twitter:author" in self.meta_dict:
            author['name'] = self.meta_dict["twitter:author"]

        if "article:author" in self.meta_dict:
            author['url'] = self.meta_dict["article:author"]

        return author

    def get_body_images(self):
        body = re.search(regex.body, self.content, flags=re.IGNORECASE)
        image_urls = {'with_extension': [], 'without_extension': []}

        if body:
            image_matches = re.findall(self._body_images_with_extension_regex, body.group(1), flags=re.IGNORECASE)
            image_urls['with_extension'] = list(set(list(filter(None, [item for m in image_matches for item in m]))))
            image_urls['with_extension'] = [self.fix_url(url) for url in image_urls['with_extension']]

            image_matches = re.findall(self._body_images_without_extension_regex, body.group(1), flags=re.IGNORECASE)
            image_urls['without_extension'] = list(set(list(filter(None, [item for m in image_matches for item in m]))))
            image_urls['without_extension'] = [self.fix_url(url) for url in image_urls['without_extension']]

        return image_urls

    def get_meta_images(self, _except=[]):
        meta_images = []

        types = [
            'og:image',
            'twitter:image',
            'twitter:image:src'
        ]

        for _type in types:
            if _type in _except:
                continue

            if _type in self.meta_dict and html.unescape(self.meta_dict[_type]):
                meta_images.append(self.fix_url(self.meta_dict[_type]))

        return meta_images

    def is_meta_valid(self):
        if not self.get_title() and not self.get_description():
            return False

        if(self.get_title() or self.get_description()).startswith('{{'):
            return False

        return True

    def get_fetch_method(self):
        method = None
        redirect_url = None

        if self.is_meta_valid():
            method = self.fetch_method
        elif(self.get_title() or self.get_description()).startswith('{{') or 'robots' in self.meta_dict:
            method = 'selenium'
        else:
            meta_redirect = re.search(regex.meta_redirect_url, self.content, flags=re.IGNORECASE)
            js_redirect = re.search(regex.js_redirect_url, self.content, flags=re.IGNORECASE)

            if meta_redirect or js_redirect:
                if meta_redirect:
                    redirect_url = meta_redirect.group(1)
                    method = 'request_advance'
                elif js_redirect:
                    redirect_url = js_redirect.group(1)
                    method = 'request_advance'

        return method, redirect_url

    def get_embed_id(self):
        return None

    def embed_duration(self):
        return None

    @staticmethod
    def parse_meta(content):
        meta = re.findall(regex.meta, content, flags=re.IGNORECASE)
        temp = []

        for tup in meta:
            tup = tuple(filter(None, tup))
            temp.append(dict(zip_longest(*[iter(tup[:])] * 2, fillvalue="")))

        return {
            k.lower().strip(): v.strip().replace('""', '').replace("''", "") for d in temp for k, v in d.items()
        }

    def fix_url(self, url):
        if any(url.startswith(name) for name in self.image_folder_name):
            return html.unescape(Url(self.url, self.url).get_provider_url()+'/'+url)
        return html.unescape(urljoin(self.url, url))
