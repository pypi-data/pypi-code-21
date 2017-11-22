#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ibotcloud import ask

APP_KEY = 'mjjmBCLHyjeo'
SECRET = '5OI4lJr5zwgQFHuZhWXR'


class TestAsk(unittest.TestCase):

    def test_execute(self):
        req = ask.Request(APP_KEY, SECRET)
        question = '天王盖地虎'
        print('Q:', question)
        answer = req.execute(question)
        print('A:', answer)
        self.assertTrue(answer)
