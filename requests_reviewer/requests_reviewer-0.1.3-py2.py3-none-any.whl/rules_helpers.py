# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(name=__name__)


def match_content(r, target_str):
    logger.debug(u"Trying content matching: {} in {}"
                 .format(target_str, r.text))
    result = r.text.lower().find(target_str.lower())
    logger.debug("Content matching result: {}, so {}".format(
        result, result >= 0))
    return result >= 0


def match_url(r, url_str):
    logger.debug(u"Trying URL matching: {} in {}".format(url_str, r.url))
    return r.url.find(url_str) >= 0


def match_header(r, header_name, header_val):
    logger.debug(u"Trying HTTP header matching: {}: {} in {}".format(
        header_name, header_val, r.headers))

    # request uses CaseInsensitiveDict
    try:
        return r.headers[header_name].find(header_val) >= 0
    except:
        return False


def match_exact_header(r, header_name, header_val):
    logger.debug(u"Trying HTTP header exact matching: {}: {} in {}".format(
        header_name, header_val, r.headers))

    try:
        return r.headers[header_name] == header_val
    except:
        return False
