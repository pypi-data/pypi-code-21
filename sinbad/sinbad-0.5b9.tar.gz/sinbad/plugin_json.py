'''
A Sinbad plug-in for JSON-based data sources
'''


import json
from sinbad.plugin_base import *
from sinbad.util import collapse_dicts, normalize_keys
from json.decoder import WHITESPACE, JSONDecodeError

class JSON_Infer(Base_Infer):
    
    def matched_by(self, path):
        path = path.lower()
        if path.endswith("json"): return True
        for ptrn in [".json", "=json", ".geojson", "=geojson", "/json", "/geojson"]:   # , ".json.gz", ".json.zip"]:
            if ptrn in path: return True
        return False


class CustomDecoder(json.JSONDecoder):
    
    # enable this to be a little more loose and ignore extra data...
    # or actually, if there is more data after the first JSON object,
    # see if more objects can be decoded, and collect them in a list
    def decode(self, s, _w=WHITESPACE.match):
        results_list = None
        obj, end = self.raw_decode(s, idx=_w(s, 0).end())
        end = _w(s, end).end()
        while end != len(s):  # maybe more stuff, or maybe junk...
            if not results_list: results_list = [obj]
            try:
                next_obj, end = self.raw_decode(s, end)
                end = _w(s, end).end()
                results_list.append(next_obj)
            except JSONDecodeError: # didn't work - ignore the rest
                return obj
        
        if results_list: return results_list
        else: return obj
    

class JSON_Data_Factory(Base_Data_Factory):
    
    def load_data(self, fp, encoding = None):
        return normalize_keys(collapse_dicts(json.loads(fp.read().decode(errors='ignore'),
                                                        cls=CustomDecoder,
                                                        parse_int = str,
                                                        parse_float = str)))

