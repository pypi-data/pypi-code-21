#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.worker.performance.eleme
    ~~~~~~~~~~~~

    This module provide the eleme special test.

    :copyright: (c) 2017 by Ma Fei.
"""
from agent.util.uihelper import UiHelper


class ElemeSpecialTest(object):
    def __init__(self):
        self.uiHelper = UiHelper("deviceConfig.txt")
        self.uiHelper.init_driver()

    def test_login(self):
        try:
            next_step = self.uiHelper.find_element("me.ele:id/agl")
            next_step.click()
            permission_allow_button = self.uiHelper.find_element("com.android.packageinstaller:id/permission_allow_button")
            permission_allow_button.click()
            permission_allow_button = self.uiHelper.find_element(
                "com.android.packageinstaller:id/permission_allow_button")
            permission_allow_button.click()
            permission_allow_button = self.uiHelper.find_element(
                "com.android.packageinstaller:id/permission_allow_button")
            permission_allow_button.click()

        finally:
            if self.uiHelper is not None:
                self.uiHelper.quit_driver()


if __name__ == '__main__':
    eleme = ElemeSpecialTest()
    eleme.test_login()
