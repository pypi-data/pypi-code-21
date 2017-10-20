import requests

from russell.exceptions import RussellException
from base64 import b64encode
from russell.cli.utils import getPythonVersion

def get_url_contents(url):
    """
    Downloads the content of the url and returns it
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.content.decode('utf-8')
    else:
        raise RussellException("Failed to get contents of the url : {}".format(url))


def get_basic_token(access_token):
        return b64encode("{}:".format(access_token).encode()).decode("ascii")