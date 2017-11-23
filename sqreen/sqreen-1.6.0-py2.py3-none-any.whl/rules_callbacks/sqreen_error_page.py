# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Base custom error page
"""
from os.path import dirname, join

from ..rules import RuleCallback


class BaseSqreenErrorPage(RuleCallback):

    def __init__(self, *args, **kwargs):
        super(BaseSqreenErrorPage, self).__init__(*args, **kwargs)
        with open(join(dirname(__file__), 'sqreen_error_page.html')) as f:
            self.content = f.read()

        rule_data = self.data["values"][0]
        self.rule_type = rule_data["type"]

        if self.rule_type == 'custom_error_page':
            self.status_code = int(rule_data['status_code'])
        elif self.rule_type == 'redirection':
            self.redirection_url = rule_data['redirection_url']
        else:
            raise ValueError("Invalid rule_type %s" % self.rule_type)

    def pre(self, original, *args, **kwargs):
        exception = self._get_exception(*args, **kwargs)

        if exception:
            if self.rule_type == 'custom_error_page':
                response = self._get_response(exception, self.content, self.status_code)
            elif self.rule_type == 'redirection':
                headers = {'Location': self.redirection_url}
                response = self._get_response(exception, "", 303, headers)

            return {"status": "override", "new_return_value": response}
