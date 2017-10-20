import os
import argparse
import requests
import tempfile
import subprocess

from lxml import html

signs = [
    'belier',
    'taureau',
    'gemeaux',
    'cancer',
    'lion',
    'vierge',
    'balance',
    'scorpion',
    'sagittaire',
    'capricorne',
    'verseau',
    'poissons',
]

parser = argparse.ArgumentParser()
parser.add_argument('sign', help="Astrological sign (in french)", choices=signs)


class Horoscoop(object):

    URL = "https://www.horoscope.fr/horoscopes/horoscope_{sign}.html"

    def __init__(self, sign, tts_lang='fr-FR'):
        self.sign = sign
        self.tts_lang = tts_lang

    def _build_url(self):
        """
        Builds and returns the complete URL for the astological sign
        """
        return self.URL.format(sign=self.sign)

    def _fetch(self):
        """
        Fetches and returns the horoscope HTML page contents
        """
        r = requests.get(self._build_url())

        if r.status_code != 200:
            raise RuntimeError("Unable to fetch horoscope page for ({sign}) sign".format(
                sign=self.sign))

        return r.text

    def _parse(self, html_contents):
        """
        Parses the HTML tree and returns horoscope data
        """
        data = []
        tree = html.fromstring(html_contents)

        topics = [
            'astral-climate',
            'love-light',
            'work',
            'money',
            'vitality',
            'family',
            'friends'
        ]

        for topic in topics:
            title_elt = tree.xpath('.//h3[contains(@class, "title-{0}")]'.format(topic))[0]
            content_elt = title_elt.xpath('./following-sibling::p[@class="description-horo"]')[0]
            note_elt = title_elt.xpath('./following-sibling::div[contains(@class, "wrapper-note")]')[0]
            note_open_count = len(note_elt.xpath('.//i[contains(@class, "-o")]'))
            note_total_count = len(note_elt.xpath('.//i'))

            data.append({
                'title': title_elt.text_content(),
                'text': content_elt.text_content(),
                'note': "{} sur {}".format(note_total_count - note_open_count, note_total_count)
            })

        return data

    def _get_horoscope(self):
        """
        Fetches, parses and returns the horoscope contents
        """
        return self._parse(self._fetch())

    def tts(self):
        """
        Text To Speech horoscope data
        """
        data = self._get_horoscope()

        with tempfile.TemporaryDirectory(prefix='horo-') as tmp_dir:
            for i, topic in enumerate(data, 1):
                text = "{title}. {note}. {text}".format(
                    title=topic['title'],
                    note=topic['note'],
                    text=topic['text'])
                topic_wav_path = os.path.join(tmp_dir, 'topic-{}.wav'.format(i))
                subprocess.call(
                    'pico2wave -w {wav} -l {tts_lang} "{text}" && aplay {wav}'.format(
                        wav=topic_wav_path, tts_lang=self.tts_lang, text=text),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True)


def run():
    args = parser.parse_args()
    horoscoop = Horoscoop(sign=args.sign)
    horoscoop.tts()
