#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function, absolute_import

import unittest
import os

from ibotcloud import ask

APP_KEY = os.environ['APP_KEY']
APP_SECRET = os.environ['APP_SECRET']


class TestAsk(unittest.TestCase):

    def test_execute(self):

        req = ask.Request(APP_KEY, APP_SECRET)
        question = '这个周末北京的天气?'
        print('Q:', question)
        answer = req.execute(question, response_type=ask.ResponseType.advanced)
        print('A:', answer)
        self.assertTrue(answer)
