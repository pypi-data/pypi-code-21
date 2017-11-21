from pyavrophonetic import avro
from mstranslator import Translator
from redislite import Redis
import re


class ConvQ:
    def __init__(self, sub_key, db_dir):
        self.ms_t = Translator(sub_key)
        self.redis = Redis(db_dir + '/redis.db')
        self.my_regex = re.compile(r'[ `~!@#$%^&*()\-_=+[{\]}\\|;:\'",<.>/?]')

    def expand(self, query, language):
        words = self.my_regex.split(query)
        words = [x.strip().lower() for x in words if len(x.strip()) > 0]
        concat_words = ' '.join(words)
        ret_arr = [concat_words]

        if language == 'en':
            ret_arr.append(avro.parse(concat_words))

            trans_arr = []
            conn_flag = True
            for word in words:
                trans = self.redis.get(word)
                if trans is None:
                    try:
                        if not conn_flag:
                            raise ConnectionError('Connection error while communicating with translate API')
                        trans = self.ms_t.translate(word, lang_from='en', lang_to='bn')
                        # print('ms_output: {}'.format(trans))
                        self.redis.set(word, trans)
                    except Exception as e:
                        conn_flag = False
                        print('Error: {}'.format(e))
                        trans = word
                else:
                    trans = trans.decode('utf-8')
                trans_arr.append(trans)

            ret_arr.append(' '.join(trans_arr))

        elif language == 'bn':
            trans_arr = []
            conn_flag = True
            for word in words:
                trans = self.redis.get(word)
                if trans is None:
                    try:
                        if not conn_flag:
                            raise ConnectionError('Connection error while communicating with translate API')
                        trans = self.ms_t.translate(word, lang_from='bn', lang_to='en')
                        trans = trans.lower()
                        self.redis.set(word, trans)
                    except Exception as e:
                        conn_flag = False
                        print('Error: {}'.format(e))
                        trans = word
                else:
                    trans = trans.decode('utf-8')
                trans_arr.append(trans)
            ret_arr.append(' '.join(trans_arr))

        return ret_arr
