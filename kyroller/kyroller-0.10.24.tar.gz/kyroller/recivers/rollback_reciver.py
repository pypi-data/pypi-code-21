from threading import Thread
import requests
import time
from socketIO_client import SocketIO
from ..types import Tick, Bar, MarketEvent, IncorrectDataException
import logging
import hashlib
import os
import sys
import codecs
log = logging.getLogger('RollbackReciver')


class RollbackReciver:

    def __init__(self, url, subs, begin, end):
        self.url = url
        self.subs = subs
        self.begin = begin
        self.end = end
        self.runing = False

    def get_cache_file(self, url):
        if not os.path.exists('./cache'):
            os.mkdir('./cache')
        cache_file_name = hashlib.md5(url.encode('utf_8')).hexdigest()
        return './cache/' + cache_file_name + '.txt'

    def generate_events(self):
        real_url = "%s/inday-range?subs=%s&begin=%s&end=%s" % (
            self.url, self.subs, self.begin, self.end)
        cache_file_name = self.get_cache_file(real_url)
        if os.path.exists(cache_file_name):
            with codecs.open(cache_file_name, 'r', 'utf-8') as stream:
                for line in stream:
                    try:
                        (evt, msg) = line.strip().split('|')
                        if evt == 'market':
                            sp = msg.split(',')
                            e = MarketEvent(sp[0], int(sp[1]), sp[2])
                            yield (evt, e)
                        elif evt == 'tick':
                            tick = Tick(msg)
                            yield (evt, tick)
                        elif evt == 'bar':
                            bar = Bar(msg)
                            yield (evt, bar)
                    except IncorrectDataException as e:
                        print(line)
                        print(e)
                    except ValueError as e:
                        print(line)
                        print(e)
            return
        else:
            res = requests.get(real_url, stream=True)
            tmp_file = cache_file_name + '.tmp'
            with codecs.open(tmp_file, 'w', 'utf-8') as f:
                for line_bytes in res.iter_lines(decode_unicode=True):
                    line = line_bytes.decode('utf-8').strip()
                    f.write(line + '\n')
                    try:
                        (evt, msg) = line.strip().split('|')
                        if evt == 'market':
                            sp = msg.split(',')
                            e = MarketEvent(sp[0], int(sp[1]), sp[2])
                            yield (evt, e)
                        elif evt == 'tick':
                            tick = Tick(msg)
                            # 补全 date
                            tick.preclose_backadj = self.get_pre_close(
                                tick.date, tick.symbol)
                            yield (evt, tick)
                        elif evt == 'bar':
                            bar = Bar(msg)
                            bar.preclose_backadj = self.get_pre_close(
                                bar.date, bar.symbol)
                            yield (evt, bar)
                    except IncorrectDataException as e:
                        print(line)
                        print(e)
                    except ValueError as e:
                        print(line)
                        print(e)
            os.rename(tmp_file, cache_file_name)
