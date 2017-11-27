import requests

BASE_URL = "https://api.spacexdata.com"


def route_builder(version: str, method: str, route: str):
    """Builds a URL using the data given.
    
    Parameters
    ----------
    version: str
        The version that the request is for.
    method: str
        The method that the request is for.
    route: str
        The route that the request is for.
        
    Returns
    -------
    str
        The built URL.
    """
    url = "{base}/{version}/{method}/{route}".format(base=BASE_URL, version=version, method=method, route=route)

    return url


def raw_request(url: str):
    """Handles a raw request using only a URL.
    
    Parameters
    ----------
    url: str
        The URL of the request to make.
        
    Returns
    -------
    dict
        The JSON response dictionary.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()


def request(version: str, method: str, route: str, **kwargs):
    """Performs a request using the provided route builder.
    
    Parameters
    ----------
    version: str
        The version that the request is for.
    method: str
        The method that the request is for.
    route: str
        The route that the request is for.
    kwargs: any
        Any additional data to pass along to the API.
        
    Returns
    -------
    dict:
        The JSON response dictionary.
    """
    url = route_builder(version, method, route)
    response = requests.get(url, params=kwargs)
    if response.status_code == 200:
        return response.json()
