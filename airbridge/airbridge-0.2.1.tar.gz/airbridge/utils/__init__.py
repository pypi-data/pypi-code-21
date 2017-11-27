# -*- coding: utf-8 -*-
from enum import IntEnum, unique


@unique
class CrossPlatformMatchingType(IntEnum):
    UNDEFINED = 1
    ID = 2
    REFERRER = 4
    FINGER_PRINTING = 5
    DEEPLINK = 6
    PLATFORM = 9
    SAFARI_COOKIE = 3
    CHROME_COOKIE = 13


@unique
class EventCategoryType(IntEnum):
    VIEW = 1
    REACH = 2
    GOAL = 3


@unique
class EventCategorySource(IntEnum):
    CHANNEL = 1
    WEB = 2
    SMS = 3
    IOS_MARKET = 4
    ANDROID_MARKET = 5
    APP = 6
    BACKGROUND = 9
    EXIT = 0


@unique
class EventCategoryValue(IntEnum):
    VIEW__CHANNEL = 9110
    VIEW__WEB = 9120    
    VIEW__SMS = 9130    
    VIEW__APP_LAUNCH = 9160
    VIEW__APP_INSTALL = 9161    
    VIEW__APP_DEEPLINK_LAUNCH = 9162    
    VIEW__APP_DEEPLINK_INSTALL = 9163   
    VIEW__APP_PAGEVIEW = 9164   
    VIEW__APP_FOREGROUND = 9165   

    REACH__CHANNEL_TO_WEB = 9212
    REACH__CHANNEL_TO_IOS_MARKET = 9214 
    REACH__CHANNEL_TO_ANDROID_MARKET = 9215
    REACH__CHANNEL_TO_APP = 9216
    REACH__WEB_TO_WEB = 9222    
    REACH__WEB_TO_SMS = 9223    
    REACH__WEB_TO_IOS_MARKET = 9224
    REACH__WEB_TO_ANDROID_MARKET = 9225 
    REACH__WEB_TO_APP = 9226    
    REACH__SMS_TO_WEB = 9232    
    REACH__SMS_TO_IOS_MARKET = 9234
    REACH__SMS_TO_ANDROID_MARKET = 9235 
    REACH__SMS_TO_APP = 9236    
    REACH__APP_EXIT = 9260
    REACH__APP_TO_WEB = 9262    
    REACH__APP_TO_BACKGROUND = 9269

    GOAL__WEB = 9320    
    GOAL__APP = 9360    


class EventCategory(object):

    EVENT_CONSTANT = 9000

    def __init__(self, event_category):
        if event_category not in map(int, EventCategoryValue):
            raise Exception("Not Supported Event Category")

        self.value = EventCategoryValue(int(event_category))
        self.type = EventCategoryType(int(str(event_category-self.EVENT_CONSTANT)[0]))
        self.source = EventCategorySource(int(str(event_category-self.EVENT_CONSTANT)[1]))

        if self.type == EventCategoryType.VIEW.value or self.type == EventCategoryType.GOAL.value:
            self.type_value = int(str(event_category-self.EVENT_CONSTANT)[2])
            self.target = None
        elif self.type == EventCategoryType.REACH.value:
            self.type_value = None
            self.target = EventCategorySource(int(str(event_category-self.EVENT_CONSTANT)[2]))
        else:
            raise Exception("Not Supported Event Category")
