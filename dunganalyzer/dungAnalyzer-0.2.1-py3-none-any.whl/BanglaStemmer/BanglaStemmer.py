# coding: utf-8
import re

class BanglaStemmer:
    def __init__(self):
        self.re_machine = re.compile(r'[ `~!@#$%^&*()\-_=+[{\]}\\|;:\'",<.>/?\n।\u200c‘’—]')
        pass

    def _stem_verb_step_1(self, word: str) -> str:
        if word.endswith(('ই', 'ছ', 'ত', 'ব', 'ল', 'ন', 'ক', 'স', 'ম')):
            return word[:-1]
        return word

    def _stem_verb_step_2(self, word: str) -> str:
        if word.endswith(('লা', 'তা', 'ছি', 'বে', 'তে', 'ছে', 'লে', 'টি', 'নি', 'ের')):
            return word[:-2]
        return word

    def _stem_verb_step_3(self, word: str) -> str:
        if word.endswith(('ছি', 'ছে')):
            return word[:-2]
        return word

    def _harmonize_verb(self, word: str) -> str:
        # logger.warning('Harmonizing has not been implemented completely.')
        if word.endswith('য়ে'):
            return word[:-3] + 'ে'
        if word.endswith('ই'):
            return word[:-2] + 'া'
        return word

    def _stem_verb_step_4(self, word: str) -> str:
        if len(word) > 1 and not word.endswith(('ই', 'য়ে', 'ও')):
            if word.endswith(('া', 'ে', 'ি')):
                return word[:-1]
            return word
        else:
            return self._harmonize_verb(word)

    def stemWord(self, word: str) -> str:
        stemmed = self._stem_verb_step_1(word)
        stemmed = self._stem_verb_step_2(stemmed)
        stemmed = self._stem_verb_step_3(stemmed)
        stemmed = self._stem_verb_step_4(stemmed)
        return stemmed

    def stemDocument(self, document: str) -> str:
        return ' '.join([self.stemWord(word.strip()) for word in self.re_machine.split(document) if len(word.strip()) > 0])


# if __name__ == '__main__':
#     bs = BanglaStemmer()
#     print(bs.stemWord('সংবেদনশীলতা'))
