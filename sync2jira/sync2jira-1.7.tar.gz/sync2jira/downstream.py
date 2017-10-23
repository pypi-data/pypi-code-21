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

import operator

import logging

import arrow
import jira.client

log = logging.getLogger(__name__)

remote_link_title = "Upstream issue"

jira_cache = {}

def _matching_jira_issue_query(issue, config, free=False):
    client = jira.client.JIRA(**config['sync2jira']['jira'])
    query = 'issueFunction in linkedIssuesOfRemote("%s") and ' \
        'issueFunction in linkedIssuesOfRemote("%s")' % (
            remote_link_title, issue.url)
    if free:
        query += ' and status not in (Done, Dropped)'
    results = client.search_issues(query)
    log.debug("Found %i results for query %r" % (len(results), query))
    return results


def get_existing_jira_issue(issue, config):
    """ Get a jira issue by the linked remote issue.

    This is the new supported way of doing this.
    """
    results = _matching_jira_issue_query(issue, config)
    if results:
        return results[0]
    else:
        return None


def get_existing_jira_issue_legacy(issue, config):
    """ This is our old way of matching issues: use the special url field.

    This will be phased out and removed in a future release.
    """

    kwargs = dict(issue.downstream.items())
    kwargs["External issue URL"] = "%s" % issue.url
    kwargs = sorted(kwargs.items(), key=operator.itemgetter(0))

    client = jira.client.JIRA(**config['sync2jira']['jira'])
    query = " AND ".join([
        "=".join(["'%s'" % k, "'%s'" % v]) for k, v in kwargs
        if v is not None
    ]) + " AND (resolution is null OR resolution = Duplicate)"
    results = client.search_issues(query)
    if results:
        return results[0]
    else:
        return None

def _attach_link(config, downstream, remote_link):
    log.info("    Attaching tracking link %r to %r" % (
        remote_link, downstream.key))
    modified_desc = downstream.fields.description + " "
    client = jira.client.JIRA(**config['sync2jira']['jira'])

    # This is crazy.  Querying for application links requires admin perms which
    # we don't have, so duckpunch the client to think it has already made the
    # query.
    client._applicationlinks = []  # Crazy.

    # Add the link.
    client.add_remote_link(downstream.id, remote_link)

    # Finally, after we've added the link we have to edit the issue so that it
    # gets re-indexed, otherwise our searches won't work. Also, Handle some
    # weird API changes here...
    log.debug("    Modifying desc of %r to trigger re-index." % downstream.key)
    downstream.update({'description': modified_desc})

    return downstream


def upgrade_jira_issue(downstream, issue, config):
    """ Given an old legacy-style downstream issue...
    ...upgrade it to a new-style issue.

    Simply mark it with an external-url field value.
    """
    log.info("    Upgrading %r %r issue for %r" % (
        downstream.key, issue.downstream, issue))
    if config['sync2jira']['testing']:
        log.info("      Testing flag is true.  Skipping actual upgrade.")
        return

    # Do it!
    remote_link = dict(url=issue.url, title=remote_link_title)
    _attach_link(config, downstream, remote_link)


def create_jira_issue(issue, config):
    log.info("    Creating %r issue for %r" % (issue.downstream, issue))
    if config['sync2jira']['testing']:
        log.info("      Testing flag is true.  Skipping actual creation.")
        return

    client = jira.client.JIRA(**config['sync2jira']['jira'])
    kwargs = dict(
        summary=issue.title,
        description=issue.url,
        issuetype=dict(name="Story" if "RFE" in issue.title else "Bug"),
    )
    if issue.downstream['project']:
        kwargs['project'] = dict(key=issue.downstream['project'])
    if issue.downstream.get('component'):
        kwargs['components'] = [dict(name=issue.downstream['component'])] # TODO - make this a list in the config
    if issue.downstream.get('labels'):
        labels = issue.downstream['labels']
        if not isinstance(labels, list):
            labels = [labels]
        kwargs['labels'] = labels

    log.info("Creating issue.")
    downstream = client.create_issue(**kwargs)

    remote_link = dict(url=issue.url, title=remote_link_title)
    _attach_link(config, downstream, remote_link)
    return downstream


def close_as_duplicate(duplicate, keeper, config):
    log.info("  Closing %s as duplicate of %s" % (
        duplicate.permalink(), keeper.permalink()))
    client = jira.client.JIRA(**config['sync2jira']['jira'])
    if config['sync2jira']['testing']:
        log.info("      Testing flag is true.  Skipping actual delete.")
        return

    # Find the id of some dropped or done state.
    transitions = client.transitions(duplicate)
    transitions = dict([(t['name'], t['id']) for t in transitions])
    closed = None
    preferences = ['Dropped', 'Done', ]
    for preference in preferences:
        if preference in transitions:
            closed = transitions[preference]
            break

    text = 'Marking as duplicate of %s' % keeper.key
    if any([text in comment.body for comment in client.comments(duplicate)]):
        log.info("      Skipping comment.  Already present.")
    else:
        client.add_comment(duplicate, text)

    text = '%s is a duplicate.' % duplicate.key
    if any([text in comment.body for comment in client.comments(keeper)]):
        log.info("      Skipping comment.  Already present.")
    else:
        client.add_comment(keeper, text)

    if closed:
        try:
            client.transition_issue(duplicate, closed)
        except:
            log.exception("Failed to close %r" % duplicate.permalink())


def close_duplicates(issue, config):
    log.info("Looking for dupes of upstream %s, %s", issue.url, issue.title)
    results = _matching_jira_issue_query(issue, config, free=True)
    if len(results) <= 1:
        log.info("  No duplicates found.")
        return

    created = lambda x: arrow.get(x.fields.created)
    results = sorted(results, key=created)
    keeper, duplicates = results[0], results[1:]
    for duplicate in duplicates:
        close_as_duplicate(duplicate, keeper, config)


def sync_with_jira(issue, config):
    log.info("Considering upstream %s, %s", issue.url, issue.title)

    # First, check to see if we have a matching issue using the new method.
    # If we do, then just bail out.  No sync needed.
    log.info("  Looking for matching downstream issue via new method.")
    existing = get_existing_jira_issue(issue, config)
    if existing:
        log.info("   Found existing, matching downstream %r." % existing.key)
        return

    # If we're *not* configured to do legacy matching (upgrade mode) then there
    # is nothing left to do than to but to create the issue and return.
    if not config['sync2jira'].get('legacy_matching', True):
        log.debug("   Legacy matching disabled.")
        create_jira_issue(issue, config)
        return

    # Otherwise, if we *are* configured to do legacy matching, then try and
    # find this issue the old way.
    # - If we can't find it, create it.
    # - If we can find it, upgrade it to the new method.
    log.info("  Looking for matching downstream issue via legacy method.")
    match = get_existing_jira_issue_legacy(issue, config)
    if not match:
        create_jira_issue(issue, config)
    else:
        upgrade_jira_issue(match, issue, config)
