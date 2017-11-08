'''
Created on Dec 2, 2015

@author: panweif
'''
import jpush
from django.conf import settings

_JPush = jpush.JPush(settings.JPUSH['app_key'], settings.JPUSH['secret'])
def send(messageNo, message, *receiver, extras=None):
    push = _JPush.create_push()
    push.audience = jpush.alias(*receiver)
    iosMsg = jpush.ios(alert=message, extras=extras)
    androidMsg = jpush.android(alert=message, extras=extras)
    push.notification = jpush.notification(alert=message, android=androidMsg, ios=iosMsg)
    push.options = {"time_to_live":86400, "sendno":messageNo, "apns_production":False}
    push.platform = jpush.platform("all")
    return push.send()
    
