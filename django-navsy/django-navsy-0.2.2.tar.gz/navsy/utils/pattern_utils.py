# -*- coding: utf-8 -*-

from navsy.utils import path_utils

import re


__default_regexs = [

    # <blank>
    "",

    # <date_day>
    "(?P<date_day>((0|1|2)?([1-9])|[1-3]0|31))",

    # <date_month>
    "(?P<date_month>(0?([1-9])|10|11|12))",

    # <date_year>
    "(?P<date_year>[\d]{4})",

    # <date_year><date_month>
    "(?P<date_year>[\d]{4})(?P<date_month>(0?([1-9])|10|11|12))",

    # <date_year><date_month><date_day>
    "(?P<date_year>[\d]{4})(?P<date_month>(0?([1-9])|10|11|12))(?P<date_day>((0|1|2)?([1-9])|[1-3]0|31))",

    # <date_year>-<date_month>-<date_day>
    "(?P<date_year>[\d]{4})-(?P<date_month>(0?([1-9])|10|11|12))-(?P<date_day>((0|1|2)?([1-9])|[1-3]0|31))",

    # <date_year>/<date_month>
    "(?P<date_year>[\d]{4})/(?P<date_month>(0?([1-9])|10|11|12))",

    # <date_year>/<date_month>/<date_day>
    "(?P<date_year>[\d]{4})/(?P<date_month>(0?([1-9])|10|11|12))/(?P<date_day>((0|1|2)?([1-9])|[1-3]0|31))",

    # <email>
    "(?P<email>(([a-z\d]+([\.\_]{1}[a-z\d]+)?){6})\@([a-z\d]+([\.\_\-]{1}[a-z\d]+){1,}[a-z]+))",

    # <email_username>@<email_domain>
    "(?P<email_username>([a-z\d]+([\.\_]{1}[a-z\d]+)?){6})\@(?P<email_domain>[a-z\d]+([\.\_\-]{1}[a-z\d]+){1,}[a-z]+)",

    # <file_name>.<file_ext>
    "(?P<file_name>[\w-]+).(?P<file_ext>[\w]+)",

    # <id>
    "(?P<id>[\d]+)",

    # <id>/<slug>
    "(?P<id>[\d]+)/(?P<slug>[\w-]+)",

    # <page>
    "(?P<page>[\d]+)",

    # <slug>
    "(?P<slug>[\w-]+)",

    # <slug_parent>/<slug>
    "(?P<slug_parent>[\w-]+)/(?P<slug>[\w-]+)",

    # <username>
    "(?P<username>[\w.@-]+)",

    # <uuid>
    "(?P<uuid>[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[1345][a-fA-F0-9]{3}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12})",

    # <version>
    "(?P<version>[\d]+(\.[\d]+)+)",

    # <version_major>.<version_minor>
    "(?P<version_major>[\d]+)\.(?P<version_minor>[\d]+)",

    # <version_major>.<version_minor>.<version_build>
    "(?P<version_major>[\d]+)\.(?P<version_minor>[\d]+)\.(?P<version_build>[\d]+)",

    # by-<slug>
    "by-(?P<slug>[\w-]+)",

    # login
    "login",

    # logout
    "logout",
]


def get_default_regexs():
    return list(__default_regexs)


REGEX_DISPLAY_RE = re.compile(
    r'^([\w\-]+)((\.[\w]+)?)+|(\<\w+\>)|([\w\-\_\.\@\/]*)\(\?P|([\w\-]+)$')

# ([\w\-]+)                 prefix
# ((\.[\w]+)?)+             extensions
# (\<\w+\>)                 parameter
# ([\w\-\_\.\@\/]*)\(\?P    parameters conjunction
# ([\w\-]+)                 suffix


def get_regex_display(regex):

    if not regex:
        return '<blank>'

    matches = REGEX_DISPLAY_RE.findall(regex)
    # print(matches)

    s = ''

    for m in matches:
        for i in m:
            if i:
                s += str(i)
    return s


def get_regex_format(regex):

    if not regex:
        return ''

    s = get_regex_display(regex)
    s = s.replace('<', '{')
    s = s.replace('>', '}')
    return s


def get_regex_re(base_url, regex):

    path = path_utils.fix_path(base_url, regex)
    if path.endswith('/'):
        pattern = r'^%s/?$' % path[0:-1]
    else:
        pattern = r'^%s$' % path
    obj = re.compile(pattern)
    return obj
