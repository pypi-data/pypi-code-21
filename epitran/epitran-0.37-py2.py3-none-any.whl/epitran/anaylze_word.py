from __future__ import print_function
from __future__ import division

import panphon
import epiphon
import unicodedata

class WordAnalyzer(panphon.FeatureTable):
    def __init__(self, code):
        filename = filenames[feature_set]
        self.epitran = epitran.Epitran(code)
        self.segments, self.seg_dict, self.names = self._read_table(filename)
        self.seg_seq = {seg[0]: i for (i, seg) in enumerate(self.segments)}
        self.weights = self._read_weights()
        self.seg_regex = self._build_seg_regex()
        self.dogol_prime = self._dogolpolsky_prime()

    def analyze_word(self, token):
        segs = []
        while token:
            cat_0, case_0 = tuple(unicodedata.category(token[0]))
