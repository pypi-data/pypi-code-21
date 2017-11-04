
import base64
import sys
from subprocess import Popen, PIPE

if sys.version_info >= (3, 0):
    from urllib.parse import urlsplit, urlunsplit
elif sys.version_info < (3, 0):
    from urlparse import urlsplit, urlunsplit

from .exceptions import EmissionBadParameter
from .specifications import TORRENT_ARGUMENTS


def open_transmission():

    app_path = "/Applications/transmission.app"
    p = Popen(["/usr/bin/open", app_path], stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()

########################
##### HTTP HELPERS #####
########################


def to_http(url):
    """
    change url's scheme
        >>> url = 'https://www.google.fr'
        >>> url = to_http(url)
        >>> http://www.google.fr
    """
    t_url = list(urlsplit(url))
    if t_url[0] == 'http' or t_url[0] == 'file':
        return url

    t_url[0] = 'http'
    new_url = urlunsplit(t_url)
    return new_url


def decoder(content):
    """
    All text MUST be UTF-8 encoded
    """
    torrent_data = base64.b64encode(content).decode('utf-8')
    return torrent_data


###########################
##### TORRENT HELPERS #####
###########################

def check_ids(ids):

    if not (isinstance(ids, int) or isinstance(ids, list) or isinstance(ids, str)):
        raise EmissionBadParameter('ids shoul be a int, list or string')

    if isinstance(ids, list):
        for v in ids:
            if isinstance(v, float):
                raise EmissionBadParameter('ids shoul not be a float')

    return ids


def to_dash(s):
    """
        >>> to_dash('delete_local_data')
        >>> delete-local-data
    """
    return s.replace('_', '-')


def from_dash(s):
    """
        >>> from_dash('delete-local-data')
        >>> delete_local_data
    """
    return s.replace('-', '_')


def check_method(method):

    if method not in TORRENT_ARGUMENTS.keys():
        raise EmissionBadParameter("'{0}' method does not exist".format(method))


def get_arguments_from_method(method):

    return TORRENT_ARGUMENTS[method]


def check_fields(method, args):

    def check_name(name, arguments):
        if name not in arguments.keys():
            raise EmissionBadParameter("'{0}' is not a valid argument".format(name))

    specs = get_arguments_from_method(method)

    for elt in args:
        check_name(elt, specs)


def check_arguments(method, args):

    def check_name(name, arguments):
        if name not in arguments.keys():
            raise EmissionBadParameter("'{0}' is not a valid argument".format(name))

    def check_value(name, value, arguments):
        if not isinstance(value, arguments[name][0]):
            raise EmissionBadParameter("'{0}' is not a valid value".format(value))

    specs = get_arguments_from_method(method)

    for elt in args:
        check_name(elt[0], specs)
        check_value(elt[0], elt[1], specs)

###############################################


def normalize_fields_arguments(method, args):

    check_method(method)

    # change '_' to '-'
    fields = [to_dash(k) for k in args]

    check_fields(method, fields)

    return fields


def normalize_arguments(method, kwargs):

    check_method(method)

    # change '_' to '-'
    options = [(to_dash(k), v) for k, v in kwargs.items()]

    # verify if the argument is valid
    check_arguments(method, options)

    return options
