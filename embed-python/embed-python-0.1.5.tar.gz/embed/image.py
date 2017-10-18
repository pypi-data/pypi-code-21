import requests
from magic import Magic
from io import BytesIO
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from PIL import Image as ImageObject
from math import floor

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


class ImageRequest:
    http = None
    url = None
    client = False
    error = None
    status_code = 200

    def __init__(self, url, **kwargs):
        self.url = url

        self.http = requests.Session()
        self.http.mount('http://', HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.5)))
        self.http.mount('https://', HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.5)))
        self.client = self.get_client(url, **kwargs)

    def get_content(self):
        if not self.client:
            return False

        return self.client.content

    def get_bytes_io(self):
        if not self.client:
            return False

        return BytesIO(self.get_content())

    def get_content_length(self):
        if not self.client:
            return False

        if 'content-length' in self.client.headers and self.client.headers['content-length']:
            return int(self.client.headers['content-length'])
        else:
            return len(self.get_content())

    def get_content_type(self):
        if not self.client:
            return False

        if 'content-type' in self.client.headers and self.client.headers['content-type']:
            return self.client.headers['content-type'].split(';')[0].lower()
        else:
            try:
                return Magic(mime=True).from_buffer(self.get_content()).lower()
            except:
                return None

    def get_client(self, url, **kwargs):
        response = None
        try:
            response = self.http.get(
                url,
                headers={
                    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36",
                    'Accept-Language': 'en-GB,en-US,en;q=0.8'
                },
                **kwargs
            )
        except requests.exceptions.SSLError as e:
            self.error = str(e)
        except requests.exceptions.RequestException as e:
            self.error = str(e)

        return response


class Image(ImageRequest):
    _allowed_types = [
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/gif',
        'image/webp',
        'image/tiff',
        'image/bmp',
        'text/plain',
        'jpg',
        'jpeg',
        'png',
        'gif',
        'webp',
        'tiff',
        'bmp',
        'image',
        'binary/octet-stream',
        'application/octet-stream',
    ]
    _is_valid = True
    _image = None
    _error = None
    resize_except = None
    width = None
    height = None
    ratio = None
    mime = None
    size = None
    extension = None

    def __init__(self, url, max_width=None, max_height=None, resize_except=None, **kwargs):
        super(Image, self).__init__(url, timeout=30)
        self.resize_except = resize_except

        if self.client and self.client.status_code == 200:
            if self.get_content_type().split(';')[0] in self._allowed_types:
                self._set_properties()

                if max_width:
                    self.resize(max_width, max_height)
            else:
                self._error = 'Image format "' + str(self.get_content_type()) + '" not supported'
                self._is_valid = False
        else:
            self._error = 'Not a valid image url'
            self._is_valid = False

    def _set_properties(self):
        try:
            self._image = ImageObject.open(self.get_bytes_io())
            self.width = self.get_image_object().size[0]
            self.height = self.get_image_object().size[1]
            self.ratio = self._ratio(self.get_image_object().size[0], self.get_image_object().size[1])
            self.mime = self.get_content_type()
            self.size = self.get_content_length()
            self.extension = self.mime_to_extension(self.mime)
        except OSError as e:
            self._is_valid = False
            print('OSError received while fetching image: ', self.url, e)

    def is_valid(self):
        return self._is_valid

    def get_image_object(self):
        return self._image

    def get_url(self):
        return self.url

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_ratio(self):
        return self.ratio

    def get_mime_type(self):
        return self.mime

    def get_size(self):
        return self.size

    def get_extension(self):
        return self.extension

    def get_properties(self, **kwargs):
        if self.is_valid():
            return {
                'url': self.get_url(),
                'width': self.get_width(),
                'height': self.get_height(),
                'ratio': self.get_ratio(),
                'mime_type': self.get_mime_type(),
                'size': self.get_size(),
                'extension': self.get_extension(),
                'mode': self.get_image_object().mode,
                'color': self.color(),
                **kwargs
            }

        return None

    def resize(self, width, height=None):
        if self.is_valid() and width < self.get_width() and \
                (self.resize_except is None or self.get_extension() not in self.resize_except):
            if not height:
                height = floor(self.get_height() * (width / self.get_width()))
            _tmp = BytesIO()
            new_image = self.get_image_object().resize((width, height))

            try:
                new_image.save(_tmp, self.get_extension())
            except KeyError as e:
                print('Received KeyError while resizing image:', "\n", str(e), "\n", 'Url:', self.url)
            except OSError as e:
                print('Received OSError while resizing image:', "\n", str(e), "\n", 'Url:', self.url)

            self.client._content = _tmp.getvalue()
            if 'content-length' in self.client.headers and self.client.headers['content-length']:
                self.client.headers['content-length'] = len(self.client._content)
            self._set_properties()

    def color(self):
        try:
            if self.is_valid():
                if self._image.mode == "RGB":
                    h = self._image.histogram()
                    return [
                        int(sum(i * w for i, w in enumerate(h[256 * x: 256 * (x + 1)])) / sum(h[256 * x: 256 * (x + 1)]))
                        for x
                        in range(3)]
                elif self._image.mode == "RGBA":
                    h = self._image.histogram()
                    result = [
                        int(sum(i * w for i, w in enumerate(h[256 * x: 256 * (x + 1)])) / sum(h[256 * x: 256 * (x + 1)]))
                        for x
                        in range(4)]
                    result[3] = round((result[3] / 255), 1)
                    return result

                elif self._image.mode == "P":
                    h = self._image.getpalette()
                    return [
                        int(sum(i * w for i, w in enumerate(h[256 * x: 256 * (x + 1)])) / (sum(h[256 * x: 256 * (x + 1)])
                        if (sum(h[256 * x: 256 * (x + 1)])) != 0 else 1)) for x
                        in range(3)]
        except Exception as e:
            print('Error received while extracting prominent color from image:', self.url, e)

    def error(self):
        return self._error

    @staticmethod
    def _ratio(width, height):
        return float('{0:.2f}'.format((height / width) * 100))

    @staticmethod
    def mime_to_extension(mime_type):
        extension = mime_type.split()[0].rstrip(";").split('/')[-1]
        extension = 'jpeg' if extension == 'jpg' else extension
        return extension
