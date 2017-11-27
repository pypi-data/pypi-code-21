import os
import re
import nltk
from nltk.corpus import stopwords

try:
    nltk.download('stopwords')
except Exception as e:
    print('Failed to download nltk stopwords data, {}'.format(e))


class StopWordProcessor:
    def __init__(self):
        self.stopWordList = list(stopwords.words('english'))
        self.re_machine = re.compile(r'[ `~!@#$%^&*()\-_=+[{\]}\\|;:\'",<.>/?\n।\u200c‘’—]')
        with open(os.path.join(os.path.dirname(__file__), '../resources/stopwords-bn.txt'), encoding='utf-8') as f:
            self.stopWordList += [word.strip() for word in f.readlines()]
            pass
        pass

    def tokenizeString(self, inputString):
        words = self.re_machine.split(inputString)
        words = [word.strip().lower() for word in words if len(word.strip()) != 0]
        return words
        pass

    def removeStopWords(self, inputString):
        words = self.tokenizeString(inputString)
        return ' '.join([word for word in words if self.stopWordList.count(word) == 0])
        pass
    pass


if __name__ == '__main__':
    sw_proc = StopWordProcessor()
    print(sw_proc.removeStopWords('test in testing and what?'))
    print(sw_proc.removeStopWords('test and in আমি বাংলার গান গাই আর খেলি'))

