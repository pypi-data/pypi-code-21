from .Normalizer import BanglaNormalizer
from .StopWordProcessor import StopWordProcessor
from .Stemmer import Stemmer


class BanglaAnalyzer:
    def __init__(self):
        self.normalizer = BanglaNormalizer(remove_nuktas=True)
        self.stop_extractor = StopWordProcessor()
        self.stemmer = Stemmer()

    def analyze(self, doc):
        doc = self.normalizer.normalize_doc(doc)
        doc = self.stop_extractor.removeStopWords(doc)
        doc = self.stemmer.stemDocument(doc, 'bn')
        return doc


class EnglishAnalyzer:
    # en_stemmers available: "en_snowball", "en_porter"
    def __init__(self, en_stemmer='en_snowball'):
        self.stop_extractor = StopWordProcessor()
        self.stemmer = Stemmer()
        self.en_stemmer = en_stemmer

    def analyze(self, doc):
        doc = self.stop_extractor.removeStopWords(doc)
        doc = self.stemmer.stemDocument(doc, self.en_stemmer)
        return doc
