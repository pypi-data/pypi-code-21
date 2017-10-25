
import platform, sys, hashlib, json, webbrowser
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from json.decoder import JSONDecodeError

import sinbad
from sinbad import prefs


HOLD_TIME = 1    # number of seconds that we will wait to get a response back from the server

os_info = platform.uname().system + "/" + platform.uname().release
lang_info = 'python {}.{}.{} {}'.format(*sys.version_info[0:4])


def handle_response(resp):
    '''Handle a response (string, probably JSON format) from the server'''
    if not resp: return
    
    try:
        obj = json.loads(resp)
        if isinstance(obj, dict) and obj.get('launch_url'):
            webbrowser.open_new(obj['launch_url'])
        #print('Got: ' + str(obj))
    except JSONDecodeError:
        #print("Nope: " + str(resp))
        pass  # it's ok... probably just an "OK" string
   

def make_request(post_fields):
    #print(post_fields)
    url = prefs.get_pref("server_base") + 'service.php'
    request = Request(url, urlencode(post_fields).encode())
    result = None
    try:
        result = urlopen(request, None, HOLD_TIME)
    except OSError:
        pass   # allow to timeout/fail silently 
    
    if result: handle_response(result.read().decode(errors='ignore'))
   
   
def register_fetch(usage_info):
    make_request({'type' : 'usage',
                   'version'    : sinbad.__version__,
                   'token'      : hashlib.md5(sinbad.__version__.encode()).hexdigest(),
                   'os'         : os_info,
                   'lang'       : lang_info,
                   'usage_type' : 'fetch',
                   'full_url'   : usage_info.get('full_url'),
                   'format'     : usage_info.get('format_type'),
                   'file_entry' : usage_info.get('file_entry'),
                   'field_paths' : usage_info.get('field_paths'),     
                   'base_path' : usage_info.get('base_path'),            
                   'select' : usage_info.get('select'),
                   'got_data' : bool(usage_info.get('got_data'))
                   })

   
def register_sample(usage_info):   
    make_request({'type' : 'usage',
                   'version'    : sinbad.__version__,
                   'token'      : hashlib.md5(sinbad.__version__.encode()).hexdigest(),
                   'os'         : os_info,
                   'lang'       : lang_info,
                   'usage_type' : 'sample',
                   'full_url'   : usage_info.get('full_url'),
                   'format'     : usage_info.get('format_type'),
                   'file_entry' : usage_info.get('file_entry'),
                   'sample_amt' : usage_info.get('sample_amt'),     
                   'sample_seed' : usage_info.get('sample_seed')              
                   })
   
   
def register_load(usage_info):  # full_url, format_type, status, sample_amt, sample_seed, data_options):   
    make_request({'type' : 'usage',
                   'version'    : sinbad.__version__,
                   'token'      : hashlib.md5(sinbad.__version__.encode()).hexdigest(),
                   'os'         : os_info,
                   'lang'       : lang_info,
                   'usage_type' : 'load',
                   'full_url'   : usage_info.get('full_url'),
                   'format'     : usage_info.get('format_type'),
                   'status'     : usage_info.get('status'),
                   'file_entry' : usage_info.get('file_entry'),
                   'data_options' : usage_info.get('data_options'),                   
                   })
    
        
def register_install():
    make_request({'type' : 'install',
                   'version' : sinbad.__version__,
                   'token' : hashlib.md5(sinbad.__version__.encode()).hexdigest(),
                   'os' : os_info,
                   'lang' : lang_info,
                   'first_use_ts' : sinbad.util.current_time()
                   })      
    

def register_milestone():
    p = prefs.load_pref_file()
    make_request({'type' : 'milestone',
                  'version' : sinbad.__version__,
                   'token' : hashlib.md5(sinbad.__version__.encode()).hexdigest(),
                   'os' : os_info,
                   'lang' : lang_info,
                   "run_count"    : p['run_count'],
                   "first_use_ts" : p['first_use_ts'],
                   "last_use_ts"  :  p['last_use_ts']})

    