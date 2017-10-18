"""Main code.

Use python library for connect in Quotes API.

CHALLENGE_URL = URL for connection
MIN_QUOTE = minimum number for API GET
MAX_QUOTE = maximum number for API GET
TIMEOUT = timeout in seconds for connection
"""
try:
    from urllib2 import urlopen as connection
    from urllib2 import URLError
except ImportError:
    from urllib.request import urlopen as connection
    from urllib.error import URLError
import json
import sys
import random


CHALLENGE_URL = 'https://1c22eh3aj8.execute-api.us-east-1.' \
    'amazonaws.com/challenge/quotes{}'

MIN_QUOTE = 0
MAX_QUOTE = 18

TIMEOUT = 2


def _get(quote_number=None):
    try:
        if quote_number is not None:
            url = CHALLENGE_URL.format("/" + str(quote_number))
            key = "quote"
        else:
            url = CHALLENGE_URL.format("")
            key = "quotes"

        response = connection(url, timeout=TIMEOUT)
        raw_data = response.read()
        decoded_data = raw_data.decode("utf-8")
        data = json.loads(decoded_data)

        result = True
        message = data.get(key)

    except URLError as error:
        result = False
        message = error.reason

    except Exception as error:
        result = False
        message = sys.exc_info()[0]

    return (result, message)


def get_quote(quote_number):
    """Function: get_quote.

    Summary: Check number and start connection
    Examples: get_quote(11)

    Attributes
    ----------
        @param (quote_number):Integer between MIN_QUOTE and MAX_QUOTE

    Returns
    -------
        Tuple:
        Bool - Successful operation
        String - Data from connection

    """
    try:
        quote_number = int(quote_number)
    except ValueError:
        return (False, "Can't convert data to string")

    if quote_number < MIN_QUOTE or quote_number > MAX_QUOTE:
        return (False, "Invalid range for seed. Choose {} to {}.".format(
            MIN_QUOTE, MAX_QUOTE))

    ret, msg = _get(quote_number)
    return (ret, msg)


def get_random_quote():
    """Function: get_random_quote.

    Summary: Start connection with random number

    Returns
    -------
        Tuple:
        Bool - Successful operation
        String - Data from connection

    """
    random_seed = random.randint(MIN_QUOTE, MAX_QUOTE)
    ret, msg = _get(random_seed)
    return (ret, msg)


def get_quotes():
    """Function: get_quotes.

    Summary: Get all quotes from connection

    Returns
    -------
        Tuple:
        Bool - Successful operation
        List - String list from connection

    """
    ret, msg = _get()
    return (ret, msg)
