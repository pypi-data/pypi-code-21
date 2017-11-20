# -*- coding: utf-8 -*-
"""Views."""
import json

from Products.Five.browser import BrowserView
from plone import api

from collective.querynextprev import QUERY, SEARCH_URL, NEXT_UIDS, PREVIOUS_UIDS  # noqa #pylint: disable=C0301
from collective.querynextprev.utils import (
    expire_session_data, first_common_item, get_previous_items, get_next_items,
    convert_to_str)


class GoToNextItem(BrowserView):

    """Redirect to next item in query."""

    uids_param = NEXT_UIDS

    def get_uids(self):
        """Get uids of the query results."""
        catalog = api.portal.get_tool('portal_catalog')
        params = convert_to_str(json.loads(self.request.SESSION[QUERY]))
        return [brain.UID for brain in catalog.searchResults(**params)]  # noqa #pylint: disable=E1103

    def __call__(self):
        request = self.request
        session = request.SESSION
        if session.has_key(QUERY) and session.has_key(self.uids_param):  # noqa
            next_uids = convert_to_str(json.loads(session[self.uids_param]))

            # reexecute the query to search within most recent results
            new_uids = self.get_uids()

            # search UID starting from context index in uids
            uid = first_common_item(next_uids, new_uids)
            if uid is not None:
                next_url = api.content.get(UID=uid).absolute_url()

                # update uids in session
                index = new_uids.index(uid)
                previous_uids = list(reversed(
                    get_previous_items(new_uids, index)))
                next_uids = get_next_items(new_uids, index)
                session[PREVIOUS_UIDS] = json.dumps(previous_uids)
                session[NEXT_UIDS] = json.dumps(next_uids)

                request.response.redirect(next_url)
                return  # don't expire session data

        if session.has_key(SEARCH_URL):  # noqa
            request.response.redirect(session[SEARCH_URL])
        else:
            request.response.redirect(api.portal.get().absolute_url())

        expire_session_data(request)
        return


class GoToPreviousItem(GoToNextItem):

    """Redirect to previous item in query."""

    uids_param = PREVIOUS_UIDS

    def get_uids(self):
        """Reverse uids."""
        uids = super(GoToPreviousItem, self).get_uids()
        uids.reverse()
        return uids
