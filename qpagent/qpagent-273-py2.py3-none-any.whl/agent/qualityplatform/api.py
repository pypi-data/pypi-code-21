#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import time

import requests
from requests.auth import HTTPBasicAuth

import agent.config as config
import agent.util.host as host
import base as api_tools
from agent.consts import DeviceStatus
from agent.consts import TestRunStatus
from agent.exc import WorkerException
from agent.util.appetizerkit import AppToolKit, iOSToolKit

logger = logging.getLogger(__name__)


def register_agent(status):
    devices = []
    android_devices = AppToolKit().get_devices()
    for android_device in android_devices:
        device = {
            'brand': android_device.get('brand'),
            'model': android_device.get('model'),
            'os_type': 'android',
            'os_version': android_device.get('os'),
            'rom_version': android_device.get('sdk'),
            'uid': android_device.get('uid'),
            'status': DeviceStatus.online.value
        }
        devices.append(device)
    tool = iOSToolKit()
    ios_devices = tool.get_devices()
    for ios_device in ios_devices:
        device = {
            'brand': ios_device.get('brand'),
            'model': ios_device.get('model'),
            'os_type': ios_device.get('os_type'),
            'os_version': ios_device.get('os_version'),
            'rom_version': ios_device.get('rom_version'),
            'uid': ios_device.get('uid'),
            'status': DeviceStatus.online.value
        }
        devices.append(device)
    agent_device = {
        'ip': host.ip(),
        'port': config.agent['port'],
        'name': host.name(),
        'status': status,
        'devices': devices
    }
    return api_tools.post('agents/register', agent_device)


def unregister_agent(agent_id):
    api_tools.delete('agents/' + str(agent_id) + '/unregister')


def update_device_status(device_id, status):
    data = {
        'status': status
    }
    api_tools.put('devices/' + str(device_id), data)


def add_case_file(test_case_id, case_url):
    data = {
        'url': case_url
    }
    api_tools.put('testcases/' + str(test_case_id), data)


def upload_file(case_file):
    files = {
        'file': case_file
    }
    data = {
        'extension': 'js'
    }
    return api_tools.upload('file/upload', files, data)


def upload_case_file(test_case_id, case_file):
    fuss_hash = upload_file(case_file)
    add_case_file(test_case_id, fuss_hash)


def get_task_by_id(task_id):
    return api_tools.get('tasks/' + str(task_id))


def update_task_status(task_id, status):
    data = {
        'status': status,
    }
    api_tools.put('tasks/' + str(task_id), data)


def update_compatibility_user_status(name, status):
    data = {
        'name': name,
        'status': status
    }
    api_tools.put('CT_users', data)


def upload_task_reports(task_id, report):
    data = {
        'log': report,
    }
    api_tools.put('tasks/' + str(task_id), data)


def send_mail(receivers, title, subject, app, content, template):
    if type(receivers) is not list:
        receivers = [receivers]
    mail_content = {
        'receivers': receivers,
        'title': title,
        'subject': subject,
        'app_version': app['appVersion'],
        'commit_id': app['commitId'],
        'build_no': app['buildNo'],
        'date': time.strftime('%Y-%m-%d  %H:%M', time.localtime(time.time())),
        'aut': app['downloadURL'],
        'content': content,
        'template': template,
    }
    return api_tools.post('mail', mail_content)


def add_user_comment(user_comment):
    return api_tools.post('comments', user_comment)


def get_app_channel_crawler_history(app_channel_id):
    return api_tools.get('crawler_histories?app_channel_id=%s' % app_channel_id)


def add_crawler_history(crawler_history):
    return api_tools.post("crawler_histories", crawler_history)


def add_report(reports):
    return api_tools.post('reports', reports)


def add_project_run(project_id, test_run):
    return api_tools.post('testrail/projects/{}/runs'.format(project_id), test_run)


def add_results_for_cases(run_id, case_id, log, status=TestRunStatus.passed.value, app=None):
    if app:
        comment = {
            "app_name": app['appName'],
            "app_version": app['appVersion'],
            "commit_id": app['commitId'],
            "download_url": app['downloadURL'],
            "log": log,
            "package_type": app['packageType'],
            "platform": app['platform'],
            "date": time.strftime('%Y-%m-%d  %H:%M', time.localtime(time.time())),
        }
    else:
        comment = {
            "report": log
        }

    test_results = {
        'results': [
            {
                "case_id": case_id,
                "status_id": status,
                "comment": json.dumps(comment)
            }
        ]
    }
    return api_tools.post('testrail/test_results/runs/{}'.format(run_id), test_results)


def get_project_milestones(project_id):
    return api_tools.get('testrail/projects/{}/milestones'.format(project_id))


def get_latest_app(appId, platform, packType, version=None):
    try:
        if version:
            r = requests.get(
                'http://mtci.beta.elenet.me:8080/ci/openapi/v1/builds/latest?appId=' + appId + '&platform=' + platform + '&packType=' + packType + '&version=' + version)
        else:
            r = requests.get(
                'http://mtci.beta.elenet.me:8080/ci/openapi/v1/builds/latest?appId=' + appId + '&platform=' + platform + '&packType=' + packType)
        if r.ok:
            return r.json()
        else:
            raise WorkerException("app data is none")
    except requests.RequestException as e:
        raise WorkerException(e.message)


def get_latest_app_version(appId, platform, packType):
    try:
        r = requests.get(
            'http://mtci.beta.elenet.me:8080/ci/openapi/v1/builds/latest?appId=' + appId + '&platform=' + platform + '&packType=' + packType)
        if r.ok:
            return r.json()['appVersion']
        else:
            raise WorkerException("appVersion is none")
    except requests.RequestException as e:
        raise WorkerException(e.message)


def add_jira_issue(project_key, summary, description):
    try:
        issue = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,
                "description": description,
                "issuetype": {
                    "name": "Bug"
                }
            }
        }
        r = requests.post(
            'http://jira.ele.to:8088/rest/api/2/issue/', json=issue, auth=HTTPBasicAuth('waimai', 'waimai@123'))
        if r.ok:
            return r.json()
    except requests.RequestException as e:
        raise WorkerException(e.message)
