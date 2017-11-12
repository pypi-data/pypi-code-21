# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from .rules_helpers import match_header, match_url

NAME = "name"
PRED = "pred"
RESULT_CODE = "code"
RESULT_REASON = "result"


# NOTE: these are applied from top to bottom. Very specific rules should be
# at top, generic towards bottom.
rules = [
    {
        NAME: "CSIRT Foundry test URL",
        PRED: lambda r: (match_url(
            r, "http://csirtfoundry.com/google874661cb60d0dc39.html")),
        RESULT_CODE: 403,
        RESULT_REASON: "Testing URL, recording as down"
    },
    {
        NAME: "suspended page cgi",
        PRED: lambda r: (match_header(r, "Location", "/suspendedpage.cgi")),
        RESULT_CODE:  403,
        RESULT_REASON: "Common suspension URL",
    },
]
