#!/usr/bin/env python3
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
""" Sync github and pagure issues to a jira instance, via fedmsg.

Run with systemd, please.
"""

import logging
import logging.config
import warnings

import fedmsg
import fedmsg.config

import sync2jira.upstream as u
import sync2jira.downstream as d


log = logging.getLogger('sync2jira.main')


handlers = {
    # Example: https://apps.fedoraproject.org/datagrepper/id?id=2016-895ed21e-5d53-4fde-86ac-64dab36a14ad&is_raw=true&size=extra-large
    'github.issue.opened': u.handle_github_message,
    # Example: https://apps.fedoraproject.org/datagrepper/id?id=2017-ef579c6c-c391-449b-8cc2-837c41bd6c85&is_raw=true&size=extra-large
    'github.issue.reopened': u.handle_github_message,
    # Example: https://apps.fedoraproject.org/datagrepper/id?id=2017-a053e0c2-f514-47d6-8cb2-f7b2858f7052&is_raw=true&size=extra-large
    'github.issue.labeled': u.handle_github_message,
    # Example: https://apps.fedoraproject.org/datagrepper/id?id=2016-d578d8f6-0c4c-493d-9535-4e138a03e197&is_raw=true&size=extra-large
    'pagure.issue.new': u.handle_pagure_message,
    # Example: https://apps.fedoraproject.org/datagrepper/id?id=2017-c2e81259-8576-41a9-83c6-6db2cbcf67d3&is_raw=true&size=extra-large
    'pagure.issue.tag.added': u.handle_pagure_message,
}


def load_config(loader=fedmsg.config.load_config):
    config = loader()

    # Force some vars that we like
    config['mute'] = True

    # Validate it
    if not 'sync2jira' in config:
        raise ValueError("No sync2jira section found in fedmsg.d/ config")

    if not 'map' in config['sync2jira']:
        raise ValueError("No sync2jira.map section found in fedmsg.d/ config")

    possible = set(['pagure', 'github'])
    specified = set(config['sync2jira']['map'].keys())
    if not specified.issubset(possible):
        message = "Specified handlers: %s, must be a subset of %s."
        raise ValueError(message % (
            ", ".join(['"%s"' % item for item in specified]),
            ", ".join(['"%s"' % item for item in possible]),
        ))

    if not 'jira' in config['sync2jira']:
        raise ValueError("No sync2jira.jira section found in fedmsg.d/ config")

    return config


def listen(config):
    log.info("Waiting for a relevant fedmsg message to arrive...")
    for _, _, topic, msg in fedmsg.tail_messages(**config):
        idx = msg['msg_id']
        suffix = ".".join(topic.split('.')[3:])
        log.debug("Encountered %r %r %r" % (suffix, topic, idx))

        if not suffix in handlers:
            continue

        log.info("Handling %r %r %r" % (suffix, topic, idx))

        issue = handlers[suffix](msg, config)

        if not issue:
            log.warn("%s, %s yielded no Issue object." % (suffix, idx))
            continue

        d.sync_with_jira(issue, config)


def initialize(config):
    log.info("Running initialization to sync all issues from upstream to jira")
    log.info("   Testing flag is %r" % config['sync2jira']['testing'])
    mapping = config['sync2jira']['map']
    for upstream in mapping.get('pagure', {}).keys():
        for issue in u.pagure_issues(upstream, config):
            try:
                d.sync_with_jira(issue, config)
            except:
                log.error("Failed on %r" % issue)
                raise
    log.info("Done with pagure initialization.")

    for upstream in mapping.get('github', {}).keys():
        for issue in u.github_issues(upstream, config):
            try:
                d.sync_with_jira(issue, config)
            except:
                log.error("Failed on %r" % issue)
                raise
    log.info("Done with github initialization.")


def main():
    config = load_config()
    logging.config.dictConfig(config['logging'])
    warnings.simplefilter("ignore")

    if config['sync2jira'].get('initialize'):
        initialize(config)

    try:
        listen(config)
    except KeyboardInterrupt:
        pass

def list_managed():
    config = load_config()
    mapping = config['sync2jira']['map']
    warnings.simplefilter("ignore")

    for upstream in mapping.get('pagure', {}).keys():
        for issue in u.pagure_issues(upstream, config):
            print(issue.url)

    for upstream in mapping.get('github', {}).keys():
        for issue in u.github_issues(upstream, config):
            print(issue.url)

def close_duplicates():
    config = load_config()
    logging.config.dictConfig(config['logging'])
    log.info("   Testing flag is %r" % config['sync2jira']['testing'])
    mapping = config['sync2jira']['map']
    warnings.simplefilter("ignore")

    for upstream in mapping.get('pagure', {}).keys():
        for issue in u.pagure_issues(upstream, config):
            try:
                d.close_duplicates(issue, config)
            except:
                log.error("Failed on %r" % issue)
                raise
    log.info("Done with pagure duplicates.")

    for upstream in mapping.get('github', {}).keys():
        for issue in u.github_issues(upstream, config):
            try:
                d.close_duplicates(issue, config)
            except:
                log.error("Failed on %r" % issue)
                raise
    log.info("Done with github duplicates.")


if __name__ == '__main__':
    main()
