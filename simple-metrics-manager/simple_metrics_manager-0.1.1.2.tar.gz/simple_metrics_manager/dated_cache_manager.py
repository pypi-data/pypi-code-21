import time
from human_time_formatter import format_seconds

_DATE = '_date'

def today():
    return time.strftime('%Y-%m-%d')

class DatedCacheManager(object):
    def __init__(self, storage_interface):
        '''An object that contains:
           * functions needed to compute each metric
           * in-memory copy of a set of the metrics
           * a storage interface to save and load metrics from disk (or something else)
           '''
        self.functions_dict = {}
        self.cache = {}
        self.storage_interface = storage_interface
    
    def set_functions_dict(self, functions_dict):
        self.functions_dict = functions_dict
    
    def exists(self, name):
        return (self.storage_interface.exists(name) and
                self.storage_interface.exists(name + _DATE))
    
    def compute(self, name, force=False, verbose=True):
        if force or name not in self.cache:
            if name not in self.functions_dict:
                raise ValueError('{} does not have a compute function defined!'.format(name))
            if verbose:
                print 'Compute {}'.format(name)
            t = time.time()
            self.cache[name] = self.functions_dict[name]()
            if verbose:
                print 'Completed {} in {}'.format(name, format_seconds(time.time() - t, ndigits=6))
            
        return self.cache[name]
    
    def _save(self, name, data, verbose=True):
        '''Save data as the name metric (and today's date in a sidecar)'''
        if verbose:
            print 'Save {}'.format(name)
        self.storage_interface.save(name, data)
        self.storage_interface.save(name + _DATE, today())
    
    def save(self, name, force=False, verbose=True):
        '''Save the name metric
           Does nothing if there is a previous save and force is False'''
        if force or not self.exists(name):
            v = self.compute(name, force, verbose)
            self._save(name, v, verbose)
        
    def _load(self, name, verbose=True):
        '''Load the stored value into the in-memory cache'''
        self.cache[name + _DATE] = self.storage_interface.load(name + _DATE)
        if verbose:
            print 'Load {} pulled on {}'.format(name, self.cache[name + _DATE])
        self.cache[name] = self.storage_interface.load(name)
    
    def load(self, name, force=False, verbose=True):
        '''Load the name metric and return the value
           Does not reload if the value is in cache and force is False'''
        if force or name not in self.cache:
            self._load(name, verbose)
        return self.cache[name]
    
    def get(self, name, use_stored=True, verbose=True):
        '''Make sure a metric is saved to disk and loaded into memory,
           then return the value
           Only computes+saves/ reloads when needed (or if force is True)'''
        force = not use_stored
        self.save(name, force, verbose)
        return self.load(name, force, verbose)
    
    def clear_cache(self):
        for k in self.cache.keys():
            del self.cache[k]
    
    def __getitem__(self, key):
        return self.get(key)
