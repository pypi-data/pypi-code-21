# Copyright (C) 2014 Red Hat
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

"""Classes that describe test events."""

from __future__ import unicode_literals
from __future__ import print_function

import abc
import logging

import fedfind.helpers
import fedfind.release
import mwclient.errors
from cached_property import cached_property

from . import listing
from . import page
from . import helpers

logger = logging.getLogger(__name__)


class ValidationEvent(object):
    """A parent class for different types of release validation event.
    site must be an instance of wikitcms.Wiki, already with
    appropriate access rights for any actions to be performed (i.e.
    things instantiating an Event are expected to do site.login
    themselves if needed). Required attributes: shortver,
    category_page. If modular is True, the event will be for a
    Fedora-Modular compose, with 'Modular' in the page names, category
    names and so on.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, site, release, milestone='', compose='', modular=False):
        self.site = site
        self.release = release
        self.milestone = str(milestone)
        try:
            self.compose = fedfind.helpers.date_check(
                compose, fail_raise=True, out='str')
        except ValueError:
            self.compose = str(compose)
        self.modular = modular
        self.version = "{0} {1} {2}".format(
            self.release, self.milestone, self.compose)
        # Sorting helpers. sortname is a string, sorttuple is a
        # 4-tuple. sorttuple is more reliable. See the function docs.
        self.sortname = helpers.fedora_release_sort(self.version)
        self.sorttuple = helpers.triplet_sort(
            self.release, self.milestone, self.compose)

    @abc.abstractproperty
    def _current_content(self):
        """The content for the CurrentFedoraCompose template for
        this test event.
        """
        pass

    @abc.abstractproperty
    def _pagetype(self):
        """The ValidationPage class to be used for this event's pages
        (for use by valid_pages).
        """
        pass

    @abc.abstractproperty
    def category_page(self):
        """The category page for this event. Is a property because
        page instantiation requires a remote trip.
        """
        pass

    @property
    def result_pages(self):
        """A list of wikitcms page objects for currently-existing
        pages that are a part of this test event, according to the
        naming convention.
        """
        _dist = "Fedora"
        if self.modular:
            _dist = "Fedora Modular"
        pages = self.site.allresults(
            prefix="{0} {1} ".format(_dist, self.version))
        return [p for p in pages if isinstance(p, page.ValidationPage)]

    @property
    def download_page(self):
        """The DownloadPage for this event. Is a property because page
        instantiation requires a remote trip.
        """
        return page.DownloadPage(self.site, self, modular=self.modular)

    @property
    def parent_category_page(self):
        """The parent category page for this event. Is a property for
        the same reason as download_page.
        """
        return listing.ValidationCategory(self.site, self.release, modular=self.modular)

    @property
    def valid_pages(self):
        """A list of the expected possible result pages (as
        page.ValidationPage objects) for this test event, derived from
        the available test types and the naming convention.
        """
        if self.modular:
            types = self.site.modular_testtypes
        else:
            types = self.site.testtypes
        return [self._pagetype(self.site, self.release, typ,
                               milestone=self.milestone,
                               compose=self.compose, modular=self.modular)
                for typ in types]

    @property
    def summary_page(self):
        """The page.SummaryPage object for the event's result summary
        page. Very simple property, but not set in __init__ as the
        summary page object does (slow) wiki roundtrips in  __init__.
        """
        return page.SummaryPage(self.site, self, modular=self.modular)

    @cached_property
    def ff_release(self):
        """A fedfind release object matching this event."""
        # note: fedfind has a hack that parses date and respin out
        # of a dot-separated compose, since wikitcms smooshes them
        # into the compose value. Also note that *this will fail*
        # for ComposeEvents in the short time after the relevant
        # compose is finished but before it is imported to PDC and/or
        # synced to stage.
        dist = "Fedora"
        if self.modular:
            dist = "Fedora-Modular"
        return fedfind.release.get_release(release=self.release,
                                           milestone=self.milestone,
                                           compose=self.compose,
                                           dist=dist)

    def update_current(self):
        """Make the CurrentFedoraCompose template on the wiki point to
        this event. The template is used for the Current (testtype)
        Test redirect pages which let testers find the current results
        pages, and for other features of wikitcms/relval. Children
        must define _current_content.
        """
        content = "{{tempdoc}}\n<onlyinclude>{{#switch: {{{1|full}}}\n"
        content += self._current_content
        content += "}}</onlyinclude>\n[[Category: Fedora Templates]]"
        if self.modular:
            curr = self.site.pages['Template:CurrentFedoraModularCompose']
        else:
            curr = self.site.pages['Template:CurrentFedoraCompose']
        curr.save(content, "relval: update to current event", createonly=None)

    def create(self, testtypes=None, force=False, current=True, check=False):
        """Create the event, by creating its validation pages,
        summary page, download page, category pages, and updating the
        current redirects. 'testtypes' can be an iterable that limits
        creation to the specified testtypes. If 'force' is True, pages
        that already exist will be recreated (destroying any results
        on them). If 'current' is False, the current redirect pages
        will not be updated. If 'check' is true, we check if any
        result page already exists first, and bail immediately if so
        (so we don't start creating pages then hit one that exists and
        fail half-way through, for things that don't want that.) 'cid'
        can be set to a compose ID, this is for forcing the compose
        location at event creation time when we know we're not going
        to be able to find it any way and is a short-term hack that
        will be removed.
        """
        logger.info("Creating validation event %s", self.version)
        createonly = True
        if force:
            createonly = None
        pages = self.valid_pages
        if testtypes:
            logger.debug("Restricting to testtypes %s", ' '.join(testtypes))
            pages = [pag for pag in pages if pag.testtype in testtypes]
        if not pages:
            raise ValueError("No result pages to create! Wrong test type?")
        if check:
            if any(pag.text() for pag in pages):
                raise ValueError("A result page already exists!")

        # NOTE: download page creation for ComposeEvents ultimately
        # relies on the compose either being synced to stage or being
        # imported to PDC. If you try to create a ComposeEvent before
        # the compose is imported to PDC or synced to stage, it will
        # not go well. relvalconsumer waits for PDC.
        pages.extend((self.summary_page, self.download_page,
                      self.category_page, self.parent_category_page))

        def _handle_existing(err):
            """We need this in two places, so."""
            if err.args[0] == 'articleexists':
                # no problem, just move on.
                logger.info("Page already exists, and forced write was not "
                            "requested! Not writing.")
            else:
                raise err

        for pag in pages:
            try:
                logger.info("Creating page %s", pag.name)
                pag.write(createonly=createonly)
                if current:
                    pag.update_current()
            except mwclient.errors.APIError as err:
                _handle_existing(err)
            except AttributeError:
                # not all pages have update_current. this is fine.
                pass
        if current:
            try:
                self.update_current()
            except mwclient.errors.APIError as err:
                _handle_existing(err)

    @classmethod
    def from_page(cls, pageobj):
        """Return the ValidationEvent object for a given ValidationPage
        object.
        """
        return cls(pageobj.site, pageobj.release, pageobj.milestone,
                   pageobj.compose, modular=pageobj.modular)


class ComposeEvent(ValidationEvent):
    """An Event that describes a release validation event - that is,
    the testing for a particular nightly, test compose or release
    candidate build.
    """
    def __init__(self, site, release, milestone, compose, modular=False):
        super(ComposeEvent, self).__init__(
            site, release, milestone=milestone, compose=compose, modular=modular)
        self.shortver = "{0} {1}".format(self.milestone, self.compose)

    @property
    def category_page(self):
        """The category page for this event. Is a property because
        page instantiation requires a remote trip.
        """
        return listing.ValidationCategory(
            self.site, self.release, self.milestone, modular=self.modular)

    @property
    def _current_content(self):
        """The content for the CurrentFedoraCompose template for
        this test event.
        """
        tmpl = ("| full = {0}\n| release = {1}\n| milestone = {2}\n"
                "| compose = {3}\n| date =\n")
        return tmpl.format(
            self.version, self.release, self.milestone, self.compose)

    @property
    def _pagetype(self):
        """For a ComposeEvent, obviously, ComposePage."""
        return page.ComposePage

    @cached_property
    def creation_date(self):
        """We need this for ordering and determining delta between
        this event and a potential new nightly event, if this is the
        current event. Return creation date of the first result page
        for the event, or "" if it doesn't exist.
        """
        try:
            return self.result_pages[0].creation_date
        except IndexError:
            # event doesn't exist
            return ""


class NightlyEvent(ValidationEvent):
    """An Event that describes a release validation event - that is,
    the testing for a particular nightly, test compose or release
    candidate build. Milestone should be 'Rawhide' or 'Branched'.
    Note that a Fedora release number attached to a Rawhide nightly
    compose is an artificial concept that can be considered a Wikitcms
    artifact. Rawhide is a rolling distribution; its nightly composes
    do not really have a release number. What we do when we attach
    a release number to a Rawhide nightly validation test event is
    *declare* that, with our knowledge of Fedora's development cycle,
    we believe the testing of that Rawhide nightly constitutes a part
    of the release validation testing for that future release.
    """
    def __init__(self, site, release, milestone, compose, modular=False):
        super(NightlyEvent, self).__init__(
            site, release, milestone=milestone, compose=compose, modular=modular)
        self.shortver = self.compose
        self.creation_date = compose.split('.')[0]

    @property
    def category_page(self):
        """The category page for this event. Is a property because
        page instantiation requires a remote trip.
        """
        return listing.ValidationCategory(
            self.site, self.release, nightly=True, modular=self.modular)

    @property
    def _current_content(self):
        """The content for the CurrentFedoraCompose template for
        this test event.
        """
        tmpl = ("| full = {0}\n| release = {1}\n| milestone = {2}\n"
                "| compose =\n| date = {3}\n")
        return tmpl.format(
            self.version, self.release, self.milestone, self.compose)

    @property
    def _pagetype(self):
        """For a NightlyEvent, obviously, NightlyPage."""
        return page.NightlyPage

# vim: set textwidth=100 ts=8 et sw=4:
