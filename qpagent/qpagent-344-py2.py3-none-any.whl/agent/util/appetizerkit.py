#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.util.apptoolkit
    ~~~~~~~~~~~~

    This module provide the app tool.

    :copyright: (c) 2017 by Ma Fei.
"""
import commands
import os

from appetizer import Appetizer

# iOS 中对应的表
ios_translate_map = {"iPhone3,1": "iPhone4(GSM)", "iPad1,1": "iPad", "iPod2,1": "iPodTouch2G", "AppleTV5,3": "AppleTV",
                     "iPhone6,1": "iPhone5s", "iPhone3,3": "iPhone4(CDMA)", "iPhone6,2": "iPhone5s",
                     "iPhone9,1": "iPhone7(A1660\/A1779\/A1780)", "iPhone9,2": "iPhone7Plus(A1661\/A1785\/A1786)",
                     "iPad2,1": "iPad2(WiFi)", "iPad2,2": "iPad2(GSM)", "iPod3,1": "iPodTouch3G",
                     "iPad2,3": "iPad2(CDMA)", "iPhone9,3": "iPhone7(A1778)", "iPad2,4": "iPad2(WiFi)",
                     "iPad2,5": "iPadMini(WiFi)", "iPhone9,4": "iPhone7Plus(A1784)", "iPad2,6": "iPadMini(GSM)",
                     "iPad2,7": "iPadMini(CDMA)", "iPhone1,1": "iPhone1G", "iPad3,1": "iPad3(WiFi)",
                     "iPod4,1": "iPodTouch4G", "iPad3,2": "iPad3(CDMA)", "iPhone1,2": "iPhone3G",
                     "iPad3,3": "iPad3(GSM)", "iPhone4,1": "iPhone4S", "iPad3,4": "iPad4(WiFi)",
                     "iPad3,5": "iPad4(GSM)", "iPad3,6": "iPad4(CDMA)", "iPhone7,1": "iPhone6Plus",
                     "iPad4,1": "iPadAir(WiFi)", "iPhone7,2": "iPhone6", "iPad4,2": "iPadAir(GSM)",
                     "iPod5,1": "iPodTouch5G", "iPad4,3": "iPadAir(CDMA)", "iPad4,4": "iPadMiniRetina(WiFi)",
                     "iPad4,5": "iPadMiniRetina(Cellular)", "iPad4,7": "iPadMini3(WiFi)",
                     "iPad4,8": "iPadMini3(Cellular)", "iPad4,9": "iPadMini3(Cellular)", "iPad5,1": "iPadMini4(WiFi)",
                     "iPad5,2": "iPadMini4(Cellular)", "iPad5,3": "iPadAir2(WiFi)", "iPad5,4": "iPadAir2(Cellular)",
                     "iPhone2,1": "iPhone3GS", "iPhone5,1": "iPhone5(GSM)", "iPod7,1": "iPodTouch6G",
                     "iPhone5,2": "iPhone5(CDMA)", "iPad6,3": "iPadPro9.7-inch(WiFi)", "iPhone8,1": "iPhone6s",
                     "iPad6,4": "iPadPro9.7-inch(Cellular)", "iPhone5,3": "iPhone5c", "i386,x86_64": "Simulator",
                     "iPhone8,2": "iPhone6sPlus", "iPhone5,4": "iPhone5c", "iPad6,7": "iPadPro12.9-inch(WiFi)",
                     "iPad6,8": "iPadPro12.9-inch(Cellular)", "iPod1,1": "iPodTouch1G", "iPhone8,4": "iPhoneSE"}


class AppToolKit(object):
    def __init__(self):
        self.app = Appetizer(toolkit=os.path.dirname(__file__) + '/darwin/appetizer')

    def get_android_devices(self):
        return self.app.devices.list()

    @staticmethod
    def install_android_app(devices, app):
        install_cmd = "adb -s " + devices + " install -f " + app
        commands.getstatusoutput(install_cmd)

    @staticmethod
    def uninstall_android_app(devices, app):
        uninstall_cmd = "adb -s " + devices + " shell pm uninstall  " + app
        commands.getstatusoutput(uninstall_cmd)

    @staticmethod
    def start_record(trace_file, device_serial_number):
        appetizer = Appetizer(toolkit=os.path.dirname(__file__) + '/darwin/appetizer')
        record_task = appetizer.trace.record(os.path.dirname(__file__) + "/trace/" + trace_file, device_serial_number)
        return record_task

    @staticmethod
    def stop_record(record_task):
        record_task.stop()

    @staticmethod
    def start_replay(trace_file, serialnos):
        appetizer = Appetizer(toolkit=os.path.dirname(__file__) + '/darwin/appetizer')
        replay_task = appetizer.trace.replay(os.path.dirname(__file__) + "/trace/" + trace_file, serialnos)
        replay_task.wait()

    @staticmethod
    def get_ios_devices():
        devices = []
        udid_cmd = "idevice_id -l"
        status, output = commands.getstatusoutput(udid_cmd)
        if len(output) > 0:
            udids = output.split('\n')
            for udid in udids:
                dic = {"os_type": 'iOS', "uid": udid}
                cmd = "ideviceinfo -u %s -k ProductType" % udid
                status, output = commands.getstatusoutput(cmd)
                device_type = ios_translate_map[output]

                brand = ''
                # -1表示找不到 0表示下标
                if device_type.find("iPhone") != -1:
                    brand = 'iPhone'
                elif device_type.find("iPad") != -1:
                    brand = 'iPad'
                elif device_type.find("iPod") != -1:
                    brand = 'iPod'

                dic['brand'] = brand
                dic['model'] = device_type

                cmd = "ideviceinfo -u %s -k ProductVersion" % udid
                status, output = commands.getstatusoutput(cmd)
                dic['os_type'] = 'ios'
                dic['os_version'] = output
                dic['rom_version'] = output

                cmd = "idevicename -u %s" % udid
                status, output = commands.getstatusoutput(cmd)
                dic['device_name'] = output
                devices.append(dic)
        return devices
