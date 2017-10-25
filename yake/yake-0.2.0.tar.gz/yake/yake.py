# -*- coding: utf-8 -*-

"""Main module."""

import string
import os
import jellyfish

from yake.datarepresentation import DataCore

# TODOS
# criar projeto pip
# comparar features python versus veatures c sharp

class YakeKeywordExtractor(object):

    def __init__(self, lan="en", n=3, dedupLim=0.8, windowsSize=2, top=20, features=None):
        self.lan = lan

        dir_path = os.path.dirname(os.path.realpath(__file__))
        # root_path = os.path.dirname(dir_path)
        # root_path = dir_path
        
        local_path = os.path.join("StopwordsList", "stopwords_%s.txt" % lan[:2].lower())
        resource_path = os.path.join(dir_path,local_path)

        with open(resource_path) as stop_fil:
            self.stopword_set = set( stop_fil.read().lower().split("\n") )

        self.n = n
        self.top = top
        self.dedupLim = dedupLim
        self.features = features
        self.windowsSize = windowsSize

    def get_keys(self, path):        
        return set([self.simplify_key(key.lower().strip()) for key in self.get_text(path).split('\n')])

    def simplify_key(self, key):

        exclude = set(string.punctuation)
        key = ' '.join([w for w in split_contractions(web_tokenizer(key)) if len([c for c in w if c in exclude]) != len(w) and not (w.startswith("'") and len(w) > 1) and len(w) > 0])
        #print(key)
        return key

    def get_text(self, path):

        try:
            with open(path, encoding="utf8") as fil:
                return fil.read()
        except:
            with open(path) as fil:
                return fil.read()
    
    def extract_keywords(self, text):
        text = text.replace('\n\t',' ')
        dc = DataCore(text=text, stopword_set=self.stopword_set, windowsSize=self.windowsSize, n=self.n)
        dc.build_single_terms_features(features=self.features)
        dc.build_mult_terms_features(features=self.features)
        resultSet = []
        for cand in dc.candidates.values():
            if cand.isValid():
                candidates_to_replace = []
                cand_to_replace = None
                max_cand = None
                for (i,(h, candResult)) in enumerate(resultSet):
                    if max_cand == None or max_cand[0] < h:
                        max_cand = (h, i)
                    if candResult.H >= cand.H:
                        #dist = jellyfish.jaro_winkler(cand.unique_kw, candResult.unique_kw ) #_tJW
                        dist = 1.-jellyfish.levenshtein_distance(cand.unique_kw, candResult.unique_kw ) / max(len(cand.unique_kw),len(candResult.unique_kw)) # _tL
                        if dist > self.dedupLim and (cand_to_replace == None or cand_to_replace[0] < dist):
                            cand_to_replace = ( dist, i, candResult )
                if cand_to_replace != None:
                    resultSet[cand_to_replace[1]] = (cand.H, cand)
                elif len(resultSet) != self.top:
                    resultSet.append( (cand.H, cand) )
                elif max_cand[0] >= cand.H:
                    resultSet[max_cand[1]] = (cand.H, cand)
        resultSet = sorted(resultSet, key=lambda c: c[0])
        return [ (h,cand.unique_kw) for (h,cand) in resultSet]
