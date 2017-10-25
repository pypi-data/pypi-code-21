
import gzip
import hashlib
import ssl
import time
import urllib.request

from os import system, path
from platform import system as platform

try:
    the_ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS)
except AttributeError:
    the_ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_SSLv23)


def hash_string(str):
    '''Return a simple hash of the given string.
    
    The hash itself is a string of at most 25 characters.
    '''
    h = hashlib.sha1(str.encode('utf_8')).hexdigest()
    return h[:25]


def current_time_millis():
    '''Return the current time in milliseconds'''
    return int(time.time() * 1000)


def current_time():
    '''Return the current time in seconds'''
    return int(time.time())


def smells_like_url(path):
    '''Determine if the given path seems like a URL.
    
    Currently, only things that start off http://
    https:// or ftp:// are treated as URLs.
    '''
    return path.find("://") >= 0 and \
        (path.startswith("http") or path.startswith("ftp")) 


def smells_like_zip(path):
    return path.find(".zip") >= 0


def smells_like_gzip(path):
    return path.find(".gz") >= 0


def create_input(path):
    return raw_create_input(path)[0]


def raw_create_input(path):
    '''Returns a triple, ( fp, real_name, enc ), containing a file-type object
    for the given path, an alternate name for the resource, and an encoding.
    
    If the path is a normal file, produces a file-object for that file.
    
    If the path is a URL, makes a request to that URL and
    returns an input stream to read the response.
    
    In the process of processing the response from the URL,
    if a name for the file is found (e.g. in 
    a Content-Disposition header), that is produced as real_name. 
    Otherwise real_name is returned as None.
    
    If an encoding is determined from the URL response
    headers, it is included, otherwise the third element 
    of the triple is None.    
    '''
    if not path: return None, None, None
    
    charset = None
    local_name = None
    if smells_like_url(path):
        req = urllib.request.Request(path, 
                                     data=None,
                                     headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'})
        file = urllib.request.urlopen(req, context=the_ssl_context)
        charset = file.info().get_content_charset()
        if 'Content-Disposition' in file.info():
            # If the response has Content-Disposition, we take file name from it
            local_name = file.info()['Content-Disposition'].split('filename=')[1]
            if local_name[0] == '"' or local_name[0] == "'":
                local_name = local_name[1:-1]
            path=local_name
            #print("CONTENT: {}".format(path))
    elif path.startswith("wss:"):
        return (None, None, None)
    else:
        file = open(path, 'rb')  # binary to be consistent with urlopen 

    if smells_like_gzip(path):
        file = gzip.GzipFile('', 'rb', 9, file)

    return (file, local_name, charset)
    


def normalize_keys(data):
    '''Ensures that keys in the dictionary follow identifier naming rules. 
    
    (This is required because the jsonpath parser is picky.) 
    '''
    if isinstance(data, list):
        for i in range(len(data)):
            data[i] = normalize_keys(data[i])
    elif isinstance(data, dict):
        for k, v in data.items():
            #if k.find("-") >= 0:
            #    del data[k]
            #    k = k.replace("-", "_")
            #    data[k] = v
            
            if k[0].isdigit():
                del data[k]
                k = "_" + k
                data[k] = v
                
            normalize_keys(v)
    
    return data
    

def collapse_lists(data):
    if all(isinstance(el, list) for el in data):
        return [item for sublist in data for item in sublist]
    else:
        return data


def collapse_dicts(data):
    '''
    Removes extraneous levels of dictionary nesting.
    
    For example,
         { 'a' : { 'b' : { 'c' : "blah", 'd' : "blah" } } }
    turns into
         { 'c' : "blah", 'd' : "blah" }
    '''
    if not isinstance(data, dict):
        return data
    else:
        for k, v in data.items():
            data[k] = collapse_dicts(v)
            
        first_item = None
        first_value = None
        for first_item, first_value in data.items(): break          # https://stackoverflow.com/questions/59825/how-to-retrieve-an-element-from-a-set-without-removing-it
        if len(data.keys()) == 1 and first_item and isinstance(first_value, dict) and \
                len(first_value.keys()) == 1:
            for _, first_value_value in first_value.items(): break
            data[first_item] = first_value_value
        
        if len(data.keys()) == 1:
            data = first_value
        
        return data



def extract_base_path(paths, seps = ['.', '/']):
    if len(paths) <= 1: return None, paths
    
    p = path.commonprefix(paths)
    i = 1
    while i < len(p) and p[-i] not in seps:  # so we split on the separator
        i = i + 1
    if (len(p) == 0
            or i >= len(p) 
            or p[:-i] == '$[*]'): 
        return None, paths

    p = p[:-i]
    return p, [ pth[len(p) + 1:] for pth in paths ]



def drop_lines(str_data, n):
    i = 0
    for i in range(len(str_data)):
        if n <= 0: break
        if str_data[i] == '\n': n = n - 1

    if n > 0: return ''
    else: return str_data[i:]
    
    

def tk_to_front(root):
    root.focus_force()
    
    if platform() == 'Darwin':  # How Mac OS X is identified by Python
        system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')

