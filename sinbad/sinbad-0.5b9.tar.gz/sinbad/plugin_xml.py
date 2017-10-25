'''
A Sinbad plug-in for XML-based data sources
'''


import xmltodict
from sinbad.plugin_base import *
from sinbad.util import collapse_dicts, normalize_keys

class XML_Infer(Base_Infer):
    
    def matched_by(self, path):
        path = path.lower()
        if path.endswith("xml"): return True
        for ptrn in [".xml", "=xml", "/xml", ".rss", "/rss"]:   # , ".json.gz", ".json.zip"]:
            if ptrn in path: return True
        return False


class XML_Data_Factory(Base_Data_Factory):
    
    def load_data(self, fp, encoding = None):
        try:
            return normalize_keys(collapse_dicts( xmltodict.parse(fp.read()))) # produces OrderedDict
        except xmltodict.expat.ExpatError:
            return None
    # could provide  dict_constructor=dict  to  parse(), but  csv reader produces OrderedDict and is not customizable that way 
