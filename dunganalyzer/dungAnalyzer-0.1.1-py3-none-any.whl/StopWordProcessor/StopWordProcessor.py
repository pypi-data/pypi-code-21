import os
import re


class StopWordProcessor:
    def __init__(self):
        # print(os.path.join(os.path.dirname(__file__), '../resources/stopwords-bn.txt'))
        self.re_machine = re.compile(r'[ `~!@#$%^&*()\-_=+[{\]}\\|;:\'",<.>/?\n।\u200c‘’—]')
        with open(os.path.join(os.path.dirname(__file__), '../resources/stopwords-bn.txt')) as f:
            self.stopWordList = [word.strip() for word in f.readlines()]
            pass
        pass

    def tokenizeString(self, inputString):
        words = self.re_machine.split(inputString)
        words = [word for word in words if len(word.strip()) != 0]
        return words
        pass

    def removeStopWords(self, inputString):
        words = self.tokenizeString(inputString)
        return ' '.join([word for word in words if self.stopWordList.count(word) == 0])
        pass
    pass
