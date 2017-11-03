import os
import requests
from cachingutil.json_file_cache import JsonFileCache
from collections import OrderedDict


class MD5Cache(JsonFileCache):

    OBJECT_PAIRS_HOOK = OrderedDict

    def key(self,
            text,
            **params):
        return text

    def fetch_from_source(self,
                          text,
                          **params):
        print(u'fetching from source')
        return requests.get(u'http://md5.jsontest.com/?text={text}'.format(text=text)).json()

WEEK = 7*24*60*60*60

json_test_file_cache = MD5Cache(folder=os.getcwd(),
                                sub_folder=u'temp',
                                max_age=WEEK)

print(u"Will show 'fetching from source' if the item is not cached or is expired...")
print(json_test_file_cache.fetch(text=u'test'))