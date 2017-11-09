import datetime
import json
import os
import random
import urllib.request
from contextlib import ContextDecorator
from multiprocessing.pool import ThreadPool

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connections
from django.utils import lorem_ipsum
from django.utils.text import capfirst
from taggit.models import Tag
from wagtail.wagtailimages.models import Image

n = random.randint


def rbool(prob=0.5):
    return random.random() < prob


def lpar(num):
    """``num`` random paragraphs of lorem ipsum."""
    return ''.join('<p>{0}</p>'.format(p)
                   for p in lorem_ipsum.paragraphs(num, False))


def lwords(num):
    """``num`` random lorem ipsum words."""
    return capfirst(lorem_ipsum.words(num, False))


def tel():
    """ random international format (aus) telephone number eg. +61 (0) 412 345 678"""
    return '+{0} ({1}) {2} {3} {4}'.format(
        n(10, 99), n(0, 9), n(100, 999), n(100, 999), n(100, 999))


def rdate(future=True):
    """
    A random date. Set ``future`` to True for dates in the future, False for
    dates in the past. Possible dates span up to five years from today.
    """
    now = datetime.date.today()
    delta = datetime.timedelta(days=n(0, 1825))
    if future:
        return now + delta
    else:
        return now - delta


def r_heading(level, num):
    return '<h{0}>{1}</h{0}>'.format(level, lwords(num))


def r_bold(num):
    return '<p><b>{0}</b></p>'.format(lwords(num))


def r_italic(num):
    return '<p><i>{0}</i></p>'.format(lwords(num))


def r_ordered_list(list_elements):
    list_elems = []
    for i in range(list_elements):
        list_elems.append('<li>{0}</li>\n'.format(lwords(n(2, 4))))
    return '<ol>\n{0}</ol>'.format('\n'.join(map(str, list_elems)))


def r_unordered_list(list_elements):
    list_elems = []
    for i in range(list_elements):
        list_elems.append('<li>{0}</li>\n'.format(lwords(n(2, 4))))
    return '<ul>\n{0}</ul>'.format('\n'.join(map(str, list_elems)))


def hr():
    return '<hr>'


def r_anchor(num):
    return("<a href='http://example.com'>{0}</a>".format(lwords(num)))


def r_image():
    image = get_random_image()
    return('<embed alt="Example image" embedtype="image" format="fullwidth" id="{0}"/>'.format(image.id))


def embed_video():
    return '<embed embedtype="media" url="{0}"/>'.format(get_random_video_url())


def rich_text_example():
    """Layout all possible elements that can be used in rich text fields."""
    return open(os.path.join(os.path.dirname(__file__), 'rich_text_example.html'), 'r').read()


def random_rich_text_example(num, embeds=False):
    """
    Layout some possible elements that can be used in rich text fields in a random fashion
    Takes one argument, the number of elements. Set embeds=True if you wish to include images
    and videos
    """
    funcs = [
        lambda: r_heading(n(2, 5), n(1, 3)),
        lambda: r_bold(n(3, 5)),
        lambda: r_italic(n(3, 5)),
        lambda: r_ordered_list(n(3, 5)),
        lambda: r_unordered_list(n(3, 5)),
        lambda: r_anchor(n(3, 5)),
        lambda: lpar(n(3, 5)),
        hr,
    ]
    if embeds:
        funcs.extend([r_image, embed_video])
    return '\n'.join([random.choice(funcs)() for _ in range(num)])


def json_dumps(x):
    """Dump a value to JSON using the Django JSON encoder"""
    return json.dumps(x, cls=DjangoJSONEncoder)


def shuf(l):
    """Generate a shuffled copy of a list"""
    l2 = l[:]
    random.shuffle(l2)
    return l2


class once(object):
    """A decorator that only calls the decorated function once"""
    has_run = False
    value = None
    fn = None

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args, **kwargs):
        if self.has_run:
            return self.value

        self.value = self.fn(*args, **kwargs)
        self.has_run = True
        return self.value


flickr_api_key = 'f6b85533d3860015082acff890dce7cf'
flickr_endpoint = 'https://api.flickr.com/services/rest/'
flickr_photo_url = 'https://farm{farm}.staticflickr.com/{server}/{id}_{secret}_k.jpg'


def download_image_file(image_url, image_path):
    print("Downloading", image_url)
    image_stream = urllib.request.urlopen(image_url)
    tmp_path = image_path + '.part'
    with open(tmp_path, "wb") as out:
        out.write(image_stream.read())
    os.rename(tmp_path, image_path)


class close_db_connections(ContextDecorator):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc, exc_tb):
        connections.close_all()


@once
def download_random_images(image_categories=None):
    """Download a bunch of random images from the Flickr public API"""
    if image_categories is None:
        image_categories = [('cats', 10), ('dogs', 10), ('nature', 10),
                            ('pattern', 10), ('architecture', 10)]

    image_prefix = 'original_images/test-images'
    image_dirname = os.path.join(settings.MEDIA_ROOT, image_prefix)

    os.makedirs(image_dirname, exist_ok=True)

    @close_db_connections()
    def job(category, num, photo):
        filename = "{0}-{1}.jpg".format(category, num)
        image_path = os.path.join(image_dirname, filename)

        if not os.path.exists(image_path):
            response = requests.get(flickr_endpoint, params={
                'method': 'flickr.photos.getSizes',
                'api_key': flickr_api_key,
                'photo_id': photo['id'],
                'format': 'json', 'nojsoncallback': '1'})
            sizes = sorted(response.json()['sizes']['size'], reverse=True,
                           key=lambda p: int(p['width']) * int(p['height']))
            largest = sizes[0]
            image_url = largest['source']
            download_image_file(image_url, image_path)

        image = Image(
            title=photo['title'] or '{} {}'.format(category, num),
            file=ImageFile(open(image_path, 'rb'), name=filename))
        return (image, category)

    jobs = []
    for category, count in image_categories:
        json_path = os.path.join(image_dirname, '{}.json'.format(category))
        # Annoying race condition when implicitly creating tags by assigning
        # them to objects. Creating them straight up should sort that out.
        Tag.objects.get_or_create(name=category)
        if not os.path.exists(json_path):
            response = requests.get(flickr_endpoint, params={
                'method': 'flickr.photos.search',
                'api_key': flickr_api_key,
                'tags': category,
                'media': 'photos', 'per_page': count,
                'format': 'json', 'nojsoncallback': '1'})
            with open(json_path, 'w') as json_file:
                json_file.write(response.text)
            json_data = response.json()
        else:
            with open(json_path, 'r') as json_file:
                json_data = json.load(json_file)

        for num, photo in enumerate(json_data['photos']['photo']):
            jobs.append((category, num, photo))

    with ThreadPool(4) as pool:
        async_result = pool.starmap_async(job, jobs)
        pool.close()
        results = async_result.get(240)
        for image, category in results:
            image.save()
            image.tags.add(category)
        pool.join()
        pool.terminate()


def get_random_image(category=None):
    download_random_images()
    images = Image.objects.order_by('?')
    if category:
        images = images.filter(tags__name__in=[category])
    return images.first()


def get_random_video_url():
    return random.choice([
        'https://youtu.be/H9VVkwRb_7M',
        'https://youtu.be/2WWwkArWajM',
        'https://youtu.be/yYaJWO_mNWs',
        'https://youtu.be/1kThvYlo2Lc',
        'https://youtu.be/Ji9qSuQapFY',
        'https://vimeo.com/155536745',
        'https://vimeo.com/179936131',
        'https://vimeo.com/188197250',
        'https://vimeo.com/175535505',
        'https://vimeo.com/188321226'
    ])


def make_superuser():
    User.objects.create_superuser(username='admin', email='', password='p')
