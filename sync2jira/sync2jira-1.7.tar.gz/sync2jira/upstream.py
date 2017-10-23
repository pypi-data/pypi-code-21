# This file is part of sync2jira.
# Copyright (C) 2016 Red Hat, Inc.
#
# sync2jira is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# sync2jira is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with sync2jira; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110.15.0 USA
#
# Authors:  Ralph Bean <rbean@redhat.com>

import logging

try:
    from urllib.parse import urlencode  # py3
except ImportError:
    from urllib import urlencode  # py2

import requests

import sync2jira.intermediary as i


log = logging.getLogger(__name__)


def handle_github_message(msg, config):
    owner = msg['msg']['repository']['owner']['login']
    repo = msg['msg']['repository']['name']
    upstream = '{owner}/{repo}'.format(owner=owner, repo=repo)
    mapped_repos = config['sync2jira']['map']['github']

    if upstream not in mapped_repos:
        log.info("%r not in github map: %r" % (upstream, mapped_repos.keys()))
        return None

    filter = config['sync2jira']\
        .get('filters', {})\
        .get('github', {})\
        .get(upstream, {'state': 'open'})

    for key, expected in filter.items():
        # special handling for label: we look for it in the list of msg labels
        if key == 'labels':
            actual = [label['name'] for label in msg['msg']['issue']['labels']]
            if expected not in actual:
                log.info("Label %s not set on issue" % expected)
                return None
        else:
            # direct comparison
            actual = msg['msg']['issue'].get(key)
            if actual != expected:
                log.info("Actual %r %r != expected %r" % (key, actual, expected))
                return None

    return i.Issue.from_github(upstream, msg['msg']['issue'], config)


def handle_pagure_message(msg, config):
    upstream = msg['msg']['project']['name']
    ns = msg['msg']['project'].get('namespace') or None
    if ns:
        upstream = '{ns}/{upstream}'.format(ns=ns, upstream=upstream)
    mapped_repos = config['sync2jira']['map']['pagure']

    if upstream not in mapped_repos:
        log.info("%r not in pagure map: %r" % (upstream, mapped_repos.keys()))
        return None

    filter = config['sync2jira']\
        .get('filters', {})\
        .get('pagure', {})\
        .get(upstream, {'status': 'Open'})

    for key, expected in filter.items():
        # special handling for tag: we look for it in the list of msg tags
        if key == 'tags':
            actual = msg['msg']['issue']['tags'] + msg['msg']['tags']
            if actual:
                if isinstance(actual[0], dict):
                    actual = [item['name'] for item in actual]
            intersection = set(actual) & set(expected)
            if not intersection:
                log.info("None of %r in %r on issue." % (expected, actual))
                return None
        else:
            # direct comparison
            actual = msg['msg']['issue'].get(key)
            if actual != expected:
                log.info("Actual %r %r != expected %r" % (key, actual, expected))
                return None

    return i.Issue.from_pagure(upstream, msg['msg']['issue'], config)


def pagure_issues(upstream, config):
    base = config['sync2jira'].get('pagure_url', 'https://pagure.io')
    url = base + '/api/0/' + upstream + '/issues'

    params = config['sync2jira']\
        .get('filters', {})\
        .get('pagure', {})\
        .get(upstream, {'status': 'Open'})

    response = requests.get(url, params=params)
    if not bool(response):
        try:
            reason = response.json()
        except:
            reason = response.text
        raise IOError("response: %r %r %r" % (response, reason, response.request.url))
    data = response.json()['issues']
    issues = (i.Issue.from_pagure(upstream, issue, config) for issue in data)
    for issue in issues:
        yield issue


def github_issues(upstream, config):
    token = config['sync2jira'].get('github_token')
    if not token:
        headers = {}
        log.warning('No github_token found.  We will be rate-limited...')
    else:
        headers = {'Authorization': 'token ' + token}

    filter = config['sync2jira']\
        .get('filters', {})\
        .get('github', {})\
        .get(upstream, {'state': 'open'})
    url = 'https://api.github.com/repos/%s/issues' % upstream
    url += '?' + urlencode(filter)

    issues = _get_all_github_issues(url, headers)
    issues = list((
        i.Issue.from_github(upstream, issue, config) for issue in issues
        if not 'pull_request' in issue  # We don't want to copy these around
    ))
    for issue in issues:
        yield issue


def _get_all_github_issues(url, headers):
    """ Pagination utility.  Obnoxious. """
    link = dict(next=url)
    while 'next' in link:
        response = requests.get(link['next'], headers=headers)
        if not bool(response):
            try:
                reason = response.json()
            except:
                reason = response.text
            raise IOError("response: %r %r %r" % (response, reason, response.request.url))
        for issue in response.json():
            yield issue
        link = _github_link_field_to_dict(response.headers.get('link', None))


def _github_link_field_to_dict(field):
    """ Utility for ripping apart github's Link header field.
    It's kind of ugly.
    """

    if not field:
        return dict()
    return dict([
        (
            part.split('; ')[1][5:-1],
            part.split('; ')[0][1:-1],
        ) for part in field.split(', ')
    ])
