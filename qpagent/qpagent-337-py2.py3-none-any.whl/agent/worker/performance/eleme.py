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
            # next_step = self.uiHelper.find_element("me.ele:id/agl")
            # next_step.click()
            # permission_allow_button = self.uiHelper.find_element("com.android.packageinstaller:id/permission_allow_button")
            # permission_allow_button.click()
            # permission_allow_button = self.uiHelper.find_element(
            #     "com.android.packageinstaller:id/permission_allow_button")
            # permission_allow_button.click()
            # permission_allow_button = self.uiHelper.find_element(
            #     "com.android.packageinstaller:id/permission_allow_button")
            # permission_allow_button.click()
            # self.uiHelper.find_element(
            #     "me.ele:id/a2p").click()
            # self.uiHelper.find_element(
            #     "me.ele:id/a5h").click()
            # self.uiHelper.find_element(
            #     "me.ele:id/arb").click()
            # self.uiHelper.find_element_by_ui_automator('new UiSelector().text("密码登录")').click()
            # name = self.uiHelper.find_element_by_ui_automator('new UiSelector().text("手机/邮箱/用户名")')
            # name.click()
            # name.send_keys('13200001111')
            # password = self.uiHelper.find_element_by_ui_automator('new UiSelector().text("密码")')
            # password.click()
            # password.send_keys('911028')
            # self.uiHelper.find_element(
            #     "me.ele:id/a7k").click()
            self.uiHelper.find_element_by_ui_automator(
                'new UiSelector().resourceId("com.tencent.wstt.gt:id/selected_app_bg")').click()
            self.uiHelper.wait_for_element(u'饿了么', 10)
            self.uiHelper.find_element(u'饿了么').click()
            self.uiHelper.get_driver().wait_activity('com.tencent.wstt.gt.activity.GTMainActivity', 10, 1)

        finally:
            if self.uiHelper is not None:
                self.uiHelper.quit_driver()


if __name__ == '__main__':
    eleme = ElemeSpecialTest()
    eleme.test_login()
