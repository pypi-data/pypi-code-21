# -*- coding: utf-8 -*-
import time
from uuid import uuid4


class MobileAppEvent(object):

    def __init__(self, event):
        self.event = event

    def get_event(self):
        return self.event

    def refresh(self, event_category=None, app_id=None, external_user_id=None, external_user_email=None):
        event_timestamp = int(time.time()*1000)
        self.event['event']['eventData']['timesetamp'] = event_timestamp
        self.event['event']['eventTimesetamp'] = event_timestamp
        self.event['event']['requestTimesetamp'] = event_timestamp

        if event_category is not None:
            self.event['event']['eventData']['eventCategory'] = event_category
        if app_id is not None:
            self.event['event']['app']['appID'] = app_id
        if external_user_id is not None:
            self.event['event']['user']['externalUserID'] = external_user_id
        if external_user_email is not None:
            self.event['event']['user']['externalUserEmail'] = external_user_email


def get_sample_event(user__external_user_id=None, 
                     user__external_user_email=None,
                     device__device_uuid=None,
                     event_category=None):
    device_uuid = device__device_uuid or str(uuid4())
    event_timestamp = int(time.time()*1000)

    event = {
       "event":{
          "user":{
             "externalUserID": user__external_user_id or str(uuid4()),
             "externalUserEmail": user__external_user_email or str(uuid4()),
          },
          "device":{
             "orientation":"portrait",
             "locale":"ko-KR",
             "deviceUUID": device_uuid,
             "gaid": device_uuid,
             "ifv": "",
             "ifa": "",
             "timezone":"seoul",
             "deviceIdentifier":"",
             "network":{
                "wifi":1,
                "bluetooth":0,
                "cellular":0,
                "carrier":"KT"
             },
             "deviceModel":"SM-G900P",
             "location":{
                "latitude":120.103,
                "altitude":123.0,
                "speed":12,
                "longitude":120.1023412
             },
             "limitAdTracking":1,
             "manufacturer":"Samsung",
             "facebookAttributionID":"",
             "screen":{
                "width":123,
                "height":"123",
                "density":2
             },
             "limitAppTracking":0,
             "clientIP":"127.0.0.1",
             "osVersion":"5.0",
             "deviceIP":"127.0.0.1",
             "language":"ko",
             "country":"kr",
             "osName":"Android",
             "systemAutoTime":"",
             "osRaw":"Android5.0"
          },
          "app":{
             "iTunesAppID":"1135798509",
             "packageName":"com.ab180.co",
             "appName":"ablog",
             "version":"1.2.3",
             "appID":619,
             "versionCode":"4.5"
          },
          "eventData":{
             "goal":{
                "category":"haha",
                "semanticAttributes":{

                },
                "value":3000,
                "label":"labellaiaaai",
                "customAttributes":{
                   "haha":"hoho"
                },
                "action":"hoho"
             },
             "deeplink":"ablog://redirect",
             "googleReferrer":"referrer=utm_campaign%3D123",
             "eventCategory": event_category,
             "eventDatetime":"2017-09-21T16:50:14+09:00",
             "systemInstallTimestamp":"",
             "eventTimestampInSec":1505980214,
             "exActiveStatus":1,
             "page":{
                "customAttributes":{
                   "haha":"hoho"
                },
                "name":"activity",
                "label":"haha"
             },
             "timestamp": event_timestamp,
          },
          "eventTimestamp": event_timestamp,
          "requestTimestamp": event_timestamp,
          "sdkVersion":"T_A_v2.0",
       }
    }
    return MobileAppEvent(event)
