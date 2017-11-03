from nltk.tokenize import RegexpTokenizer
#from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import ItalianStemmer
from stop_words import get_stop_words


class Util:
    def __init__(self):
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.it_stop_words = get_stop_words('it')
        self.other_it_stop_words = ['a', 'adesso', 'ai', 'al', 'alla', 'allo', 'allora', 'altre', 'altri', 'altro', 'anche', 'ancora', 'avere', 'aveva', 'avevano', 'ben', 'buono', 'che', 'chi', 'cinque', 'comprare', 'con', 'consecutivi', 'consecutivo', 'cosa', 'cui', 'da', 'del', 'della', 'dello', 'dentro', 'deve', 'devo', 'di', 'doppio', 'due', 'e', 'ecco', 'fare', 'fine', 'fino', 'fra', 'gente', 'giu', 'ha', 'hai', 'hanno', 'ho', 'il', 'indietro', 'invece', 'io', 'la', 'lavoro', 'le', 'lei', 'lo', 'loro', 'lui', 'lungo', 'ma', 'me', 'meglio', 'molta', 'molti', 'molto', 'nei', 'nella', 'no', 'noi', 'nome', 'nostro', 'nove', 'nuovi', 'nuovo', 'o', 'oltre', 'ora', 'otto', 'peggio', 'pero', 'persone', 'piu', 'poco', 'primo', 'promesso', 'qua', 'quarto', 'quasi', 'quattro', 'quello', 'questo', 'qui', 'quindi', 'quinto', 'rispetto', 'sara', 'secondo', 'sei', 'sembra\tsembrava', 'senza', 'sette', 'sia', 'siamo', 'siete', 'solo', 'sono', 'sopra', 'soprattutto', 'sotto', 'stati', 'stato', 'stesso', 'su', 'subito', 'sul', 'sulla', 'tanto', 'te', 'tempo', 'terzo', 'tra', 'tre', 'triplo', 'ultimo', 'un', 'una', 'uno', 'va', 'vai', 'voi', 'volte', 'vostro']
        self.total_it_stop = list(set(self.it_stop_words)|set(self.other_it_stop_words))


    def clean_document(self, data):
        data = data.encode('utf-8').decode('utf-8')
        raw = data.lower()
        tokens = self.tokenizer.tokenize(raw)
        stopped_tokens = self.remove_stopwords(tokens)
        #stemmer = PorterStemmer()
        #stemmed_tokens = [stemmer.stem(token) for token in stopped_tokens]
        stemmer = ItalianStemmer()
        stemmed_tokens = [stemmer.stem(token) for token in stopped_tokens]
        return stemmed_tokens


    def remove_stopwords(self, tokenized_data):
        it_stop = self.total_it_stop
        stopped_tokens = [token for token in tokenized_data if token not in it_stop and not token.isdigit()]
        return stopped_tokens