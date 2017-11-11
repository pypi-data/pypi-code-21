# Copyright (C) 2016 Red Hat
#
# This file is part of relvalconsumer.
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

# these are all kinda inappropriate for pytest patterns
# pylint: disable=old-style-class, no-init, protected-access, no-self-use, unused-argument

import time

import mock
import pytest
import relvalconsumer
import wikitcms.event

# The test approach here is that we just recreate an entire release
# cycle with mocks, and ensure the consumer does the right thing for
# each compose that shows up.

def _fakepginit(self, site, name, info=None, extra_properties=None):
    """Stub init for mwclient Page, just make sure name and site are
    set.
    """
    self.site = site
    self.name = name

def _fakemsg(cid, action='create'):
    return {
        'body': {
            'msg': {
                'compose_id': cid,
                'action': action
            }
        }
    }

def _fakegetsame(self, packages):
    """This is a fake 'get_current_packages' which always returns the
    same dict, so when *this* is used as the mock, the consumer will
    consider both composes to have the same packages.
    """
    return {'key': 'value'}

def _fakegetdifferent(self, packages):
    """This is a fake 'get_current_packages' which returns a dict with
    time.clock() as the 'package version'. This should mean that when
    *this* is used as the mock, the consumer will consider both
    composes to have different packages, and the 'new' compose (whose
    package list is checked second) will have 'newer' packages.
    """
    return {'fakepackage': "fakepackage-{0}-1.fc24.src".format(str(int(time.clock() * 1000000)))}

def _fakegetolder(self, packages):
    """This is a fake 'get_current_packages' which returns a dict with
    (10 - time.clock()) as the 'package version'. So when *this* is
    used as the mock, the consumer will consider both composes to have
    different packages, and the 'new' compose (whose package list is
    checked second) will have 'older' packages.
    """
    return {'fakepackage': "fakepackage-{0}-1.fc24.src".format(str(10 * 1000000 - int(time.clock() * 1000000)))}

def _fakegetcurr1(branched=False):
    """A faked get_current_release which just returns static values.
    This one is for pre-branch-point, when 24 is always the result.
    """
    return 24

def _fakegetcurr2(branched=False):
    """A faked get_current_release which just returns static values.
    This one is for post-branch-point, when 25 is the current Branched
    but 24 is the current stable.
    """
    if branched:
        return 25
    else:
        return 24

# a bunch of patches we need throughout the tests
# ALL SLEEPS MUST DIE
mock.patch('time.sleep', autospec=True).start()
# we have to stub this as we are skipping FedmsgConsumer __init__
mock.patch('relvalconsumer.RelvalConsumer._log', autospec=True).start()
# page init requires wiki trip
mock.patch('mwclient.page.Page.__init__', _fakepginit).start()
# testtypes are read from wiki
mock.patch('wikitcms.wiki.Wiki.testtypes', ['Installation', 'Desktop', 'Server', 'Cloud', 'Base']).start()
mock.patch('wikitcms.wiki.Wiki.modular_testtypes', ['Installation', 'Server', 'Base']).start()
# login hits the wiki, obviously
mock.patch('wikitcms.wiki.Wiki.login', autospec=True).start()
# so does site init
mock.patch('mwclient.client.Site.site_init', autospec=True).start()

# this we need to switch at Branch point, so name it. It hits the
# 'collections' API.
fakecurrpatcher = mock.patch('fedfind.helpers.get_current_release', _fakegetcurr1)
fakecurrpatcher.start()

# proper consumer init requires a fedmsg hub instance, we don't have
# one and don't want to faff around faking one.
CONSUMER = None
with mock.patch('fedmsg.consumers.FedmsgConsumer.__init__', return_value=None):
    CONSUMER = relvalconsumer.RelvalProductionConsumer(None)

# These are all fake IDs for various composes, in the order we'll test them.
RAWHIDE1 = 'Fedora-Rawhide-20160601.n.0'
RAWHIDE2 = 'Fedora-Rawhide-20160601.n.1'
RAWHIDE3 = 'Fedora-Rawhide-20160605.n.0'
RAWHIDE4 = 'Fedora-Rawhide-20160620.n.0'
BRANCHED1 = 'Fedora-25-20160621.n.0'
BRANCHED2 = 'Fedora-25-20160629.n.0'
ALPHA1 = 'Fedora-25-20160629.0'
ALPHA2 = 'Fedora-25-20160629.1'
BRANCHED3 = 'Fedora-25-20160630.n.0'
BRANCHED4 = 'Fedora-25-20160705.n.0'
ALPHA3 = 'Fedora-25-20160706.0'
BRANCHED5 = 'Fedora-25-20160710.n.0'
RAWHIDE5 = 'Fedora-Rawhide-20160714.n.0'
BETA1 = 'Fedora-25-20160714.0'
FINAL1 = 'Fedora-25-20160721.1'
ATOMIC1 = 'Fedora-Atomic-25-20160725.1'
MODBRANCHED1 = 'Fedora-Modular-27-20171030.n.0'
MODBRANCHED2 = 'Fedora-Modular-27-20171031.n.0'
MODBRANCHED3 = 'Fedora-Modular-27-20171106.n.0'
MODBETA1 = 'Fedora-Modular-27-20171108.2'
MODBRANCHED4 = 'Fedora-Modular-27-20171125.n.0'
MODFINAL1 = 'Fedora-Modular-27-20171126.1'

# obviously we don't really want to create the event. we mock this
# separately for each test, instead of just once, to make the call
# asserts simple.
@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
# ditto sending emails.
@mock.patch('smtplib.SMTP', autospec=True)
# this obviously hits mirrors; we have a couple of functions for faking
# 'same' and 'different' package sets, for different tests
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetsame)
# this needs mocking when the current event is a ComposeEvent; it's
# used to figure out how many days it's been since 'current' event.
# For nightly events this doesn't need a remote trip, but for
# candidate events it does
@mock.patch('wikitcms.event.ComposeEvent.creation_date', '20160530')
# this always needs mocking, as whatever the 'current' event ought
# to be in our fake release series.
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.ComposeEvent(None, '24', 'Final', '1.4'))
def test_rawhide1(fakesmtp, fakecreate):
    """Creating first Rawhide nightly for next release."""
    CONSUMER.consume(_fakemsg(RAWHIDE1))
    assert fakecreate.call_args[1]['check'] is True

@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetdifferent)
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.NightlyEvent(None, '25', 'Rawhide', '20160601.n.0'))
def test_rawhide2(fakesmtp, fakecreate):
    """Another Rawhide nightly one day later should not produce an
    event, even if there are package differences.
    """
    CONSUMER.consume(_fakemsg(RAWHIDE2))
    assert fakecreate.call_count == 0
    assert fakesmtp.call_count == 0

@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetsame)
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.NightlyEvent(None, '25', 'Rawhide', '20160601.n.0'))
def test_rawhide3_same(fakesmtp, fakecreate):
    """Another Rawhide nightly four days later should not produce an
    event if the packages are the same...
    """
    CONSUMER.consume(_fakemsg(RAWHIDE3))
    assert fakecreate.call_count == 0
    assert fakesmtp.call_count == 0

@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetdifferent)
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.NightlyEvent(None, '25', 'Rawhide', '20160601.n.0'))
def test_rawhide3_different(fakesmtp, fakecreate):
    """...but the same four days later nightly should produce an
    event if the packages are different.
    """
    CONSUMER.consume(_fakemsg(RAWHIDE3))
    assert fakecreate.call_args[1]['check'] is True

@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetsame)
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.NightlyEvent(None, '25', 'Rawhide', '20160605.n.0'))
def test_rawhide4(fakesmtp, fakecreate):
    """Another Rawhide nightly 15 days later should produce an event
    even if the packages are the same.
    """
    CONSUMER.consume(_fakemsg(RAWHIDE4))
    assert fakecreate.call_args[1]['check'] is True

# BRANCH POINT

@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetsame)
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.NightlyEvent(None, '25', 'Rawhide', '20160620.n.0'))
def test_branched1(fakesmtp, fakecreate):
    """First Branched nightly shouldn't produce an event as it's only
    one day after the Rawhide nightly.
    """
    # switch the get_current_release mock to Branched mode
    fakecurrpatcher.stop() 
    mock.patch('fedfind.helpers.get_current_release', _fakegetcurr2).start()
    CONSUMER.consume(_fakemsg(BRANCHED1))
    assert fakecreate.call_count == 0
    assert fakesmtp.call_count == 0

@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetdifferent)
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.NightlyEvent(None, '25', 'Rawhide', '20160620.n.0'))
def test_branched2(fakesmtp, fakecreate):
    """Second branched compose some days later should create an event.
    """
    CONSUMER.consume(_fakemsg(BRANCHED2))
    assert fakecreate.call_args[1]['check'] is True

# this has to be mocked when the 'new' event is a production one;
# to find the correct event from the compose ID, wikitcms gets a
# Production instance from fedfind and checks its label property,
# then parses that
@mock.patch('fedfind.release.Production.label', 'Alpha-1.1')
@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetsame)
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.NightlyEvent(None, '25', 'Branched', '20160629.n.0'))
def test_alpha1(fakesmtp, fakecreate):
    """First Alpha candidate should produce an event even though it's
    for the same date and package set as BRANCHED2.
    """
    CONSUMER.consume(_fakemsg(ALPHA1))
    assert fakecreate.call_args[1]['check'] is True

# this has to be mocked whenever the current event is a candidate IDed
# by milestone and compose; wikitcms asks fedfind for the compose for
# the current event, fedfind will return a Compose if it exists.
@mock.patch('fedfind.release.Compose.exists', return_value=True)
@mock.patch('fedfind.release.Production.label', 'Alpha-1.2')
@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetsame)
@mock.patch('wikitcms.event.ComposeEvent.creation_date', '20160629')
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.ComposeEvent(None, '25', 'Alpha', '1.1'))
def test_alpha2(fakesmtp, fakecreate, fakecompexists):
    """Second Alpha candidate should produce an event even though it's
    for the same date and package set as ALPHA1 (somewhat unrealistic,
    but it's what ought to happen).
    """
    CONSUMER.consume(_fakemsg(ALPHA2))
    assert fakecreate.call_args[1]['check'] is True

@mock.patch('fedfind.release.Compose.exists', return_value=True)
@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetdifferent)
@mock.patch('wikitcms.event.ComposeEvent.creation_date', '20160629')
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.ComposeEvent(None, '25', 'Alpha', '1.2'))
def test_branched3(fakesmtp, fakecreate, fakecompexists):
    """Branched nightly shortly after candidate compose should not
    create event even if package set is different.
    """
    CONSUMER.consume(_fakemsg(BRANCHED3))
    assert fakecreate.call_count == 0
    assert fakesmtp.call_count == 0

@mock.patch('fedfind.release.Compose.exists', return_value=True)
@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetsame)
@mock.patch('wikitcms.event.ComposeEvent.creation_date', '20160629')
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.ComposeEvent(None, '25', 'Alpha', '1.2'))
def test_branched4_same(fakesmtp, fakecreate, fakecompexists):
    """Branched nightly a few days later with same package set should
    not create event...
    """
    CONSUMER.consume(_fakemsg(BRANCHED4))
    assert fakecreate.call_count == 0
    assert fakesmtp.call_count == 0

@mock.patch('fedfind.release.Compose.exists', return_value=True)
@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetolder)
@mock.patch('wikitcms.event.ComposeEvent.creation_date', '20160629')
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.ComposeEvent(None, '25', 'Alpha', '1.2'))
def test_branched4_older(fakesmtp, fakecreate, fakecompexists):
    """...nor should same few-days-later Branched nightly with *older*
    packages...
    """
    CONSUMER.consume(_fakemsg(BRANCHED4))
    assert fakecreate.call_count == 0
    assert fakesmtp.call_count == 0

@mock.patch('fedfind.release.Compose.exists', return_value=True)
@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetdifferent)
@mock.patch('wikitcms.event.ComposeEvent.creation_date', '20160629')
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.ComposeEvent(None, '25', 'Alpha', '1.2'))
def test_branched4_newer(fakesmtp, fakecreate, fakecompexists):
    """...but same few-days-later Branched nightly with newer
    packages should create event.
    """
    CONSUMER.consume(_fakemsg(BRANCHED4))
    assert fakecreate.call_args[1]['check'] is True

@mock.patch('fedfind.release.Production.label', 'Alpha-1.3')
@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetdifferent)
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.NightlyEvent(None, '25', 'Branched', '20160705.n.0'))
def test_alpha3(fakesmtp, fakecreate):
    """Another Alpha candidate came along! Event should be created
    even though it's only been one day.
    """
    CONSUMER.consume(_fakemsg(ALPHA3))
    assert fakecreate.call_args[1]['check'] is True

@mock.patch('fedfind.release.Compose.exists', return_value=True)
@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetdifferent)
@mock.patch('wikitcms.event.ComposeEvent.creation_date', '20160706')
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.ComposeEvent(None, '25', 'Alpha', '1.3'))
def test_branched5(fakesmtp, fakecreate, fakecompexists):
    """OK, say Alpha 1.3 went out as Alpha. Now another Branched
    comes along. This isn't testing anything new but I wanna go
    from Branched to Beta then Beta to Final. We should get an event
    here.
    """
    CONSUMER.consume(_fakemsg(BRANCHED5))
    assert fakecreate.call_args[1]['check'] is True

@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetdifferent)
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.NightlyEvent(None, '25', 'Branched', '20160710.n.0'))
def test_rawhide5(fakesmtp, fakecreate):
    """Meanwhile, a Rawhide compose shows up (this is a thing that
    happens all the time). We should NOT create any event for it -
    we never create events for the release after the next (i.e. for
    Rawhide when there is a Branched).
    """
    CONSUMER.consume(_fakemsg(RAWHIDE5))
    assert fakecreate.call_count == 0
    assert fakesmtp.call_count == 0

@mock.patch('fedfind.release.Production.label', 'Beta-1.1')
@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetdifferent)
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.NightlyEvent(None, '25', 'Branched', '20160710.n.0'))
def test_beta1(fakesmtp, fakecreate):
    """OK, here comes Beta. We should get an event, of course."""
    CONSUMER.consume(_fakemsg(BETA1))
    assert fakecreate.call_args[1]['check'] is True

@mock.patch('fedfind.release.Production.label', 'RC-1.1')
@mock.patch('fedfind.release.Compose.exists', return_value=True)
@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetdifferent)
@mock.patch('wikitcms.event.ComposeEvent.creation_date', '20160714')
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.ComposeEvent(None, '25', 'Beta', '1.1'))
def test_final1(fakesmtp, fakecreate, fakecompexists):
    """Finally, here comes Final! Testing going straight from one
    candidate compose to another milestone candidate compose, though
    this is unlikely ever to happen. We should get an event.
    """
    CONSUMER.consume(_fakemsg(FINAL1))
    #assert fakecreate.call_args[1]['check'] is True
    assert fakecreate.call_args[1]['check'] is True

@mock.patch('fedfind.release.Production.label', 'RC-20161120.0')
@mock.patch('fedfind.release.Compose.exists', return_value=True)
@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetdifferent)
@mock.patch('wikitcms.event.ComposeEvent.creation_date', '20160721')
@mock.patch('wikitcms.wiki.Wiki.current_event', wikitcms.event.ComposeEvent(None, '25', 'RC', '1.1'))
def test_atomic1(fakesmtp, fakecreate, fakecompexists):
    """We may get two-week Atomic composes for the release starting
    up before it goes final; make sure we don't get events for these.
    """
    CONSUMER.consume(_fakemsg(ATOMIC1))
    assert fakecreate.call_count == 0
    assert fakesmtp.call_count == 0

@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetdifferent)
@mock.patch('wikitcms.wiki.Wiki.current_modular_event', wikitcms.event.NightlyEvent(None, '27', 'Branched', '20171001.n.0', modular=True))
def test_modular_branched1(fakesmtp, fakecreate):
    """Now a Modular compose shows up! We should get an event."""
    CONSUMER.consume(_fakemsg(MODBRANCHED1))
    assert fakecreate.call_args[1]['check'] is True

@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetdifferent)
@mock.patch('wikitcms.wiki.Wiki.current_modular_event', wikitcms.event.NightlyEvent(None, '27', 'Branched', '20171030.n.0', modular=True))
def test_modular_branched2(fakesmtp, fakecreate):
    """Another compose the next day shouldn't produce an event even
    with different packages.
    """
    CONSUMER.consume(_fakemsg(MODBRANCHED2))
    assert fakecreate.call_count == 0
    assert fakesmtp.call_count == 0

@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetsame)
@mock.patch('wikitcms.wiki.Wiki.current_modular_event', wikitcms.event.NightlyEvent(None, '27', 'Branched', '20171030.n.0', modular=True))
def test_modular_branched3_same(fakesmtp, fakecreate):
    """Another compose a few days later with same packages shouldn't
    create an event...
    """
    CONSUMER.consume(_fakemsg(MODBRANCHED3))
    assert fakecreate.call_count == 0
    assert fakesmtp.call_count == 0

@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetdifferent)
@mock.patch('wikitcms.wiki.Wiki.current_modular_event', wikitcms.event.NightlyEvent(None, '27', 'Branched', '20171030.n.0', modular=True))
def test_modular_branched3_different(fakesmtp, fakecreate):
    """...but with different packages it should."""
    CONSUMER.consume(_fakemsg(MODBRANCHED3))
    assert fakecreate.call_args[1]['check'] is True

@mock.patch('fedfind.release.ModularProduction.label', 'Beta-1.1')
@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetsame)
@mock.patch('wikitcms.wiki.Wiki.current_modular_event', wikitcms.event.NightlyEvent(None, '27', 'Branched', '20171106.n.0', modular=True))
def test_modular_beta1(fakesmtp, fakecreate):
    """Now a Modular Beta compose appears; event should be created
    even though it's only a couple of days later and packages are
    the same.
    """
    CONSUMER.consume(_fakemsg(MODBETA1))
    assert fakecreate.call_args[1]['check'] is True

@mock.patch('fedfind.release.Compose.exists', return_value=True)
@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetsame)
@mock.patch('wikitcms.event.ComposeEvent.creation_date', '20171108')
@mock.patch('wikitcms.wiki.Wiki.current_modular_event', wikitcms.event.ComposeEvent(None, '27', 'Beta', '1.1', modular=True))
def test_modular_branched4(fakesmtp, fakecreate, fakecompexists):
    """A nightly more than 2 weeks after Beta creates an event, even
    with the same packages.
    """
    CONSUMER.consume(_fakemsg(MODBRANCHED4))
    assert fakecreate.call_args[1]['check'] is True

@mock.patch('fedfind.release.ModularProduction.label', 'Final-1.1')
@mock.patch('wikitcms.event.ValidationEvent.create', autospec=True)
@mock.patch('smtplib.SMTP', autospec=True)
@mock.patch('fedfind.release.Pungi4Release.get_package_nvras', _fakegetsame)
@mock.patch('wikitcms.wiki.Wiki.current_modular_event', wikitcms.event.NightlyEvent(None, '27', 'Branched', '20171125.n.0', modular=True))
def test_modular_final1(fakesmtp, fakecreate):
    """Modular Final appears; event should be created.
    """
    CONSUMER.consume(_fakemsg(MODFINAL1))
    assert fakecreate.call_args[1]['check'] is True

# vim: set textwidth=120 ts=8 et sw=4:
