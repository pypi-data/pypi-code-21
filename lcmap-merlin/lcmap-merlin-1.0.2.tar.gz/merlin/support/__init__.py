import os

CWD = os.path.dirname(os.path.realpath(__file__))

def chip_spec_queries(url):
    '''A map of pyccd spectra to chip-spec queries

    Args:
        url (str): full url (http://host:port/resource) for chip-spec endpoint

    Returns:
        dict: map of spectra to chip spec queries

    Example:
    
    >>> chip_spec_queries('http://host/v1/landsat/chip-specs')
    {'reds':     'http://host/v1/landsat/chip-specs?q=tags:red AND sr',
     'greens':   'http://host/v1/landsat/chip-specs?q=tags:green AND sr'
     'blues':    'http://host/v1/landsat/chip-specs?q=tags:blue AND sr'
     'nirs':     'http://host/v1/landsat/chip-specs?q=tags:nir AND sr'
     'swir1s':   'http://host/v1/landsat/chip-specs?q=tags:swir1 AND sr'
     'swir2s':   'http://host/v1/landsat/chip-specs?q=tags:swir2 AND sr'
     'thermals': 'http://host/v1/landsat/chip-specs?q=tags:thermal AND ta'
     'quality':  'http://host/v1/landsat/chip-specs?q=tags:pixelqa'}
    '''

    return {'reds':     ''.join([url, '?q=tags:red AND sr']),
            'greens':   ''.join([url, '?q=tags:green AND sr']),
            'blues':    ''.join([url, '?q=tags:blue AND sr']),
            'nirs':     ''.join([url, '?q=tags:nir AND sr']),
            'swir1s':   ''.join([url, '?q=tags:swir1 AND sr']),
            'swir2s':   ''.join([url, '?q=tags:swir2 AND sr']),
            'thermals': ''.join([url, '?q=tags:bt AND thermal AND NOT tirs2']),
            'quality':  ''.join([url, '?q=tags:pixelqa'])}


def data_config():
    '''Default configuration for retrieving and serving test data

    Returns:
        dict: x, y, acquired, dataset_name, chips_dir, specs_dir
    '''

    return {'x': -1821585,
            'y': 2891595,
            'acquired': '2012-01-01/2014-12-12',
            'dataset_name': 'ARD',
            'chips_dir': os.path.join(CWD, 'data/chips'),
            'specs_dir': os.path.join(CWD, 'data/specs')}
