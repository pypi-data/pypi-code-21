# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
from .rules import PRED, RESULT_CODE, RESULT_REASON

logger = logging.getLogger(name=__name__)


class ReviewResponse(object):
    response = None
    status_code = None
    reason = None
    rules = None

    def __init__(self, resp, rules=None):
        # could be a requests.response or a MagicMock
        if not hasattr(resp, "status_code"):
            raise ValueError(
                "ReviewResponse only works with requests.Response")

        # allow for override ruleset
        if rules:
            self.rules = rules
        else:
            from .rules import rules as rules_
            self.rules = rules_

        self.response = resp
        self.review()

    def review(self):
        for rule in self.rules:
            logger.debug(rule)
            res = rule[PRED](self.response)
            logger.debug("RESULT: {}".format(res))

            if res:
                self.status_code = rule[RESULT_CODE]
                self.reason = rule[RESULT_REASON]
                logger.debug("MATCHED: status_code: {}, reason{}".format(
                    self.status_code, self.reason))
                break

        else:
            # no rule match, return as per requests response
            self.status_code = self.response.status_code

        return self

    @property
    def updated(self):
        return self.reason is not None

    def __unicode__(self):
        return "Code: {}, reason: {}".format(self.status_code, self.reason)


def review_response(resp, rules=None):
    """
    Reviews a requests' response object to be analysed according to a ruleset.

    Args:
        resp: requests' response.
        rules: optionally pass a custom ruleset to process with. Default:
            build-in ruleset.

    Returns:
        A ReviewResponse object, containing:
            .response: the original requests' response object passed in.
            .status_code: the "corrected" HTTP code. Will be the same as the
                original request if no corrections were made, or will be a new
                value if updated.
            .reason: if defined, the code has been updated, and this string
                explains why (i.e. which rule it matched).
            .rules: the ruleset being used, either default or custom.
    """
    revresp = ReviewResponse(resp, rules=rules)

    return revresp
