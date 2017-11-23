from pyavrophonetic import avro
from mstranslator import Translator
from redislite import Redis
import re


class ConvQ:
    def __init__(self, sub_key, db_dir):
        self.ms_t = Translator(sub_key)
        self.redis = Redis(db_dir + '/redis.db')
        self.my_regex = re.compile(r'[ `~!@#$%^&*()\-_=+[{\]}\\|;:\'",<.>/?]')

    @staticmethod
    def is_english(query):
        try:
            query.encode(encoding='utf-8').decode('ascii')
        except UnicodeDecodeError:
            return False
        else:
            return True

    def detect_lang(self, query):
        score = 0
        words = query.split(' ')
        for word in words:
            if self.is_english(word):
                score += 1
            else:
                score -= 1
        if score == len(words):
            return 'en'
        elif -score == len(words):
            return 'bn'
        else:
            return 'mixed'

    def expand(self, query):
        words = self.my_regex.split(query)
        words = [x.strip().lower() for x in words if len(x.strip()) > 0]
        concat_words = ' '.join(words)
        avro_conv = avro.parse(concat_words)
        ret_arr = [[concat_words, self.detect_lang(concat_words)], [avro_conv, self.detect_lang(avro_conv)]]

        trans_arr = []
        conn_flag = True
        for word in words:
            trans = self.redis.get(word)
            if trans is None:
                try:
                    if not conn_flag:
                        raise ConnectionError('Connection error while communicating with translate API')
                    if self.is_english(word):
                        lang_from = 'en'
                        lang_to = 'bn'
                    else:
                        lang_from = 'bn'
                        lang_to = 'en'
                    trans = self.ms_t.translate(word, lang_from=lang_from, lang_to=lang_to)
                    trans = trans.lower()
                    # print('ms_output: {}'.format(trans))
                    self.redis.set(word, trans)
                except Exception as e:
                    conn_flag = False
                    print('Error: {}'.format(e))
                    trans = word
            else:
                trans = trans.decode('utf-8')
            trans_arr.append(trans)

        ms_conv = ' '.join(trans_arr)
        ret_arr.append([ms_conv, self.detect_lang(ms_conv)])

        return ret_arr
