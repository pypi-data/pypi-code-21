#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from agent.util.appetizerkit import AppToolKit

app_tool_kit = AppToolKit()


class TestAppToolKit(unittest.TestCase):
    def test_get_android_devices(self):
        print(app_tool_kit.get_android_devices())
        self.assertIsNotNone(app_tool_kit.get_android_devices())

    def test_get_ios_devices(self):
        print(app_tool_kit.get_ios_devices())
        self.assertIsNotNone(app_tool_kit.get_ios_devices())


if __name__ == '__main__':
    unittest.main()
