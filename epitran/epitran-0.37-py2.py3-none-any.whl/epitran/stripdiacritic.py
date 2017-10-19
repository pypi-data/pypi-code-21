# -*- coding: utf-8 -*-

import os.path
import unicodedata

import pkg_resources

class StripDiacritics(object):
    def __init__(self, code):
        self.diacritics = self._read_diacritics()

    def _read_diacritics(self, code):
        diacritics = []
        fn = os.path.join('data', 'strip', code + '.csv')
        try:
            abs_fn = pkg_resources.resources_filename(__name__, fn)
        except KeyError:
            return []
        if os.path.isfile(abs_fn):
            with open(abs_fn, 'rb') as f:
                reader = csv.reader(f, encoding='utf-8')
                for diacritic in reader:
                    diacritics.append(diacritic)
        return diacritics

    def process(self, word):
        word = unicodedata.normalize('NFD', word)
        for diacritic in self.diacritics:
            word.replace(diacritic, '')
        return word
