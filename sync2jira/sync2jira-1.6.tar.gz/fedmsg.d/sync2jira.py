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

config = {
    'sync2jira': {
        'initialize': True,
        'testing': True,

        'jira': {
            'options': {
                'server': 'https://some_jira_server_somewhere.com',
                'verify': True,
            },
            'basic_auth': ('YOUR_USERNAME', 'YOUR_PASSWORD'),
        },
        'map': {
            'pagure': {
                'pungi': { 'project': 'COMPOSE', 'component': 'Pungi', },
                #'koji': { 'project': 'BREW', 'component': None, },
            },
            'github': {
                'fedora-infra/bodhi': { 'project': 'FACTORY', 'component': None, },
                #'product-definition-center/product-definition-center': {
                #    'project': 'PDC', 'component': 'General', },
                #'product-definition-center/pdc-client': {
                #    'project': 'PDC', 'component': 'General', },
            },
        },
        'filters': {
            'github': {
                # Only sync multi-type tickets from bodhi.
                'fedora-infra/bodhi': { 'state': 'open', 'milestone': 4, },
            },
        },
    },
    'logging': dict(
        version=1,
        loggers=dict(
            sync2jira={
                "level": "INFO",
                "propagate": True,
            },
        ),
    ),
}
