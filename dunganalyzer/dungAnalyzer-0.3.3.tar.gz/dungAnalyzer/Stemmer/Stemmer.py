# coding: utf-8
import re
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer


class Stemmer:
    def __init__(self):
        self.porter_stem = PorterStemmer()
        self.snowball_stem = SnowballStemmer('english')
        self.re_machine = re.compile(r'[ `~!@#$%^&*()\-_=+[{\]}\\|;:\'",<.>/?\n।\u200c‘’—]')
        pass

    def bangla_stem(self, word: str) -> str:
        wlen = len(word)
        if wlen > 9 and (word.endswith("িয়াছিলাম") or word.endswith("িতেছিলাম") or word.endswith("িতেছিলেন") or
                         word.endswith("ইতেছিলেন") or word.endswith("িয়াছিলেন") or word.endswith("ইয়াছিলেন")):
            return word[:-8]

        if wlen > 8 and (word.endswith("িতেছিলি") or word.endswith("িতেছিলে") or word.endswith("িয়াছিলা") or
                         word.endswith("িয়াছিলে") or word.endswith("িতেছিলা") or word.endswith("িয়াছিলি") or
                         word.endswith("য়েদেরকে")):
            return word[:-7]

        if wlen > 7 and (word.endswith("িতেছিস") or word.endswith("িতেছেন") or word.endswith("িয়াছিস") or
                         word.endswith("িয়াছেন") or word.endswith("েছিলাম") or word.endswith("েছিলেন") or
                         word.endswith("েদেরকে")):
            return word[:-6]

        if wlen > 6 and (word.endswith("িতেছি") or word.endswith("িতেছা") or word.endswith("িতেছে") or
                         word.endswith("ছিলাম") or word.endswith("ছিলেন") or word.endswith("িয়াছি") or
                         word.endswith("িয়াছা") or word.endswith("িয়াছে") or word.endswith("েছিলে") or
                         word.endswith("েছিলা") or word.endswith("য়েদের") or word.endswith("দেরকে")):
            return word[:-5]

        if wlen > 5 and (word.endswith("িলাম") or word.endswith("িলেন") or word.endswith("িতাম") or
                         word.endswith("িতেন") or word.endswith("িবেন") or word.endswith("ছিলে") or
                         word.endswith("ছিলি") or word.endswith("ছিলা") or word.endswith("তেছে") or
                         word.endswith("িতেছ") or word.endswith("খানা") or word.endswith("খানি") or
                         word.endswith("গুলো") or word.endswith("গুলি") or word.endswith("য়েরা") or
                         word.endswith("েদের")):
            return word[:-4]

        if wlen > 4 and (word.endswith("লাম") or word.endswith("িলি") or word.endswith("ইলি") or word.endswith("িলে") or
                         word.endswith("ইলে") or word.endswith("লেন") or word.endswith("িলা") or word.endswith("ইলা")
                         or word.endswith("তাম") or word.endswith("িতি") or word.endswith("ইতি") or word.endswith("িতে")
                         or word.endswith("ইতে") or word.endswith("তেন") or word.endswith("িতা") or word.endswith("িবা")
                         or word.endswith("ইবা") or word.endswith("িবি") or word.endswith("ইবি") or word.endswith("বেন")
                         or word.endswith("িবে") or word.endswith("ইবে") or word.endswith("ছেন") or word.endswith("য়োন")
                         or word.endswith("য়ের") or word.endswith("েরা") or word.endswith("দের")):
            return word[:-3]

        if wlen > 3 and (word.endswith("িস") or word.endswith("েন") or word.endswith("লি") or word.endswith("লে") or
                         word.endswith("লা") or word.endswith("তি") or word.endswith("তে") or word.endswith("তা") or
                         word.endswith("বি") or word.endswith("বে") or word.endswith("বা") or word.endswith("ছি") or
                         word.endswith("ছা") or word.endswith("ছে") or word.endswith("ুন") or word.endswith("ুক") or
                         word.endswith("টা") or word.endswith("টি") or word.endswith("নি") or word.endswith("ের") or
                         word.endswith("তে") or word.endswith("রা") or word.endswith("কে")):
            return word[:-2]

        if wlen > 2 and (word.endswith("ি") or word.endswith("ী") or word.endswith("া") or word.endswith("ো")
                         or word.endswith("ে") or word.endswith("ব") or word.endswith("ত")):
            return word[:-1]

        return word

    def stemWord(self, word: str, lang) -> str:
        # TODO: Check in Dictionary before stemming
        if lang == 'bn':
            stemmed = self.bangla_stem(word)
        elif lang == 'en_porter':
            stemmed = self.porter_stem.stem(word)
        elif lang == 'en_snowball':
            stemmed = self.snowball_stem.stem(word)
        else:
            stemmed = word

        return stemmed

    def stemDocument(self, document: str, lang) -> str:
        return ' '.join([self.stemWord(word.strip().lower(), lang) for word in self.re_machine.split(document)
                         if len(word.strip()) > 0])


if __name__ == '__main__':
    bs = Stemmer()
    print(bs.stemWord('সংবেদনশীলতা', 'bn'))
