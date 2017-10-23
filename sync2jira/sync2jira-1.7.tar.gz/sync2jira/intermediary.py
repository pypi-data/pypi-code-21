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


class Issue(object):

    def __init__(self, source, title, url, upstream, config):
        self.source = source
        self._title = title
        self.url = url
        self.upstream = upstream
        self.downstream = config['sync2jira']['map'][self.source][upstream]

    @property
    def title(self):
        return u'[%s] %s' % (self.upstream, self._title)

    @classmethod
    def from_pagure(cls, upstream, issue, config):
        base = config['sync2jira'].get('pagure_url', 'https://pagure.io')
        return Issue(
            source='pagure',
            title=issue['title'],
            url=base + '/%s/issue/%i' % (upstream, issue['id']),
            upstream=upstream,
            config=config,
        )

    @classmethod
    def from_github(cls, upstream, issue, config):
        return Issue(
            source='github',
            title=issue['title'],
            url=issue['html_url'],
            upstream=upstream,
            config=config,
        )

    def __repr__(self):
        return "<Issue %s >" % self.url
