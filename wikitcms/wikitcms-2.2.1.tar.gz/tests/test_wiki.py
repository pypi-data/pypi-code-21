# Copyright (C) 2016 Red Hat
#
# This file is part of wikitcms.
#
# wikitcms is free software; you can redistribute it and/or modify
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

"""Tests for wiki.py."""

from __future__ import unicode_literals
from __future__ import print_function

# note: we need the external 'mock', unittest.mock does not seem to
# work correctly with the @patch decorator still
import mock
import pytest
import wikitcms.wiki as wk
import wikitcms.event
import wikitcms.result

FAKE_CURRENT_COMPOSE = """{{tempdoc}}
<onlyinclude>{{#switch: {{{1|full}}}
| full = 24 Alpha 1.1
| release = 24
| milestone = Alpha
| compose = 1.1
| date =
}}</onlyinclude>
[[Category: Fedora Templates]]
"""

class FakeRow(object):
    """This is a very bare fake ResultRow class; we need it to fully
    test report_validation_results, can't really do it with Mocks. We
    use mock to replace the 'real' page.find_resultrow method with the
    fake_findrow method below, which returns instances of this class.
    """
    def __init__(self, name):
        self.name = name

    def matches(self, other):
        return self.name == other.name

def fake_findrow(self, testcase='', section='', testname='', env=''):
    """This is a fake find_resultrow function which just returns
    FakeRows based on the values it's given. We use mock to replace
    Page instances' find_resultrow methods with this, further down.
    Note we're simulating a case where the found row covers both
    reported envs here; find_resultrow can also cover a case where
    there are two rows with equal case, section and name but each
    covering different envs, but we'll test that in its own test.
    """
    name = '.'.join((testcase, section, testname))
    return FakeRow(name)

class TestWiki:
    """Tests for the functions in wiki.py."""
    # the 'fjajah' is just to make sure we're running offline; if I
    # screw up and add a test that hits the network it'll cause the
    # tests to hang/fail instead of succeeding a bit slower
    site = wk.Wiki('fjajah', do_init=False, force_login=False)

    @mock.patch('mwclient.page.Page.__init__', return_value=None)
    @mock.patch('mwclient.page.Page.text', return_value=FAKE_CURRENT_COMPOSE)
    def test_current_compose(self, faketext, fakeinit):
        assert self.site.current_compose == {'full': '24 Alpha 1.1', 'release': '24', 'milestone': 'Alpha', 'compose': '1.1', 'date': ''}
        assert self.site.current_modular_compose == {'full': '24 Alpha 1.1', 'release': '24', 'milestone': 'Alpha', 'compose': '1.1', 'date': ''}

    @mock.patch('mwclient.page.Page.__init__', return_value=None)
    @mock.patch('mwclient.page.Page.text', return_value=FAKE_CURRENT_COMPOSE)
    @mock.patch('wikitcms.wiki.Wiki.get_validation_event', autospec=True)
    def test_current_event(self, fakeget, faketext, fakeinit):
        ret = self.site.current_event
        fakeget.assert_called_with(mock.ANY, compose='1.1', milestone='Alpha', release='24')
        fakeget.reset_mock()
        ret = self.site.current_modular_event
        fakeget.assert_called_with(mock.ANY, compose='1.1', milestone='Alpha', release='24', modular=True)

    @mock.patch('mwclient.page.Page.__init__', return_value=None)
    @mock.patch('mwclient.page.Page.text', return_value='foobar')
    @mock.patch('mwclient.page.Page.save')
    def test_add_to_category(self, fakesave, faketext, fakeinit):
        self.site.add_to_category('Foobar', 'Category:Some category', 'summary')
        fakesave.assert_called_with('foobar\n[[Category:Some category]]', 'summary', createonly=False)

    @mock.patch('mwclient.page.Page.__init__', return_value=None)
    @mock.patch('mwclient.page.Page.text', return_value=FAKE_CURRENT_COMPOSE)
    @mock.patch('wikitcms.event.NightlyEvent', autospec=True)
    @mock.patch('wikitcms.event.ComposeEvent', autospec=True)
    def test_get_validation_event(self, fakecompose, fakenightly, faketext, fakeinit):
        # current event
        ret = self.site.get_validation_event()
        fakecompose.assert_called_with(self.site, '24', 'Alpha', '1.1', modular=False)
        ret = self.site.get_validation_event(modular=True)
        fakecompose.assert_called_with(self.site, '24', 'Alpha', '1.1', modular=True)
        # old-school TC/RC
        ret = self.site.get_validation_event(23, 'Final', 'TC9')
        fakecompose.assert_called_with(self.site, 23, 'Final', 'TC9', modular=False)
        ret = self.site.get_validation_event(23, 'Beta', 'RC1')
        fakecompose.assert_called_with(self.site, 23, 'Beta', 'RC1', modular=False)
        # old-school nightly
        ret = self.site.get_validation_event(23, 'Rawhide', '20151112')
        fakenightly.assert_called_with(
            self.site, release=23, milestone='Rawhide', compose='20151112', modular=False)
        ret = self.site.get_validation_event(23, 'Branched', '20151211', modular=False)
        fakenightly.assert_called_with(
            self.site, release=23, milestone='Branched', compose='20151211', modular=False)
        # Pungi 4 production/candidate
        ret = self.site.get_validation_event(24, 'Alpha', '1.1')
        fakecompose.assert_called_with(self.site, 24, 'Alpha', '1.1', modular=False)
        ret = self.site.get_validation_event(27, 'Beta', '1.5', modular=True)
        fakecompose.assert_called_with(self.site, 27, 'Beta', '1.5', modular=True)
        # Past 23, 'Final' milestone should be converted to 'RC'
        ret = self.site.get_validation_event(25, 'Final', '1.1')
        fakecompose.assert_called_with(self.site, 25, 'RC', '1.1', modular=False)
        # Pungi 4 nightly
        ret = self.site.get_validation_event(24, 'Rawhide', '20160222.n.0')
        fakenightly.assert_called_with(
            self.site, release=24, milestone='Rawhide', compose='20160222.n.0', modular=False)
        ret = self.site.get_validation_event(24, 'Branched', '20160315.n.1')
        fakenightly.assert_called_with(
            self.site, release=24, milestone='Branched', compose='20160315.n.1', modular=False)
        ret = self.site.get_validation_event(27, 'Branched', '20171110.n.1', modular=True)
        fakenightly.assert_called_with(
            self.site, release=27, milestone='Branched', compose='20171110.n.1', modular=True)

        with pytest.raises(ValueError):
            # Non-nightly compose but no milestone
            self.site.get_validation_event(24, '', '1.1')
            # Invalid composes
            self.site.get_validation_event(24, 'Branched', 'foobar')
            self.site.get_validation_event(24, 'Branched', 'TC1a')
            self.site.get_validation_event(24, 'Branched', '1.1a')
            # looks kinda like a date but is not one
            self.site.get_validation_event(24, 'Branched', '20161356')
            self.site.get_validation_event(24, 'Branched', '20161356.n.0')
            # invalid type
            self.site.get_validation_event(24, 'Branched', '20160314.x.0')

    @mock.patch('wikitcms.event.NightlyEvent.__init__', return_value=None, autospec=True)
    @mock.patch('wikitcms.event.NightlyEvent.result_pages', [mock.Mock(**{'text.return_value': 'foobar'})])
    def test_get_validation_event_guess_nightly(self, fakeinit):
        # We can't quite test this fully as we can't patch the Branched
        # event to not be found but the Rawhide event to be found
        ret = self.site.get_validation_event(24, '', '20160314.n.0')
        assert isinstance(ret, wikitcms.event.NightlyEvent)

    @mock.patch('mwclient.page.Page.__init__', return_value=None, autospec=True)
    @mock.patch('mwclient.page.Page.text', return_value=FAKE_CURRENT_COMPOSE)
    @mock.patch('wikitcms.page.NightlyPage', autospec=True)
    @mock.patch('wikitcms.page.ComposePage', autospec=True)
    def test_get_validation_page(self, fakecompose, fakenightly, faketext, fakeinit):
        # current event
        ret = self.site.get_validation_page('Installation')
        fakecompose.assert_called_with(
            self.site, '24', 'Installation', 'Alpha', '1.1', modular=False)
        # old-school TC/RC
        ret = self.site.get_validation_page('Installation', 23, 'Final', 'TC9')
        fakecompose.assert_called_with(self.site, 23, 'Installation', 'Final', 'TC9', modular=False)
        ret = self.site.get_validation_page('Installation', 23, 'Beta', 'RC1')
        fakecompose.assert_called_with(self.site, 23, 'Installation', 'Beta', 'RC1', modular=False)
        # old-school nightly
        ret = self.site.get_validation_page('Installation', 23, 'Rawhide', '20151112')
        fakenightly.assert_called_with(
            self.site, 23, 'Installation', 'Rawhide', '20151112', modular=False)
        ret = self.site.get_validation_page('Installation', 23, 'Branched', '20151211')
        fakenightly.assert_called_with(
            self.site, 23, 'Installation', 'Branched', '20151211', modular=False)
        # Pungi 4 production/candidate
        ret = self.site.get_validation_page('Installation', 24, 'Alpha', '1.1')
        fakecompose.assert_called_with(self.site, 24, 'Installation', 'Alpha', '1.1', modular=False)
        ret = self.site.get_validation_page('Installation', 27, 'Beta', '1.5', modular=True)
        fakecompose.assert_called_with(self.site, 27, 'Installation', 'Beta', '1.5', modular=True)
        # Past 23, 'Final' milestone should be converted to 'RC'
        ret = self.site.get_validation_page('Installation', 25, 'Final', '1.1')
        fakecompose.assert_called_with(self.site, 25, 'Installation', 'RC', '1.1', modular=False)
        # Pungi 4 nightly
        ret = self.site.get_validation_page('Installation', 24, 'Rawhide', '20160222.n.0')
        fakenightly.assert_called_with(
            self.site, 24, 'Installation', 'Rawhide', '20160222.n.0', modular=False)
        ret = self.site.get_validation_page('Installation', 24, 'Branched', '20160315.n.1')
        fakenightly.assert_called_with(
            self.site, 24, 'Installation', 'Branched', '20160315.n.1', modular=False)
        ret = self.site.get_validation_page(
            'Installation', 27, 'Branched', '20171110.n.1', modular=True)
        fakenightly.assert_called_with(
            self.site, 27, 'Installation', 'Branched', '20171110.n.1', modular=True)

        with pytest.raises(ValueError):
            # Non-nightly compose but no milestone
            self.site.get_validation_page('Installation', 24, '', '1.1')
            # Invalid composes
            self.site.get_validation_page('Installation', 24, 'Branched', 'foobar')
            self.site.get_validation_page('Installation', 24, 'Branched', 'TC1a')
            self.site.get_validation_page('Installation', 24, 'Branched', '1.1a')
            # looks kinda like a date but is not one
            self.site.get_validation_page('Installation', 24, 'Branched', '20161356')
            self.site.get_validation_page('Installation', 24, 'Branched', '20161356.n.0')
            # invalid type
            self.site.get_validation_page('Installation', 24, 'Branched', '20160314.x.0')

    @mock.patch('wikitcms.page.NightlyPage.__init__', return_value=None, autospec=True)
    @mock.patch('wikitcms.page.NightlyPage.exists', True, create=True)
    def test_get_validation_page_guess_nightly(self, fakeinit):
        # We can't quite test this fully as we can't patch the Branched
        # page to not be found but the Rawhide page to be found
        ret = self.site.get_validation_page('Installation', 24, '', '20160314.n.0')
        assert isinstance(ret, wikitcms.page.NightlyPage)

    # we use the find_resultrow and ResultRow dummies from the top of the file here
    @mock.patch('wikitcms.page.NightlyPage.__init__', return_value=None, autospec=True)
    @mock.patch('wikitcms.page.ComposePage.__init__', return_value=None, autospec=True)
    @mock.patch('wikitcms.page.NightlyPage.find_resultrow', fake_findrow)
    @mock.patch('wikitcms.page.ComposePage.find_resultrow', fake_findrow)
    @mock.patch('wikitcms.page.NightlyPage.add_results', autospec=True)
    @mock.patch('wikitcms.page.ComposePage.add_results', autospec=True)
    def test_report_validation_results(self, fakecompose, fakenightly, fakecompinit, fakenightinit):
        restups = [
            wk.ResTuple('Installation', '24', 'Alpha', '1.1', 'QA:Testcase_foo', status='pass',
                        user='adamwill'),
            wk.ResTuple('Installation', '24', 'Alpha', '1.1', 'QA:Testcase_bar', status='pass',
                        user='adamwill', section='testsec', env='testenv1'),
            wk.ResTuple('Installation', '24', 'Alpha', '1.1', 'QA:Testcase_bar', status='pass',
                        user='adamwill', section='testsec', env='testenv2'),
            wk.ResTuple('Installation', '24', 'Branched', '20160314.n.1', 'QA:Testcase_foo', status='pass',
                        user='adamwill'),
            wk.ResTuple('Installation', '24', 'Branched', '20160314.n.1', 'QA:Testcase_bar', status='pass',
                        user='adamwill', section='testsec', env='testenv1'),
            wk.ResTuple('Installation', '24', 'Branched', '20160314.n.1', 'QA:Testcase_bar', status='pass',
                        user='adamwill', section='testsec', env='testenv2')
            ]
        self.site.report_validation_results(restups)
        # this ought to call add_results once for each page.
        for fake in (fakecompose, fakenightly):
            assert len(fake.call_args_list) == 1
            compargs = fake.call_args
            # compargs[0] is all args as a list, add_results takes a single arg which is the resdict
            # first item is self (when autospec is used)
            resdict = compargs[0][1]
            # resdict should have exactly two entries, one per test instance
            assert len(resdict) == 2
            # we're going to sort the dict items for ease of testing.
            items = sorted(list(resdict.items()), key=lambda x: x[0].name, reverse=True)
            # first resdict entry: should be for the 'foo' test case...
            (key, value) = items[0]
            assert key.name == 'QA:Testcase_foo..'
            # ...and value should be a 1-item list of a single 2-tuple, env '', result a Result instance
            assert len(value) == 1
            (env, res) = value[0]
            assert env == ''
            assert isinstance(res, wikitcms.result.Result)
            (key, value) = items[1]
            # second resdict entry: should be for the 'bar' test case with section name...
            assert key.name == 'QA:Testcase_bar.testsec.'
            # ... and value should be a 2-item list of 2-tuples, differing in the environment
            assert len(value) == 2
            (env1, res) = value[0]
            assert env1 == 'testenv1'
            assert isinstance(res, wikitcms.result.Result)
            (env1, res) = value[1]
            assert env1 == 'testenv2'
            assert isinstance(res, wikitcms.result.Result)

# vim: set textwidth=100 ts=8 et sw=4:
