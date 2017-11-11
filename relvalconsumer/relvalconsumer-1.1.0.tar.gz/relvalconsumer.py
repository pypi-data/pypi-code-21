# Copyright (C) 2016 Red Hat
#
# relvalconsumer is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>

"""fedmsg consumer to create release validation events."""

from __future__ import unicode_literals
from __future__ import print_function

import logging
import smtplib
import sys
import time

import fedfind.helpers
import fedmsg.consumers
import hawkey
import mwclient.errors
import rpm
import wikitcms.event
import wikitcms.wiki

from six.moves.urllib.error import (URLError, HTTPError)

__version__ = "1.1.0"


class RelvalConsumer(fedmsg.consumers.FedmsgConsumer):
    """A fedmsg consumer that creates release validation test events
    for new composes when appropriate. This is a parent class shared
    by the two children for 'production' and 'testing' mode and should
    not be used on its own (it is not complete).
    """
    def _log(self, level, message):
        """Convenience function for sticking the class name on the
        front of the log message as an identifier.
        """
        logfnc = getattr(self.log, level)
        logfnc("%s: %s", self.__class__.__name__, message)

    def consume(self, message):
        """Consume incoming message. 'relval_prod' indicates prod or
        test mode.
        """
        # only run on completed composes
        action = message['body']['msg'].get('action')
        cid = message['body']['msg'].get('compose_id')
        if not action == "create" and cid:
            return

        # some compose info we'll use
        (dist, rel, date, typ, _) = fedfind.helpers.parse_cid(cid, dist=True)

        # don't run on any dist but Fedora or Fedora-Modular for now
        if dist not in ('Fedora', 'Fedora-Modular'):
            return
        # We only want to create F27 events for Modular for now
        if dist == 'Fedora-Modular' and rel != '27':
            return

        if self.relval_prod:
            serv = 'fedoraproject.org'
        else:
            serv = 'stg.fedoraproject.org'
        site = wikitcms.wiki.Wiki(('https', serv), '/w/')
        site.login()

        # get the validation event instance
        try:
            event = site.get_validation_event(cid=cid)
        except ValueError:
            self._log('info',
                      "Could not determine event for compose {0}".format(cid))
            return
        self._log('info', "Working on compose {0}".format(cid))

        # FIXME: we might want to put some 'are there sufficient
        # images for testing' heuristic in here, or even wait for
        # openQA results and bail if they all failed

        # at present we should only ever create events for exactly the
        # release after the current stable release; this prevents us
        # creating Rawhide events during Branched periods. Note we have
        # to handle the case of creating the *first* Rawhide nightly
        # after a stable release, so we cannot just require release to
        # equal wiki.current_compose['release']. We skip this logic
        # for Fedora-Modular for now as we're only creating 27 events.
        if dist == 'Fedora':
            curr = fedfind.helpers.get_current_release()
            if not int(event.release) == curr+1:
                self._log('info', "Compose {0} is not for the next release!".format(cid))
                return

        if dist == 'Fedora':
            currev = site.current_event
        else:
            currev = site.current_modular_event
        try:
            newdate = fedfind.helpers.date_check(date, out='obj')
            currdate = fedfind.helpers.date_check(currev.creation_date, out='obj')
        except ValueError:
            self._log('warning', "Could not determine date of current or new event!")
            return

        if typ not in ('nightly', 'production'):
            self._log('warning', "Unexpected compose type {0} for compose "
                      "{1}!".format(typ, cid))
            return

        # FLOW NOTE: at this point if the event release is newer than
        # the current event release, we do no further checks and just
        # create the event. This should occur once per cycle just
        # after GA and create the first Rawhide nightly event for the
        # next release.
        diff = ''

        if typ == 'production' and event.release == currev.release:
            # just check we're actually newer than the current event as a
            # sanity check
            ok = True
            if newdate < currdate:
                ok = False
            # for same date, check the sorttuple as a tie-breaker, so
            # two 'production' events on the same day *do* get created
            if newdate == currdate and event.sorttuple <= currev.sorttuple:
                ok = False
            if not ok:
                self._log('warning', "New event {0} would not be newer than "
                          "current event {1}!".format(event.version, currev.version))
                return

        # if we're proposing a nightly event for the same release, do the
        # date check / package comparison stuff
        if typ == 'nightly' and event.release == currev.release:
            delta = newdate - currdate
            if delta.days < 3:
                # we never create an event if it's been < 3 days.
                self._log('info', "Less than three days since current event.")
                return
            elif delta.days > 14:
                # we *always* create an event if it's been > 14 days.
                self._log('debug', "More than two weeks since current event!")
            else:
                # between 3 and 14 we check if important packages have changed.
                self._log('debug', "Comparing package versions...")
                packages = ['anaconda', 'python-blivet', 'pyparted',
                            'lorax', 'pungi', 'parted', 'pykickstart']
                # this is awful, but there's a race between PDC fedmsg
                # emission and database commit (per threebean) so we
                # should sleep a bit before trying to talk to PDC.
                time.sleep(10)
                try:
                    currpacks = currev.ff_release.get_package_nvras(packages)
                    newpacks = event.ff_release.get_package_nvras(packages)
                except (ValueError, URLError, HTTPError):
                    self._log('info', "Package version check failed!")
                    return
                if not currpacks:
                    self._log('info', "Could not do package version check on current compose!")
                    return
                if not newpacks:
                    self._log('info', "Could not do package version check on new compose!")
                    return
                for key in list(currpacks.keys()):
                    if not currpacks[key] or not newpacks[key]:
                        self._log('info', "Could not find versions for all significant "
                                          "packages in both composes!")
                        return
                if currpacks == newpacks:
                    self._log('info', "No significant package changes since current event.")
                    return
                else:
                    # check that packages are *newer*, not older (this is to
                    # guard against creating a nightly event after a candidate
                    # event with older packages; it's not perfect, though)
                    for package in list(currpacks.keys()):
                        currnevra = hawkey.split_nevra(currpacks[package])
                        newnevra = hawkey.split_nevra(newpacks[package])
                        # use rpm.labelCompare for now as hawkey NEVRA
                        # comparison is broken:
                        # https://github.com/rpm-software-management/libhif/issues/125
                        currtup = (str(currnevra.epoch), str(currnevra.version),
                                   str(currnevra.release))
                        newtup = (str(newnevra.epoch), str(newnevra.version),
                                  str(newnevra.release))
                        if rpm.labelCompare(newtup, currtup) == -1:
                            self._log('info', "Package {0} older in new event! New: {1} "
                                      "Old: {2}".format(package, newpacks[package],
                                                        currpacks[package]))
                            return
                    self._log('info', "Significant package updates since current event!")
                    # this means we're carrying on.
                    diff = ''
                    for key in list(currpacks.keys()):
                        if currpacks[key] != newpacks[key]:
                            diff += ("{0} - {1}: {2}, {3}: {4}\n".format(
                                key, currev.compose, currpacks[key],
                                event.compose, newpacks[key]))

        self._log('info', "Creating validation event {0}".format(event.version))
        try:
            event.create(check=True)
        except mwclient.errors.APIError as err:
            self._log('warning', "Mediawiki error creating event!")
            self._log('debug', "Error: {0}".format(err))
            return
        except ValueError:
            self._log('warning', "Existing page found for event! Aborting.")
            return

        # send the announcement mail. FIXME: for now the text is still
        # nightly-specific, change that when we use this for TCs/RCs.
        self._log('debug', "Sending announcement email")
        dest = "test-announce@lists.fedoraproject.org"
        urltmpl = "https://fedoraproject.org/wiki/{0}"
        summurl = urltmpl.format(event.summary_page.name.replace(' ', '_'))
        pageurls = [urltmpl.format(pag.name.replace(' ', '_'))
                    for pag in event.valid_pages if 'Summary' not in pag.name]
        if diff:
            difftext = '\nNotable package version changes:\n{0}'.format(diff)
        else:
            difftext = ''
        # this is the final part of the testcase_stats link; we want it
        # to be e.g. '27' for non-modular, '27modular' for modular
        tcstext = event.release
        if dist == 'Fedora-Modular':
            tcstext += "modular"
        nighttmpl = ("""From: rawhide@fedoraproject.org
To: {0}
Subject: {1} {2} nightly compose nominated for testing

Announcing the creation of a new nightly release validation test event
for {1} {2}. Please help run some tests for this
nightly compose if you have time. For more information on nightly
release validation testing, see:
https://fedoraproject.org/wiki/QA:Release_validation_test_plan
{3}
Test coverage information for the current release can be seen at:
https://www.happyassassin.net/testcase_stats/{4}

You can see all results, find testing instructions and image download
locations, and enter results on the Summary page:

{5}

The individual test result pages are:

{6}

Thank you for testing!
-- 
Mail generated by relvalconsumer: https://pagure.io/fedora-qa/relvalconsumer
""")
        prodtmpl = ("""From: rawhide@fedoraproject.org
To: {0}
Subject: {1} {2} Candidate {3}-{4} Available Now!

According to the schedule [1], {1} {2} Candidate {3}-{4} is now
available for testing. Please help us complete all the validation
testing! For more information on release validation testing, see:
https://fedoraproject.org/wiki/QA:Release_validation_test_plan
{5}
Test coverage information for the current release can be seen at:
https://www.happyassassin.net/testcase_stats/{6}

You can see all results, find testing instructions and image download
locations, and enter results on the Summary page:

{7}

The individual test result pages are:

{8}

All {3} priority test cases for each of these test pages [2] must
pass in order to meet the {3} Release Criteria [3].

Help is available on #fedora-qa on irc.freenode.net [4], or on the
test list [5].

Current Blocker and Freeze Exception bugs:
http://qa.fedoraproject.org/blockerbugs/current

[1] http://fedorapeople.org/groups/schedule/f-{2}/f-{2}-quality-tasks.html
[2] https://fedoraproject.org/wiki/QA:Release_validation_test_plan
[3] https://fedoraproject.org/wiki/Fedora_{2}_{3}_Release_Criteria
[4] irc://irc.freenode.net/fedora-qa
[5] https://lists.fedoraproject.org/archives/list/test@lists.fedoraproject.org/
""")
        if typ == 'nightly':
            msg = nighttmpl.format(
                dest, dist, event.version, difftext, tcstext, summurl, '\n'.join(pageurls))
        else:
            msg = prodtmpl.format(
                dest, dist, event.release, event.milestone, event.compose, difftext, tcstext, summurl,
                '\n'.join(pageurls))
        if self.relval_prod:
            server = smtplib.SMTP('localhost')
            server.sendmail('rawhide@fedoraproject.org', [dest], msg)
        else:
            self._log('info', msg)


class RelvalProductionConsumer(RelvalConsumer):
    """The production consumer: listens for prod messages, creates
    events in the production wiki, and sends emails to mailing lists.
    Use carefully! Only one instance of this should be running in the
    world at any time.
    """
    topic = "org.fedoraproject.prod.pdc.compose"
    config_key = "relvalconsumer.prod.enabled"
    # this is our own thing, so let's 'namespace' it to avoid any
    # unfortunate collisions with fedmsg/moksha
    relval_prod = True


class RelvalTestConsumer(RelvalConsumer):
    """The testing consumer: listens for dev messages, creates
    events in the staging wiki, and logs the announcement email rather
    than sending it. Still, don't run this willy-nilly, as the more
    people poking the staging wiki, the more confusing things will be.
    """
    topic = "org.fedoraproject.dev.pdc.compose"
    config_key = "relvalconsumer.test.enabled"
    validate_signatures = False
    # this is our own thing, so let's 'namespace' it to avoid any
    # unfortunate collisions with fedmsg/moksha
    relval_prod = False

# vim: set textwidth=120 ts=8 et sw=4:
