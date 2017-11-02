#!/usr/bin/env python  
# encoding: utf-8  

""" 
@version: v1.0 
@author: David 
@contact: tangwei@newrank.cn
@file: __init__.py.py 
@time: 2017/10/20 9:36 
@description: 
"""
import json
import os
import socket
import subprocess
import requests
import sys
import time

from requests import ConnectionError

__all__ = ["Device"]

show_statistic = True

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass


def use_time_statistic(func):
    def wrapper(*args, **kw):
        start = time.clock()
        result = func(*args, **kw)
        end = time.clock()
        if show_statistic:
            print  'func: <%s>,time: %f,args: %s' % (func.__name__, (end - start), list(args))
        return result

    return wrapper


_init_local_port = 9999
_remote_port = 9999
serial_port_dict = {}
serial_requests_dict = {}


def is_port_listening(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex(('127.0.0.1', port))
    s.close()
    return result == 0


def next_local_port():
    global _init_local_port
    while is_port_listening(_init_local_port):
        _init_local_port += 1
    return _init_local_port


class Adb(object):
    def __init__(self, serial=None):
        devices = Adb.devices()
        if not serial:
            if len(devices) == 1:
                serial = devices[0]
            elif len(devices) > 1:
                raise EnvironmentError("error: more than one device/emulator, should set a serial")
            else:
                raise EnvironmentError("no device connected")
        elif serial not in devices:
            raise EnvironmentError("serial->%s not connected" % serial)
        self.serial = serial

    def __repr__(self):
        return "<Adb:%s>" % self.serial

    @classmethod
    def devices(cls):
        """ return all device serials list"""
        result = Adb.raw_cmd("adb", "devices").communicate()[0].decode("utf-8")
        return [device.split("\t")[0] for device in result.split("\r\n") if device.endswith('device')]

    def adb_cmd(self, *args):
        '''adb command, add -s serial by default. return the subprocess.Popen object.'''
        return Adb.raw_cmd(*["adb", "-s", self.serial] + list(args))

    @classmethod
    def raw_cmd(cls, *args):
        '''adb command. return the subprocess.Popen object.'''
        return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def forward(self, local_port, device_port):
        '''adb port forward. return 0 if success, else non-zero.'''
        return self.adb_cmd("forward", "tcp:%d" % local_port, "tcp:%d" % device_port).wait()

    @classmethod
    def forward_list(cls):
        '''adb forward --list'''
        lines = Adb.raw_cmd("adb", "forward", "--list").communicate()[0].decode("utf-8").strip().splitlines()
        return [line.strip().split() for line in lines]

    @classmethod
    def query_local_port_by_forward_list(cls, serial, forward_port):
        '''adb forward --list
        if serial device forwarded  forward_port, return a forward local port
        else return None
        '''

        def __format_key(aim_port, aim_device):
            return "%s-%s" % (aim_port, aim_device)

        result = {}
        for device in Adb.forward_list():
            remote_port = device[2].split(":")[1]
            local_port = device[1].split(":")[1]
            device_serial = device[0]
            key = __format_key(remote_port, device_serial)
            result[key] = local_port
        aim_key = __format_key(forward_port, serial)
        if aim_key in result:
            return result[aim_key]
        else:
            return None

    def install(self, apk_path):
        """success return 0"""
        return self.adb_cmd("install", "-r", "-t", apk_path).wait()

    def get_pid(self, app_name):
        return self.shell(" ps | grep %s |awk '{print $2}'" % app_name).communicate()[0].decode("utf-8").strip()

    def kill_android_process_by_pid(self, pid):
        return self.shell(" kill %s" % pid).communicate()

    def install_uiautomator(self):
        r1 = self.install(Adb.asset_path() + "/app-debug.apk")
        r2 = self.install(Adb.asset_path() + "/app-debug-androidTest.apk")
        return r1 == 0 and r2 == 0

    def run_uiautomator(self):
        result = self.shell("am", "instrument", "-w", "-r", "-e", "debug", "false", "-e", "class",
                            "cn.newrank.ana.uiautomator_server.Entry cn.newrank.ana.uiautomator_server.test"
                            "/android.support.test.runner.AndroidJUnitRunner").poll()
        time.sleep(1)  # wait server start
        return result

    def shell(self, *args):
        return self.adb_cmd("shell", *args)

    def start_service(self, service_name):
        return self.shell("am", "startservice", service_name).wait()

    @classmethod
    def project_path(cls):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    @classmethod
    def asset_path(cls):
        return Adb.project_path() + "/client/asset/"

    @classmethod
    def start_chrome_driver(cls, port=8000, url_base="/wd/hub"):
        result = Adb.raw_cmd(Adb.asset_path() + "/chromedriver.exe", "--port=%s" % port,
                             "--url-base=%s" % url_base).poll()
        return result

    @classmethod
    def kill_windows_process_by_exe_name(cls, name):
        """
        :param name: 程序进程名称 如 MEmu.exe
        :return: 
        """
        return Adb.raw_cmd("TASKKILL", "/F", "/IM", name).wait()


class Server(object):
    def __init__(self, serial=None, adb=None, port=None):
        self.adb = adb
        if not self.adb:
            self.adb = Adb(serial)
        self.serial = serial
        global serial_port_dict
        query_port = None
        if not port and self.serial not in serial_port_dict:
            if port:
                serial_port_dict[self.serial] = port
            else:
                query_port = Adb.query_local_port_by_forward_list(self.serial, _remote_port)
                serial_port_dict[self.serial] = query_port if query_port else next_local_port()
        if self.serial not in serial_requests_dict:
            serial_requests_dict[self.serial] = requests.session()
        self.port = serial_port_dict.get(self.serial, _init_local_port)
        if not query_port:
            self.adb.forward(int(self.port), int(_remote_port))
        self.session = serial_requests_dict[self.serial]

    @property
    def rpc(self):
        return RPCClient(self)

    def __repr__(self):
        return "<Server:%s>" % self.serial


class RPCClient(object):
    server_start = False

    def __init__(self, server):
        self.server = server

    def __getattr__(self, method):
        if not RPCClient.server_start:
            if not self.server.adb.get_pid("uiautomator"):
                self.server.adb.install_uiautomator()
                self.server.adb.run_uiautomator()
            RPCClient.server_start = True
        self.uri = "http://127.0.0.1:%s/rpc/%s" % (self.server.port, method)
        return self

    def __call__(self, *args, **kwargs):
        data = []
        if args:
            for x in args:
                if isinstance(x, Selector):
                    data.append(json.dumps(x))
                else:
                    data.append(x)
        return self.server.session.post(self.uri, data=str(data)).json()


class Selector(dict):
    __fields = {"text": "text",  # MASK_TEXT,
                "textContains": "textContains",  # MASK_TEXTCONTAINS,
                "textMatches": "text",  # MASK_TEXTMATCHES,
                "textStartsWith": "textStartsWith",  # MASK_TEXTSTARTSWITH,
                "className": "clazz",  # MASK_CLASSNAME
                "classNameMatches": "clazz",  # MASK_CLASSNAMEMATCHES
                "description": "desc",  # MASK_DESCRIPTION
                "descriptionContains": "descContains",  # MASK_DESCRIPTIONCONTAINS
                "descriptionMatches": "desc",  # MASK_DESCRIPTIONMATCHES
                "descriptionStartsWith": "descStartsWith",  # MASK_DESCRIPTIONSTARTSWITH
                "checkable": "checkable",  # MASK_CHECKABLE
                "checked": "checked",  # MASK_CHECKED
                "clickable": "clickable",  # MASK_CLICKABLE
                "longClickable": "longClickable",  # MASK_LONGCLICKABLE,
                "scrollable": "scrollable",  # MASK_SCROLLABLE,
                "enabled": "enabled",  # MASK_ENABLED,
                "focusable": "focusable",  # MASK_FOCUSABLE,
                "focused": "focused",  # MASK_FOCUSED,
                "selected": "selected",  # MASK_SELECTED,
                "packageName": "pkg",  # MASK_PACKAGENAME,
                "packageNameMatches": "pkg",  # MASK_PACKAGENAMEMATCHES,
                "resourceId": "res",  # MASK_RESOURCEID,
                "resourceIdMatches": "res"}

    # ,MASK_RESOURCEIDMATCHES,#  "index": (0x800000, 0),  # MASK_INDEX,
    # "instance": (0x01000000, 0)  # MASK_INSTANCE,}

    def __init__(self, **kwargs):
        for k in kwargs:
            self[k] = kwargs[k]

    def __setitem__(self, k, value):
        key = self.__fields.get(k)
        if not key:
            raise ReferenceError("'%s' key error, please check again" % k)
        super(Selector, self).__setitem__(key, value)

    def __repr__(self):
        return json.dumps(self)


class UiObject(object):
    def __init__(self, device, selector):
        self.device = device
        self.rpc = self.device.server.rpc
        self.selector = selector
        self.objectInfo = None

    def __getattr__(self, item):
        return self.__getitem__(item=item)

    def __getitem__(self, item):
        if item in self.info:
            return self.info[item]
        else:
            raise AttributeError("'%s' is not in UiObject" % item)

    def __repr__(self):
        return self.selector.__repr__()

    def __str__(self):
        return self.__repr__()

    @property
    def info(self):
        if not self.objectInfo:
            self.objectInfo = self.rpc.objectInfo(self.selector)
            if not self.objectInfo:
                raise RuntimeError("object not found:%s" % self.selector)
        return self.objectInfo

    @property
    def key(self):
        return str(self["key"])

    def click(self, timeout=0L):
        return self.device.server.rpc.click(self.key, timeout)

    def set_text(self, text):
        return self.device.server.rpc.setText(self.key, text)

    def long_click(self, time=None):
        """
        :param time:  long type
        :return: 
        """
        x, y = (self.bounds['left'] + self.bounds['right']) / 2, (self.bounds['right'] + self.bounds['bottom']) / 2
        if not time:
            return self.device.long_click(x, y, 500L)
        else:
            return self.device.long_click(x, y, time)


class Device(object):
    web_driver_dict = {}

    def __init__(self, serial=None, port=None, auto_init_web=False):
        self.adb = Adb(serial)
        self.serial = self.adb.serial
        self.server = Server(serial=self.serial, adb=self.adb, port=port)
        self.web_driver = None
        self.auto_init_web = auto_init_web

    def __getattribute__(self, item):
        result = super(Device, self).__getattribute__(item)
        if item == "web_driver":
            if not result:
                if super(Device, self).__getattribute__("auto_init_web"):
                    return self.init_web_driver()
                raise RuntimeError("call init_web_driver first...")
        return result

    def __call__(self, **kwargs):
        pass
        # clone_d = copy(self)
        # clone_d.selector = Selector(**kwargs)
        return UiObject(self, Selector(**kwargs))

    def __repr__(self):
        return "<Device:%s>" % self.serial

    def init_web_driver(self, android_package="com.tencent.mm", android_process="com.tencent.mm:tools"):
        if is_port_listening(8000):
            Adb.kill_windows_process_by_exe_name("chromedriver.exe")
        self.adb.start_chrome_driver()
        if self.serial not in Device.web_driver_dict:
            from selenium import webdriver
            desired_capabilities = {
                "chromeOptions": {"androidPackage": android_package, "androidUseRunningApp": True,
                                  "androidProcess": android_process,
                                  "androidDeviceSerial": self.serial}}
            Device.web_driver_dict[self.serial] = webdriver.Remote("http://127.0.0.1:8000/wd/hub",
                                                                   desired_capabilities=desired_capabilities)
        self.web_driver = Device.web_driver_dict[self.serial]
        return self.web_driver

    def quit_web_driver(self, safety=True):
        if not self.web_driver and not safety:
            raise RuntimeError("web_driver not init")
        if safety and self.web_driver:
            self.web_driver.quit()
        self.web_driver = None
        Device.web_driver_dict[self.serial] = None

    def bomb(self):
        return self.server.rpc.bomb()

    def stop(self):
        try:
            print self.server.rpc.stop()
            RPCClient.server_start = False
        except ConnectionError:
            return True
        return False

    def info(self):
        return self.server.rpc.deviceInfo()

    def click(self, x, y):
        return self.server.rpc.click(x, y)

    def long_click(self, x, y, time=None):
        if not time:
            return self.server.rpc.longClick(x, y, 500L)
        else:
            return self.server.rpc.longClick(x, y, time)

    def back(self):
        return self.server.rpc.pressKey("back")

    def home(self):
        return self.server.rpc.pressKey("home")
