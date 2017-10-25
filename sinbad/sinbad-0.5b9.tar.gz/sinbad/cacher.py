'''
Provides functionality to store cached data sources 
in the user's local temporary file directory. Use the
default_cacher() function to obtain the global singleton
Cacher object. Use update_* functions to produce modified
Cacher objects if desired.
'''

import json
import os.path
import tempfile
import shutil

import sinbad.util as U
from sinbad.dot_printer import Dot_Printer

# private globals
__sinbadCacheEnabled = True

# public constants
NEVER_CACHE = 0
NEVER_RELOAD = -1

# private constants
__DEFAULT_CACHE_DIR__ = os.path.join(tempfile.gettempdir(), "sinbad_cache")
__MINIMUM_TIMEOUT_VALUE__ = 100 # milliseconds


def setCaching(onOff):
    '''Enable or disable global caching behavior'''
    global __sinbadCacheEnabled
    __sinbadCacheEnabled = onOff
    
def is_caching():
    '''Determine if caching is currently enabled globally or not'''
    global __sinbadCacheEnabled
    return __sinbadCacheEnabled



class Cacher:
    '''
    Manages a cache directory and has an adjustable timeout
    (cache expiration) setting.
    '''
    
    def __init__(self):
        '''Clients should generally use the singleton Cacher object
        provided by default_cacher() instead of using this constructor. 
        '''
        global __DEFAULT_CACHE_DIR__
        self.cache_directory = __DEFAULT_CACHE_DIR__
        self.cache_expiration = NEVER_RELOAD 
        

    def is_stale(self, path, subtag):
        '''Determine if the given path+subtag is not in the cache or expired.'''
        
        if not (is_caching() and self.__is_cacheable(path, subtag)): 
            return True
                
        entry = self.cache_entry_for(path, subtag)
        if not entry or is_expired(entry, self.cache_expiration): 
            return True
        
        return False

    
    def clear_cache_data(self, tag, subtag):
        '''Delete the stored data in the cache directory and remove info from the cache index file.'''
        
        entry = self.cache_entry_for(tag, subtag)
        if not entry: return False
        if data_valid(entry):
            try: os.remove(entry["cachedata"])
            except OSError: pass
        return self.remove_entry(entry)
    
    
    def cache_entry_for(self, tag, subtag):
        '''Return the cache entry (dictionary) object for the tag+subtag pair if it exists.'''
        
        cel = self.__read_cache_entry_list(self.__get_cache_index_file(tag))

        for e in cel:
            if (e["tag"] == tag and 
                e["subtag"] == subtag):
                return e
            
        return None
    
    
    def lookup_entry_data(self, tag, subtag):        
        entry = self.cache_entry_for(tag, subtag)
        if entry:
            if is_expired(entry, self.cache_expiration):
                self.clear_cache_data(tag, subtag)
            else:
                return entry["cachedata"]
        return None


    def add_or_update_entry(self, entry):
        '''Replace the cache entry in the cache index file that has the same 
        tag+subtag pair as the given cache entry with the given cache entry. 
        If there is not already an entry for that tag+subtag, then the given
        entry is added to the list in the index file.'''
        
        cache_index_name = self.__get_cache_index_file(entry["tag"])
        cel = self.__read_cache_entry_list(cache_index_name)
        
        is_new = True
        for i, e in enumerate(cel):
            if (tags_match(e, entry)):
                cel[i] = entry
                is_new = False
        if is_new:
            cel.append(entry)
            
        self.__write_cache_entry_list(cache_index_name, cel)
            
    
    def remove_entry(self, entry):
        '''Remove a particular entry from the index file that it belongs to.'''
        cache_index_name = self.__get_cache_index_file(entry["tag"])
        cel = self.__read_cache_entry_list(cache_index_name)
        leftover_cel = [e for e in cel if not tags_match(e, entry)]
        self.__write_cache_entry_list(cache_index_name, leftover_cel)
        return True
    
    
    def read_and_cache(self, path, fp=None):
        '''Reads the data (as bytes) from the given path (or already opened file
        object) and stores it in a temporary file in the local cache directory
        (using cache_byte_data). 
        
        Returns a triple of:
         - the path to the cached data file
         - an alternate name for the data (e.g. from content-disposition header)
         - an encoding for the data if detected by raw_create_input.'''
        try:
            d = None
            real_name, enc = (None, None)
            try:
                if not fp:
                    if U.smells_like_url(path):
                        d = Dot_Printer("Downloading {} (this may take a moment)".format(path))
                        d.start()
                    fp, real_name, enc = U.raw_create_input(path)
                #if real_name and real_name is not path: print("Got: " + real_name)
                #if enc: print("Encoding: " + enc)
                data = fp.read()
            finally:
                if d: d.stop()
        except OSError as err:
            print("OSError: {}".format(err.reason))
            raise FileNotFoundError("Failed to load: " + path + "\nCHECK NETWORK CONNECTION, if applicable") 
        
        cached_file = self.cache_byte_data(path, data)
        return cached_file, real_name, enc
    

    def resolve_path(self, path, subtag):
        '''Returns a local path to the cached data for the given path+subtag.
        
        If caching is not enabled, or the path is already a local path, or
        not cacheable for whatever reason, then the path is returned unchanged.
        
        If subtag is 'main', then the resource identified by path will be 
        downloaded and cached if it is not already, or if it has become stale.
        
        If subtag is NOT 'main', but the path+subtag is not in the cache, 
        then None is returned. 
        '''
        # first make sure caching is enabled and that the path is not a local file
        if not (is_caching() and self.__is_cacheable(path, subtag)):
            return path
        
        cacheIndexName = self.__get_cache_index_file(path)
        if cacheIndexName is None: return path
        
        #print(cacheIndexName)
        entry = self.cache_entry_for(path, subtag)
        if entry and not data_valid(entry):
            self.clear_cache_data(path, subtag)
            entry = None
            
        cache_path = entry["cachedata"] if entry else None
        
        if subtag.startswith("main"):
            if (not cache_path) or \
                    (entry and is_expired(entry, self.cache_expiration)):
                #print("Refreshing cache for: " + path + " (" + subtag + ")")
                cached_file_path, real_name, enc = self.read_and_cache(path)
                if cache_path:   # need to remove the old cached file
                    os.remove(cache_path)
                
                entry = make_entry(path, subtag, cached_file_path, U.current_time_millis())
                self.add_or_update_entry(entry)
                
                # if real_name or enc were detected by raw_create_input via the read_and_cache method
                # then cache those as well
                if real_name:
                    #print("adding real-name: {} for {}".format(real_name, path))
                    rn_entry = make_entry(path, "real-name", real_name, U.current_time_millis())
                    self.add_or_update_entry(rn_entry)
                if enc:
                    #print("adding enc: {} for {}".format(enc, path))
                    enc_entry = make_entry(path, "encoding", enc, U.current_time_millis())
                    self.add_or_update_entry(enc_entry)
                
                
                return cached_file_path
        else:
            if entry and is_expired(entry, self.cache_expiration):
                return None
        
        #print("Using previously data cached for " + path + " (" + subtag + ")")
        return cache_path
    
    
    def add_to_cache(self, path, subtag, fp):
        '''Reads data from the given file object and stores it in the local
        cache directory (using read_and_cache) and also updates the cache
        index file accordingly.
        
        (This is sort of a simple, manual version of resolve_path.)
        
        Returns True if the whole procedure succeeded.'''
        global NEVER_CACHE
        if not is_caching() or self.cache_expiration == NEVER_CACHE: return False
        
        cacheIndexName = self.__get_cache_index_file(path)
        if cacheIndexName is None: return False
        
        entry = self.cache_entry_for(path, subtag)
        cache_path = entry["cachedata"] if entry else None
        #print("Refreshing cache for: " + path + " (" + subtag + ")")
        
        cached_file_path, _, _ = self.read_and_cache(path + " (" + subtag + ")", fp=fp)
        if cache_path:   # need to remove the old cached file
            os.remove(cache_path)
        entry = make_entry(path, subtag, cached_file_path, U.current_time_millis())
        self.add_or_update_entry(entry)
        return True
    

    def update_directory(self, newdir):
        '''Returns an new Cacher object like self but with the given cache directory.'''
        new_cacher = Cacher()
        new_cacher.cache_directory = newdir
        new_cacher.cache_expiration = self.cache_expiration
        return new_cacher
    
    
    def update_timeout(self, value):
        '''Returns an new Cacher object like self but with the given cache expiration value
        specified in milliseconds.
        
        The value cannot be less than the global minimum (100msec = 1/10second).'''
        global __MINIMUM_TIMEOUT_VALUE__
        if (value > 0 and value < __MINIMUM_TIMEOUT_VALUE__):
            print("Warning: cannot set cache timeout less than " + str(__MINIMUM_TIMEOUT_VALUE__) + " msec.")
            value = __MINIMUM_TIMEOUT_VALUE__
            
        new_cacher = Cacher()
        new_cacher.cache_directory = self.cache_directory
        new_cacher.cache_expiration = value
        return new_cacher
    
    
    def clear_cache(self):
        '''Delete the entire cache directory being maintained by this Cacher.'''  
        if os.path.isdir(self.cache_directory):    
            shutil.rmtree(self.cache_directory)
            
    
    def cache_byte_data(self, tag, data, encoding=None):
        '''Creates a temporary file in the cache directory and writes the 
        given data to it, encoding it first if one is provided.
        
        tag is used to determine the subdirectory in which the temp
        file is created.
           
        Note: a new temporary file is created each time this function is called
        
        Returns the path to the newly-created file 
        '''
                
        if encoding:
            stuff = data.encode(encoding)
        else:
            stuff = data
                
        cacheDir = os.path.join(self.cache_directory, self.__cacheSubdirName(tag))
        os.makedirs(cacheDir, 0o777, True)
        
        fd, temp_path = tempfile.mkstemp(".dat", "cache", cacheDir)
        os.write(fd, stuff)
        os.close(fd)
        
        return temp_path


    def __is_cacheable(self, path, subtag):
        global NEVER_CACHE
        # if it's something other than "main" data being accessed (e.g. "schema")
        #   then it can be in the cache, even if the main is a local file
        # otherwise, if it's the "main" data we're considering, then only cache
        #  if it smells like a URL and the cacher specific setting is not set 
        #  to never cache
        return (not subtag.startswith("main")) or \
                U.smells_like_url(path) and self.cache_expiration != NEVER_CACHE
    
    
    def __get_cache_index_file(self, tag):
        if not os.path.exists(self.cache_directory):
            os.makedirs(self.cache_directory, 0o777, True)
        if not os.path.isdir(self.cache_directory):
            return None

        cacheIndexFile = os.path.join(self.cache_directory, self.__cacheIndexName(tag) )
        
        if not os.path.exists(cacheIndexFile):
            self.__write_cache_entry_list(cacheIndexFile, [])
        
        if not os.path.isfile(cacheIndexFile):
            return None
        
        return os.path.abspath( cacheIndexFile )


    def __cacheIndexName(self, tag):
        return "idx" + str(U.hash_string(tag)) + ".json"
    
    
    def __cacheSubdirName(self, tag):
        return "dat" + str(U.hash_string(tag))

            
    def __read_cache_entry_list(self, cache_index_name):
        if not cache_index_name: return []
        
        try:
            with open(cache_index_name, 'r') as fp:
                return json.load(fp)
        except OSError:
            return []
        
        
    def __write_cache_entry_list(self, cache_index_name, cel):
        try:
            with open(cache_index_name, 'w') as fp:
                json.dump(cel, fp)
        except OSError:
            return False
        return True
            

        
### other entry-related functions

def make_entry(tag, subtag, cachedata, timestamp):
    '''Cache entries are a dictionary:
        { "tag" : ..., "subtag" : ..., "cachedata" : ..., "timestamp" : ... }
       where 'cachedata' is a local file path,
             'timestamp' is in milliseconds
    '''
    return { "tag" : tag, "subtag" : subtag, "cachedata" : cachedata, "timestamp" : timestamp }


def data_valid(entry):
    '''Check to see if the entry's cachedata refers to an actual readable file.'''
    if entry["cachedata"] and \
            os.path.isfile(entry["cachedata"]):
        fp = U.raw_create_input(entry["cachedata"])[0]
        if fp:
            fp.close()
            return True

    return False


def is_expired(entry, expiration):
    '''Check to see if the given entry has expired (relative to current time).'''
    diff = U.current_time_millis() - entry["timestamp"]
    return expiration >= 0 and diff > expiration
   
   
def tags_match(e1, e2):
    '''Determine if a pair of tag+subtag's match.'''
    return e1["tag"] == e2["tag"] and e1["subtag"] == e2["subtag"]
        
        
        

### singleton global Cacher object with accessor function
    
__DEFAULT_CACHER = Cacher()

def default_cacher():
    '''Return the default global Cacher object.'''
    global __DEFAULT_CACHER
    return __DEFAULT_CACHER
    
