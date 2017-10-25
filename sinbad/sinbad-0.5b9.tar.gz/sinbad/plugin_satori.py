'''
A Sinbad plug-in for Satori-based data sources
'''


import json
from satori.rtm.connection import Connection

from sinbad.plugin_base import *
from sinbad.util import collapse_dicts, normalize_keys

class Satori_Infer(Base_Infer):
    
    def matched_by(self, path):
        path = path.lower()
        if path.startswith("wss:") and path.find("satori") >= 0: return True
        
        return False


class Satori_Data_Factory(Base_Data_Factory):

    def __init__(self):
        super().__init__()
        self.channel = None
        self.appkey = None
    
    
    def load_data(self, fp, encoding = None):
        '''
        Here, fp is a path string "wss://..." rather than a file-like object 
        '''
# TODO: fix this violation of how this method ties in... !        
        if not self.appkey: 
            print("Warning: Need to set 'appkey' option for Satori data source")
            return None
        if not self.channel: 
            print("Warning: Need to set 'channel' option for Satori data source")
            return None
        
        c = Connection(fp, self.appkey)
        c.start()
        data = normalize_keys(collapse_dicts(json.loads(c.read_sync(self.channel))))
        c.stop()
        return data


    def get_options(self):
        return ["channel", "appkey"]
    
    
    def get_option(self, name):
        if name == "channel":
            return self.channel
        elif name == "appkey":
            return self.appkey
        else:
            return None


    def set_option(self, name, value):
        if name == "channel":
            self.channel = value
        elif name == "appkey":
            self.appkey = value
        pass

