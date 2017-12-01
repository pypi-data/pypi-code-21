import re, math

import datetime
from enum import Enum

CONNECTION_TIMEOUT_PAUSE = 60

def clean_for_kairos(s):
    """
    Simple kairos parser utility funcion for insert

    :param s: a simple string value to insert in kairos
    :type s: string
    :return: value string parsed ready to insert in kairos
    """
    removelist = r'[^A-Za-z0-9./_-]'
    return re.sub(removelist,"", s)



class SuffixNameFrecuency(Enum):
    """ Index type supported
    the handler supports
    - Daily indices
    - Weekly indices
    - Monthly indices
    - Year indices
    """
    DAILY = 0
    MONTHLY = 2
    YEARLY = 3
    NONE = 5


def _get_daily_suffix_name(date):
    """ Returns elasticearch index name
    :param: index_name the prefix to be used in the index
    :return: A srting containing the elasticsearch indexname used which should include the date.
    """
    return "{0!s}".format(date.strftime('%Y.%m.%d'))



def _get_monthly_suffix_name(date):
    """ Return elasticsearch index name
    :param: index_name the prefix to be used in the index
    :return: A srting containing the elasticsearch indexname used which should include the date and specific moth
    """
    return "{0!s}".format(date.strftime('%Y.%m'))


def _get_yearly_suffix_name(date):
    """ Return elasticsearch index name
    :param: index_name the prefix to be used in the index
    :return: A srting containing the elasticsearch indexname used which should include the date and specific year
    """
    return "{0!s}".format(date.strftime('%Y'))

def _get_none_suffix_name(es_suffix_name):
    """ Return elasticsearch index name
    :param: index_name the prefix to be used in the index
    :return: A srting containing the elasticsearch indexname used which should include the date and specific year
    """
    return None

_SUFFIX_FRECUENCY_FUNCION_DICT = {
    SuffixNameFrecuency.DAILY: _get_daily_suffix_name,
    SuffixNameFrecuency.MONTHLY: _get_monthly_suffix_name,
    SuffixNameFrecuency.YEARLY: _get_yearly_suffix_name,
    SuffixNameFrecuency.NONE: _get_none_suffix_name
}


