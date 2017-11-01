import html

from aionationstates.utils import normalize, timestamp
from aionationstates.types import (
    EmbassyPostingRights, Officer, Authority, Embassies, Poll)
from aionationstates.session import Session, api_query
from aionationstates.shards import NationRegion
import aionationstates


class Region(NationRegion, Session):
    """A class to interact with the NationStates Region API.

    Attributes
    ----------
    id : str
        The defining characteristic of a region, its normalized name.
        No two regions share the same id, and no one id is shared by
        multiple regions.
    """

    def __init__(self, name):
        self.id = normalize(name)

    def _call_api(self, params, *args, **kwargs):
        params['region'] = self.id
        return super()._call_api(*args, params=params, **kwargs)


    @property
    def url(self):
        """str: URL of the region."""
        return f'https://www.nationstates.net/region={self.id}'

    @api_query('name')
    async def name(self, root):
        """Name of the region, with proper capitalization.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('NAME').text

    @api_query('flag')
    async def flag(self, root):
        """URL of the region's flag.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('FLAG').text

    @api_query('factbook')
    async def factbook(self, root):
        """Region's World Factbook Entry.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        # This lib might have been a mistake, but the line below
        # definitely isn't.
        return html.unescape(html.unescape(root.find('FACTBOOK').text))

    @api_query('power')
    async def power(self, root):
        """An adjective describing region's power on the interregional
        scene.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('POWER').text

    @api_query('delegatevotes')
    async def delegatevotes(self, root):
        """Number of the World Assembly votes the region's Delegate
        has.

        Returns
        -------
        an :class:`ApiQuery` of int
        """
        return int(root.find('DELEGATEVOTES').text)

    @api_query('numnations')
    async def numnations(self, root):
        """The number of nations in the region.

        Returns
        -------
        an :class:`ApiQuery` of int
        """
        return int(root.find('NUMNATIONS').text)

    @api_query('foundedtime')
    async def founded(self, root):
        """When the region was founded.

        Returns
        -------
        an :class:`ApiQuery` of a naive UTC :class:`datetime.datetime`
        """
        return timestamp(root.find('FOUNDEDTIME'))

    @api_query('nations')
    async def nations(self, root):
        """All the nations in the region.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Nation` objects
        """
        text = root.find('NATIONS').text
        return ([aionationstates.Nation(n) for n in text.split(':')]
                if text else [])

    @api_query('embassies')
    async def embassies(self, root):
        """Embassies the region has.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Embassies`
        """
        return Embassies(root.find('EMBASSIES'))

    @api_query('embassyrmb')
    async def embassyrmb(self, root):
        """Posting rights for members the of embassy regions.

        Returns
        -------
        an :class:`ApiQuery` of :class:`EmbassyPostingRights`
        """
        return EmbassyPostingRights._from_ns(root.find('EMBASSYRMB').text)

    @api_query('delegate')
    async def delegate(self, root):
        """Regional World Assembly Delegate.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Nation`
        an :class:`ApiQuery` of None
            If the region has no delegate.
        """
        nation = root.find('DELEGATE').text
        if nation == '0':
            return None
        return aionationstates.Nation(nation)

    @api_query('delegateauth')
    async def delegateauth(self, root):
        """Regional World Assembly Delegate's authority.  Always set,
        no matter if the region has a delegate or not.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Authority`
        """
        return Authority._from_ns(root.find('DELEGATEAUTH').text)

    @api_query('founder')
    async def founder(self, root):
        """Regional Founder.  Returned even if the nation has ceased to
        exist.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Nation`
        an :class:`ApiQuery` of None
          If the region is Game-Created and doesn't have a founder.
        """
        nation = root.find('FOUNDER').text
        if nation == '0':
            return None
        return aionationstates.Nation(nation)

    @api_query('founderauth')
    async def founderauth(self, root):
        """Regional Founder's authority.  Always set,
        no matter if the region has a founder or not.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Authority`
        """
        return Authority._from_ns(root.find('FOUNDERAUTH').text)

    @api_query('officers')
    async def officers(self, root):
        """Regional Officers.  Does not include the Founder or
        the Delegate, unless they have additional litles as Officers.
        In the correct order.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Officer`
        """
        officers = sorted(
            root.find('OFFICERS'),
            # I struggle to say what else this tag would be useful for.
            key=lambda elem: int(elem.find('ORDER').text)
        )
        return [Officer(elem) for elem in officers]

    @api_query('tags')
    async def tags(self, root):
        """Tags the region has.

        Returns
        -------
        an :class:`ApiQuery` of a list of str
        """
        return [elem.text for elem in root.find('TAGS')]

    @api_query('poll')
    async def poll(self, root):
        """Current regional poll.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Poll`
        """
        elem = root.find('POLL')
        return Poll(elem) if elem else None

    # TODO: history, messages
