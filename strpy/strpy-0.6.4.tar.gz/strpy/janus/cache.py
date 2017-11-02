#--------------------------------------------------------------------------
#
# Copyright (c) 2014 Systems and Technology Research 
#
#--------------------------------------------------------------------------

import os
import shutil
import hashlib
import inspect
import tempfile

from strpy.bobo.util import remkdir, isfile, fileext, quietprint, isnumpy, isimageobject
import cPickle as pickle
import gc


def _save(obj, pklfile):
    gc.disable()         
    pickle.dump(obj, open(pklfile, 'wb'), pickle.HIGHEST_PROTOCOL)
    gc.enable()
    return pklfile
    
def _load(pklfile):
    gc.disable()
    obj = pickle.load(open(pklfile, 'rb'))
    gc.enable()
    return obj
        
def root():
    #JANUS_CACHE = os.environ.get('JANUS_CACHE')
    JANUS_CACHE = None
    if JANUS_CACHE is None:
        JANUS_CACHE = remkdir(os.path.join(tempfile.gettempdir(), 'janustr'))  # must be a fast local drive 
    remkdir(JANUS_CACHE)
    return JANUS_CACHE
    
def _funchash(f, x):
    """This function is designed for lambda functions (f) with arguments numpy objects x or bobo.image objects"""
    fhash = hashlib.md5()
    f_repr = str(inspect.getsource(f))
    fhash.update(f_repr)
    if isnumpy(x):
        x_repr = hashlib.md5(x).hexdigest()
        fhash.update(x_repr)
    elif isimageobject(x):
        # Janus platform image object defined in bobo.image or bobo.video
        x_repr = x.__repr__()
        fhash.update(hashlib.md5(x_repr).hexdigest())                
    elif type(x) is list or type(x) is tuple:
        if isimageobject(x[0]):
            x_repr = []
            for im in x:
                x_repr.append(im.__repr__())
                fhash.update(hashlib.md5(im.__repr__()).hexdigest())
        else:
            raise NotImplementedError('List of objects of type "%s" not supported for caching' % type(x[0]))            
    elif type(x) is int or float:
        x_repr = str(x)
        fhash.update(hashlib.md5(x_repr).hexdigest())                
    else:
        # WARNING: this assumes that the str(x) encodes some unique identifiable information about the argument, such as provided in __repr__() method of janus.image.Image!
        # WARNING: there may be cache collisions if this assumption is not satisfied!
        raise NotImplementedError('Object type "%s" not supported for caching' % type(x))

    return {'hash':fhash.hexdigest(), 'f':f_repr, 'x':x_repr}

def _cachefile(f,x):
    """Return the absolute path in the cached file"""
    return os.path.join(root(), '%s.pkl' % _funchash(f,x)['hash'])

def _hit(f, x):
    """Return unpicked python object if function is in cache"""
    h = _funchash(f,x)
    filename = os.path.join(root(), '%s.pkl' % h['hash'])
    if isfile(filename):
        quietprint('[janus.cache][HIT]: loading object from "%s" for function="%s", x="%s" ' % (filename, h['f'].rstrip('\n').lstrip(), h['x']))
        try:
            return _load(filename)
        except:
            quietprint('[janus.cache][HIT]: error loading cache file "%s".  Discarding... ' % filename)                        
            return None
    else:
        return None
    
def _miss(f, x):
    """Return evaluated function, and save pickled numpy object in cache"""
    h = _funchash(f,x)    
    filename = os.path.join(root(), '%s.pkl' % h['hash'])
    quietprint('[janus.cache][MISS]: evaluating function="%s", x="%s" and caching to "%s" ' % (h['f'].rstrip('\n').lstrip(), h['x'], filename))

    # store y in cache
    y = f(x)
    try:
        _save(y, filename)
    except:
        quietprint('[janus.cache][MISS]: error saving cache file "%s".  Skipping...' % filename)        
    return y

def _fetch(f, x):
    """Return the cached evaluation of f(x), or evaluate f(x) and store in cache"""
    y = _hit(f,x)
    y = _miss(f,x) if y is None else y
    return y

def _flush(f, x):
    filename = _cachefile(f,x)
    if isfile(filename):
        os.remove(filename)
    return f(x)

def clear(f):
    """Delete the entire cache"""
    shutil.rmtree(root())
    remkdir(root())
    
def preserve(f):
    """Return a function that wraps the provided lambda function to cache results"""
    """This function will preserve the results of the function evaluation across spark runs"""
    return (lambda x: _fetch(f, x))

def flush(f):
    return (lambda x: _flush(f, x))

def saveas(f, x, filename):
    """Save results of f(x) to the given filename"""
    y = _fetch(f,x) 
    if fileext(filename) is '.mat':
        bobo.util.savemat(filename, {'var':y})
    else:
        shutil.copyfile(_cachefile(f,x), filename)
    return filename
         

