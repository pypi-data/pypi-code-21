# -*- coding: utf-8 -*-
"""
    agent.util.uihelper
    ~~~~~~~~~~~~

    This module provide the appium ui helper.

    :copyright: (c) 2017 by Ma Fei.
"""
import os
from time import sleep

from appium import webdriver
from enum import Enum

# Returns abs path relative to this file and not cwd
PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

"""
Connection types are specified here:
    https://code.google.com/p/selenium/source/browse/spec-draft.md?repo=mobile#120
    Value (Alias)      | Data | Wifi | Airplane Mode
    -------------------------------------------------
    0 (None)           | 0    | 0    | 0
    1 (Airplane Mode)  | 0    | 0    | 1
    2 (Wifi only)      | 0    | 1    | 0
    4 (Data only)      | 1    | 0    | 0
    6 (All network on) | 1    | 1    | 0
"""


class ConnectionType(Enum):
    NO_CONNECTION = 0
    AIRPLANE_MODE = 1
    WIFI_ONLY = 2
    DATA_ONLY = 4
    ALL_NETWORK_ON = 6


class UiHelper:
    remoteHost = "http://127.0.0.1:4723/wd/hub"

    def __init__(self, configPath):
        self.desired_caps = {}
        self._driver = None
        file_object = open(configPath)
        try:
            for line in file_object:
                if line.startswith("#"):
                    continue

                line = line.strip()
                words = line.split("=")
                if len(words) != 2:
                    continue

                if words[0] == 'app':
                    self.desired_caps[words[0]] = PATH(words[1])
                elif words[0] == 'remoteHost':
                    self.remoteHost = words[1]
                else:
                    self.desired_caps[words[0]] = words[1]
        finally:
            file_object.close()

    def init_driver(self):
        self._driver = webdriver.Remote(self.remoteHost, self.desired_caps)

    def quit_driver(self):
        if self._driver:
            self._driver.quit()

    """
    给定控件的xpatch, id 或者name来查找控件

    :Args:
         - controlInfo: 控件的信息，可以是xpath,id或者其他属性

    :Return:
        如果找到控件，返回第一个

    :Usage:
        self.findElement(controlInfo)
    """

    def find_element(self, controlInfo):
        element = ""
        if controlInfo.startswith("//"):
            element = self._driver.find_element_by_xpath(controlInfo)
        elif ":id/" in controlInfo or ":string/" in controlInfo:
            element = self._driver.find_element_by_id(controlInfo)
        else:
            # 剩下的字符串没有特点，无法区分，因此先尝试通过名称查找
            try:
                element = self._driver.find_element_by_name(controlInfo)
            except Exception:
                # 如果通过名称不能找到则通过class name查找
                element = self._driver.find_element_by_class_name(controlInfo)

        return element

    """
    给定控件的xpatch, id 或者name来查找控件

    :Args:
         - controlInfo: 控件的信息，可以是xpath,id或者其他属性

    :Return:
        返回所有满足条件的控件，返回的类型是一个列表

    :Usage:
        self.findElements(controlInfo)
    """

    def find_elements(self, controlInfo):
        elements = ""
        if controlInfo.startswith("//"):
            elements = self._driver.find_elements_by_xpath(controlInfo)
        elif ":id/" in controlInfo:
            elements = self._driver.find_elements_by_id(controlInfo)
        else:
            elements = self._driver.find_elements_by_name(controlInfo)
            if len(elements) == 0:
                elements = self._driver.find_elements_by_class_name(controlInfo)

        return elements

    """
    在一个已知的控件中通过给定控件的xpatch, id 或者name来查找子控件

    :Args:
        - parentElement: 父控件，是一个已知的WebElement
        - childElementInfo: 子控件的信息，可以是xpath,id或者其他属性

    :Return:
        如果找到控件，返回第一个

    :Usage:
        self.findElement(controlInfo)
    """

    @staticmethod
    def find_element_in_parent_element(parentElement, childElementInfo):
        element = ""
        if childElementInfo.startswith("//"):
            element = parentElement.find_element_by_xpath(childElementInfo)
        elif ":id/" in childElementInfo:
            element = parentElement.find_element_by_id(childElementInfo)
        else:
            # 剩下的字符串没有特点，无法区分，因此先尝试通过名称查找
            try:
                element = parentElement.find_element_by_name(childElementInfo)
            except:
                # 如果通过名称不能找到则通过class name查找
                element = parentElement.find_element_by_class_name(childElementInfo)

        return element

    """
    在一个已知的控件中通过给定控件的xpatch, id 或者name来查找子控件

    :Args:
        - parentElement: 父控件，是一个已知的WebElement
        - childElementInfo: 子控件的信息，可以是xpath,id或者其他属性

    :Return:
        如果找到控件，返回所有符合条件的控件

    :Usage:
        self.findElementsInParentElement(parentElement, controlInfo)
    """

    @staticmethod
    def find_elements_in_parent_element(parentElement, childElementInfo):
        elements = ""
        if childElementInfo.startswith("//"):
            elements = parentElement.find_elements_by_xpath(childElementInfo)
        elif ":id/" in childElementInfo:
            elements = parentElement.find_elements_by_id(childElementInfo)
        else:
            # 剩下的字符串没有特点，无法区分，因此先尝试通过名称查找
            elements = parentElement.find_elements_by_name(childElementInfo)
            if len(elements) == 0:
                # 如果通过名称不能找到则通过class name查找
                elements = parentElement.find_elements_by_class_name(childElementInfo)

        return elements

    """
    通过UIAutomator的uia_string来查找控件

    :Args:
        -uia_string: UiSelector相关的代码，参考http://developer.android.com/
        tools/help/uiautomator/UiSelector.html#fromParent%28com.android.uiautomator.core.UiSelector%29

    :Return:
        -找到的控件

    :usage:
        self.findElementByUIAutomator(new UiSelector().(android.widget.LinearLayout))
    """

    def find_element_by_ui_automator(self, uia_string):
        return self._driver.find_element_by_android_uiautomator(uia_string)

    """
    滑动操作

    :Args:
         - x1,y1,x2,y2： 滑动操作的起点和终点的坐标

    :Usage:
        self.swipe(50, 50, 400, 400)
    """

    def flick(self, x1, y1, x2, y2):
        self._driver.flick(x1, y1, x2, y2)

    """
    滑动操作

    :Args:
         - x1,y1,x2,y2： 滑动操作的起点和终点的坐标
         - peroid: 多长时间内完成该操作,单位是毫秒

    :Usage:
        self.swipe(50, 50, 400, 400, 500)
    """

    def swipe(self, x1, y1, x2, y2, peroid):
        self._driver.swipe(x1, y1, x2, y2, peroid)

    def tap(self, x, y):
        self._driver.tap([(x, y)])

    """
    长按点击操作
    :Args:
     - x,y： 长按点的坐标
     - peroid: 多长时间内完成该操作,单位是毫秒

    :Usage:
        self.longPress(50, 50, 500)
    """

    def long_press(self, x, y, peroid):
        self._driver.tap([(x, y)], peroid)

    """
    点击某一个控件，如果改控件不存在则会抛出异常

    :Args:
         - elementInfo: 控件的信息，可以是xpath,id或者其他属性

    :Usage:
        self.clickElement(elementInfo)
    """

    def click_element(self, elementInfo):
        element = self.find_element(elementInfo)
        element.click()

    """
    获取某个控件显示的文本，如果该控件不能找到则会抛出异常

    :Args:
         - elementInfo: 控件的信息，可以是xpath,id或者其他属性

    :Return:
        返回该控件显示的文本

    :Usage:
        self.getTextOfElement(elementInfo)

    """

    def get_text_of_element(self, elementInfo):
        element = self.find_element(elementInfo)
        return element.text

    """
    清除文本框里面的文本

    :Usage:
        self.clearTextEdit(elementInfo)
    """

    def clear_text_edit(self, elementInfo):
        element = self.find_element(elementInfo)
        element.clear()

    """
    按返回键

    :Usage:
        self.pressBackKey()
    """

    def press_back_key(self):
        # code码参考Android的官网的keycode
        self._driver.press_keycode(4)

    """
    等待某个控件显示

    :Args:
         - elementInfo: 控件的信息，可以是xpath,id或者其他属性
         - period：等待的秒数

    :Usage:
        self.waitForElement(elementInfo, 3)
    """

    def wait_for_element(self, elementInfo, period):
        for i in range(0, period):
            sleep(1)
            try:
                self.find_element(elementInfo)
                return
            except:
                continue

        raise Exception("Cannot find %s in %d seconds" % (elementInfo, period))

    """
    等待某个控件不再显示

    :Args:
         - elementInfo: 控件的信息，可以是xpath,id或者其他属性
         - period：等待的秒数

    :Usage:
        self.waitForElementNotPresent(elementInfo, 3)
    """

    def wait_for_element_not_present(self, elementInfo, period):
        for i in range(0, period):
            sleep(1)
            # 不存在了则返回
            if not self.check_element_is_shown(elementInfo):
                return
            else:
                continue

        raise Exception("Cannot find %s in %d seconds" % (elementInfo, period))

    """
    判断某个控件是否显示

    :Args:
         - elementInfo: 控件的信息，可以是xpath,id或者其他属性
    :Return:
        True: 如果当前画面中期望的控件能被找到

    :Usage:
        self.checkElementIsShown(elementInfo)
    """

    def check_element_is_shown(self, elementInfo):
        try:
            self.find_element(elementInfo)
            return True
        except:
            return False

    """
    判断某个控件是否显示在另外一个控件中

    :Args:
        - parentElement: 父控件，是一个已知的WebElement
        - childElementInfo: 子控件的信息，可以是xpath,id或者其他属性
    :Return:
        True: 如果当前画面中期望的控件能被找到

    :Usage:
        self.checkElementShownInParentElement(elementInfo)
    """

    def check_element_shown_in_parent_element(self, parentElement, childElementInfo):
        try:
            self.find_element_in_parent_element(parentElement, childElementInfo)
            return True
        except:
            return False

    """
    判断某个控件是否被选中

    :Args:
         - elementInfo: 控件的信息，可以是xpath,id或者其他属性
    :Return:
        True: 如果当前画面中期望的控件能被选中

    :Usage:
        self.checkElementIsSelected(elementInfo)
    """

    def check_element_is_selected(self, elementInfo):
        element = self.find_element(elementInfo)
        return element.is_selected()

    """
    判断某个开关控件是否被选中

    :Args:
         - elementInfo: 控件的信息，可以是xpath,id或者其他属性
    :Return:
        True: 如果当前画面中期望的控件能被选中

    :Usage:
        self.checkElementIsChecked(elementInfo)
    """

    def check_element_is_checked(self, elementInfo):
        element = self.find_element(elementInfo)
        if element.get_attribute("checked") == "false":
            return False
        else:
            return True

    """
    判断摸个控件是否enabled
    :Args:
         - elementInfo: 控件的信息，可以是xpath,id或者其他属性
    :Return:
        True: 如果当前画面中期望的控件enabled

    :Usage:
        self.checkElementIsEnabled(elementInfo)
    """

    def check_element_is_enabled(self, elementInfo):
        element = self.find_element(elementInfo)
        return element.get_attribute("enabled")

    """
    获取当前的Activity

    :Return:
        当前Activity的名称
    """

    def get_current_activity(self):
        return self._driver.current_activity

    """
    等待某一个Activity显示
    备注：不确定是否适用于ios

    :Args:
        -activityName: 某acitivity的名称
        -period: 等待的时间，秒数
    """

    def wait_for_activity(self, activityName, period):
        for i in range(0, period):
            sleep(1)
            try:
                if activityName in self.get_current_activity():
                    return
            except:
                continue

        raise Exception("Cannot find the activity %s in %d seconds" % (activityName, period))

    """
    保存当前手机的屏幕截图到电脑上指定位置

    :Args:
         - pathOnPC: 电脑上保存图片的位置

    :Usage:
        self.saveScreenshot("c:\test_POI1.jpg")
    """

    def save_screenshot(self, pathOnPC):
        self._driver.save_screenshot(pathOnPC)

    def set_network(self, netType):
        pass

    """
    启动测试程序
    """

    def launch_app(self):
        self._driver.launch_app()

    """
    关闭测试程序
    """

    def close_app(self):
        self._driver.close_app()

    """
    获取测试设备的OS

    :Return: Android或者ios
    """

    def get_device_os(self):
        return self.desired_caps['platformName']

    """
    只打开wifi连接
    """

    def enable_wifi_only(self):
        if (self._driver.network_connection & 0x2) == 2:
            return
        else:
            self._driver.set_network_connection(ConnectionType.WIFI_ONLY)

    """
    只打开数据连接
    """

    def enable_data_only(self):
        if int(self._driver.network_connection & 4) == 4:
            return
        else:
            self._driver.set_network_connection(ConnectionType.DATA_ONLY)

    """
    关闭所有网络连接
    """

    def disable_all_connection(self):
        self._driver.set_network_connection(ConnectionType.NO_CONNECTION)

    """
    获取context
    """

    def get_context(self):
        self._driver.contexts

    def switch_context(self, contextName):
        self._driver.switch_to.context(contextName)

    """
    打开所有的网络连接
    """

    def enable_all_connection(self):
        self._driver.set_network_connection(ConnectionType.ALL_NETWORK_ON)
