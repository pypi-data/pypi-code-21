#!/usr/bin/env python
# -*- coding: utf-8 -*-
import enum


class AgentWorkerType(enum.IntEnum):
    unknown = 0
    macaca = 1
    selenium = 2
    appcrawler = 3
    androidmonkey = 4
    iosmonkey = 5


class TaskType(enum.IntEnum):
    unknown = 0
    crawler = 1
    classify = 2
    esm = 3
    proxy = 4
    uiplay = 5
    uirecord = 6
    compatibility = 7
    appcrawler = 8
    android_monkey = 9
    ios_monkey = 10


class DeviceStatus(enum.IntEnum):
    online = 1
    offline = 0
    busy = 2


class TaskStatus(enum.IntEnum):
    created = 0
    running = 1
    success = 2
    failed = 3
    timeout = 4


class CompatibilityUserStatus(enum.IntEnum):
    unavailable = 0
    available = 1


class AgentStatus(enum.IntEnum):
    online = 1
    offline = 0


class MailType(enum.IntEnum):
    unknown = 0
    monkey = 1
    testin = 2
    appcrawler = 3
