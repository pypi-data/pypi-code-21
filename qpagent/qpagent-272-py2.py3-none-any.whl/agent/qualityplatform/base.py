#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

from agent.config import qualityplatform
from agent.util.sentry import Sentry

headers = {'Token': '53a308a3-93ad-11e7-9876-28cfe91a6a05'}

sentry = Sentry()


def post(api, data):
    url = qualityplatform.get('api_url') + api
    try:
        r = requests.post(url, json=data, headers=headers)
        if r.ok:
            return r.json()
    except requests.RequestException:
        sentry.client.captureException()


def upload(api, files, data):
    url = qualityplatform.get('api_url') + api
    try:
        r = requests.post(url, files=files, data=data, headers=headers)
        if r.ok:
            return r.json()
        else:
            return ''
    except requests.RequestException:
        sentry.client.captureException()


def get(api):
    url = qualityplatform.get('api_url') + api
    try:
        r = requests.get(url, headers=headers)
        if r.ok:
            return r.json()
    except requests.RequestException:
        sentry.client.captureException()


def put(api, data):
    url = qualityplatform.get('api_url') + api
    try:
        requests.put(url, json=data, headers=headers)
    except requests.RequestException:
        sentry.client.captureException()


def delete(api):
    url = qualityplatform.get('api_url') + api
    try:
        requests.delete(url, headers=headers)
    except requests.RequestException:
        sentry.client.captureException()
