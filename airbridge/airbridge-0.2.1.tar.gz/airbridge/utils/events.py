# -*- coding: utf-8 -*-
import json
from airbridge.utils.exceptions import ValidationException
from airbridge.utils.user_agents import parse


def get_formatted_web_event(data):

    if type(data) is not dict:
        raise ValidationException("data should be dict type.")

    parsed_ua = parse("" or data.get("user_agent"))
    device = ""
    if parsed_ua.is_pc:
        device = "desktop"
    elif parsed_ua.is_tablet:
        device = "tablet"
    elif parsed_ua.is_mobile:
        device = "mobile"
    elif parsed_ua.is_bot:
        device = "bot"
    else:
        device = "other"

    result = {
        "user": {
            "externalUserID": data.get("user", {}).get("externalUserID"),
            "externalUserEmail": data.get("user", {}).get("externalUserEmail"),
        },
        "device": {
            "deviceType": device,
            "clientIP": data.get("client_ip"),
            "deviceUUID": data.get("device_uuid"),
            "gaid": data.get("device_gaid"),
            "ifv": data.get("device_ifv"),
            "ifa": data.get("device_ifa"),
        },
        "browser": {
            "userAgent": data.get("user_agent"),
            "clientID": data.get("client_id"),
        },
        "website": {
            "appID": data.get("app_id"),
        },
        "eventData": {
            "redirectURL": data.get("store_url"),
            "referrerURL": data.get("referrer_url"),
            "originURL": data.get("origin_url"),
            "attributionResult": {
                "simplelink": {
                    "short_id": data.get("short_id"),
                },
                "adClickID": data.get("ad_click_id"),
            },
            "timestamp": "",
        },
        "sdkVersion": data.get("sdk_version"),
        "requestedAt": data.get("requested_at"),
        "requestedTimestamp": data.get("requested_at"),
    }
    return result


def get_formatted_data(data):

    if type(data) is not dict:
        raise ValidationException("data should be dict type.")

    result = {
        "user": {
            "externalUserID": data.get("user", {}).get("externalUserID"),
            "externalUserEmail": data.get("user", {}).get("externalUserEmail"),
        },
        "device": {
            "deviceUUID": data.get("device", {}).get("deviceUUID"),
            "gaid": data.get("device", {}).get("gaid"),
            "ifv": data.get("device", {}).get("ifv"),
            "ifa": data.get("device", {}).get("ifa"),
            "facebookAttributionID": data.get("device", {}).get("facebookAttributionID", ""),
            "deviceModel": data.get("device", {}).get("deviceModel"),
            "deviceIdentifier": data.get("device", {}).get("deviceIdentifier"),
            "systemAutoTime": data.get("device", {}).get("systemAutoTime"),
            "manufacturer": data.get("device", {}).get("manufacturer"),
            "osName": data.get("device", {}).get("osName", ""),
            "orientation": data.get("device", {}).get("orientation", ""),
            "osVersion": data.get("device", {}).get("osVersion", ""),
            "locale": data.get("device", {}).get("locale"),
            "limitAdTracking": data.get("device", {}).get("limitAdTracking", '1'),
            "limitAppTracking": data.get("device", {}).get("limitAppTracking", '1'),
            "timezone": data.get("device", {}).get("timezone"),
            "deviceIP": data.get("device", {}).get("deviceIP"),
            "clientIP": data.get("device", {}).get("clientIP"), # can be none (Need nginx script)
            "screen": {
                "width": data.get("device", {}).get("screen", {}).get("width"),
                "height": data.get("device", {}).get("screen", {}).get("height"),
                "density": data.get("device", {}).get("screen", {}).get("density"),
            },
            "network": {
                "carrier": data.get("device", {}).get("network", {}).get("carrier"),
                "bluetooth": data.get("device", {}).get("network", {}).get("bluetooth"),
                "cellular": data.get("device", {}).get("network", {}).get("cellular"),
                "wifi": data.get("device", {}).get("network", {}).get("wifi"),
            },
            "location": {
                "latitude": data.get("device", {}).get("location", {}).get("latitude"),
                "longitude": data.get("device", {}).get("location", {}).get("longitude"),
                "altitude": data.get("device", {}).get("location", {}).get("altitude"),
                "speed": data.get("device", {}).get("location", {}).get("speed"),
            },
        },
        "app": {
            "version": data.get("app", {}).get("version"),
            "versionCode": data.get("app", {}).get("versionCode"),
            "packageName": data.get("app", {}).get("packageName"),
        },
        "eventData": {
            "exActiveStatus": data.get("eventData", {}).get("exActiveStatus"),
            "googleReferrer": data.get("eventData", {}).get("googleReferrer"),
            "systemInstallTimestamp": data.get("eventData", {}).get("systemInstallTimestamp"),
            "deeplink": data.get("eventData", {}).get("deeplink"),
            "goal": {
                "category": data.get("eventData", {}).get("goal", {}).get("category"),
                "action": data.get("eventData", {}).get("goal", {}).get("action"),
                "label": data.get("eventData", {}).get("goal", {}).get("label"),
                "value": data.get("eventData", {}).get("goal", {}).get("value"),
                "semanticAttributes": data.get("eventData", {}).get("goal", {}).get("semanticAttributes"),
                "customAttributes": data.get("eventData", {}).get("goal", {}).get("customAttributes"),
            },
            "page": {
                "label": data.get("eventData", {}).get("page", {}).get("label"),
                "name": data.get("eventData", {}).get("page", {}).get("name"),
                "customAttributes": data.get("eventData", {}).get("page", {}).get("customAttributes"),
            },
        },
        "eventTimestamp": data.get("eventTimestamp"),
        "requestTimestamp": data.get("requestTimestamp"),
        "sdkVersion": data.get("sdkVersion"),
    }

    return result 
