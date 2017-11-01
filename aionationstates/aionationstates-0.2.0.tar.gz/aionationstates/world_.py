from contextlib import suppress
from asyncio import sleep

from aionationstates.session import Session, api_query
from aionationstates.types import Dispatch, Poll
from aionationstates.happenings import process_happening
from aionationstates.shards import Census
from aionationstates.ns_to_human import dispatch_categories, happening_filters
from aionationstates.utils import utc_seconds, normalize
import aionationstates


class World(Census, Session):
    """Interface to the NationStates World API."""

    @api_query('featuredregion')
    async def featuredregion(self, root):
        """Today's featured region.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Region`
        """
        return aionationstates.Region(root.find('FEATUREDREGION').text)

    @api_query('newnations')
    async def newnations(self, root):
        """Most recently founded nations, from newest.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Nation`
        """
        return [aionationstates.Nation(n)
                for n in root.find('NEWNATIONS').text.split(',')]

    @api_query('nations')
    async def nations(self, root):
        """List of all the nations, seemingly in order of creation.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Nation`
        """
        return [aionationstates.Nation(n)
                for n in root.find('NATIONS').text.split(',')]

    @api_query('numnations')
    async def numnations(self, root):
        """Total number of nations in the game.

        Returns
        -------
        an :class:`ApiQuery` of int
        """
        return int(root.find('NUMNATIONS').text)

    @api_query('regions')
    async def regions(self, root):
        """List of all the regions, seemingly in order of creation.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Region`
        """
        return [aionationstates.Region(r)
                for r in root.find('REGIONS').text.split(',')]

    @api_query('numregions')
    async def numregions(self, root):
        """Total number of regions in the game.

        Returns
        -------
        an :class:`ApiQuery` of int
        """
        return int(root.find('NUMREGIONS').text)

    def regionsbytag(self, *tags):
        """All regions belonging to any of the named tags.

        Parameters
        ----------
        *tags : str
            Regional tags.  Can be preceded by a ``-`` to select regions
            without that tag.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Region`
        """
        if len(tags) > 10:
            raise ValueError('You can specify up to 10 tags')
        if not tags:
            raise ValueError('No tags specified')
        # We don't check for invalid tags here because the behaviour is
        # fairly intuitive - quering for a non-existent tag returns no
        # regions, excluding it returns all of them.
        @api_query('regionsbytag', tags=','.join(tags))
        async def result(_, root):
            text = root.find('REGIONS').text
            return ([aionationstates.Region(r) for r in text.split(',')]
                    if text else [])
        return result(self)

    def dispatch(self, id):
        """Dispatch by id.

        Parameters
        ----------
        id : int
            Dispatch id.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Dispatch`
            Full dispatch (with text).
        """
        @api_query('dispatch', dispatchid=str(id))
        async def result(_, root):
            elem = root.find('DISPATCH')
            if not elem:
                raise ValueError(f'No dispatch found with id {id}')
            return Dispatch(elem)
        return result(self)

    def dispatchlist(self, *, author=None, category=None,
                     subcategory=None, sort='new'):
        """Find dispatches by certain criteria.

        Parameters
        ----------
        author : str
            Name of the nation authoring the dispatch.
        category : str
            Dispatch's primary category.
        subcategory : str
            Dispatch's secondary category.
        sort : str
            Sort order, 'new' or 'best'.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Dispatch`
            Dispatch "thumbnails", missing text.
        """
        params = {'sort': sort}
        if author:
            params['dispatchauthor'] = author
        # Here we do need to ensure that our categories are valid, cause
        # NS just ignores the categories it doesn't recognise and returns
        # whatever it feels like.
        if category and subcategory:
            if (category not in dispatch_categories or
                    subcategory not in dispatch_categories[category]):
                raise ValueError('Invalid category/subcategory')
            params['dispatchcategory'] = f'{category}:{subcategory}'
        elif category:
            if category not in dispatch_categories:
                raise ValueError('Invalid category')
            params['dispatchcategory'] = category
        else:
            raise ValueError('Cannot request subcategory without category')

        @api_query('dispatchlist', **params)
        async def result(_, root):
            return [
                Dispatch(elem)
                for elem in root.find('DISPATCHLIST')
            ]
        return result(self)

    def poll(self, id):
        """Poll with a given id.

        Parameters
        ----------
        id : int
            Poll id.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Poll`
        """
        @api_query('poll', pollid=str(id))
        async def result(_, root):
            elem = root.find('POLL')
            if not elem:
                raise ValueError(f'No poll found with id {id}')
            return Poll(elem)
        return result(self)

    # Happenings interface:

    def _get_happenings(self, *, nations, regions, filters, limit=100,
                        beforeid=None, beforetime=None):
        params = {'limit': str(limit)}
        if filters:
            for filter_item in filters:
                if filter_item not in happening_filters:
                    raise ValueError(f'No such filter "{filter_item}"')
            params['filter'] = '+'.join(filters)

        if nations and regions:
            raise ValueError('You cannot specify both nation and region views')
        if nations:
            nations = ','.join(map(normalize, nations))
            params['view'] = f'nation.{nations}'
        elif regions:
            regions = ','.join(map(normalize, regions))
            params['view'] = f'region.{regions}'

        if beforetime:
            params['beforetime'] = str(utc_seconds(beforetime))
        elif beforeid:
            params['beforeid'] = str(beforeid)

        @api_query('happenings', **params)
        async def result(_, root):
            return [process_happening(elem) for elem in root.find('HAPPENINGS')]
        return result(self)

    async def happenings(self, *, nations=None, regions=None, filters=None,
                         beforeid=None, beforetime=None):
        """Iterate through happenings from newest to oldest.

        Parameters
        ----------
        nations : iterable of str
            Nations happenings of which will be requested.  Cannot be
            specified at the same time with region.
        regions : iterable of str
            Regions happenings of which will be requested.  Cannot be
            specified at the same time with nation.
        filters : iterable of str
            Categories to request happenings by.  Available filters
            are: 'law', 'change', 'dispatch', 'rmb', 'embassy', 'eject',
            'admin', 'move', 'founding', 'cte', 'vote', 'resolution',
            'member', and 'endo'.
        beforeid : int
            Only request happenings before this id.
        beforetime : :class:`datetime.datetime`
            Only request happenings before this moment.
        """
        while True:
            happening_bunch = await self._get_happenings(
                nations=nations, regions=regions, filters=filters,
                beforeid=beforeid, beforetime=beforetime
            )
            for happening in happening_bunch:
                yield happening
            if len(happening_bunch) < 100:
                break
            beforeid = happening_bunch[-1].id

    async def new_happenings(self, poll_period=30, *, nations=None,
                             regions=None, filters=None):
        """New happenings as they arrive::

            async for happening in \\
                    world.new_happenings(region='the north pacific'):
                # Your processing code here
                print(happening.text)  # As an example

        Guarantees that:

        * Every happening is generated from the moment the generator
          is started;
        * No happening is generated more than once;
        * Happenings are generated in order from oldest to newest.

        Parameters
        ----------
        poll_period : int
            How long to wait between requesting the next bunch of
            happenings, in seconds.  Note that this should only be
            tweaked for latency reasons, as the function gives a
            guarantee that all happenings will be generated.  Also note
            that, regardless of the ``poll_period`` you set, all of the
            code in your loop body still has to execute (possibly
            several times) before a new bunch of happenings can be
            requested.  Consider wrapping your happening-processing code
            in a coroutine and launching it as a task from the loop body
            if you suspect this might be an issue.
        nations : iterable of str
            Nations happenings of which will be requested.  Cannot be
            specified at the same time with region.
        regions : iterable of str
            Regions happenings of which will be requested.  Cannot be
            specified at the same time with nation.
        filters : iterable of str
            Categories to request happenings by.  Available filters
            are: 'law', 'change', 'dispatch', 'rmb', 'embassy', 'eject',
            'admin', 'move', 'founding', 'cte', 'vote', 'resolution',
            'member', and 'endo'.

        Returns
        -------
        an asyncronous generator that yields :class:`UnrecognizedHappening` \
        or any of the classes that inherit from it
        """
        try:
            # We only need the happenings from this point forwards
            last_id = (await self._get_happenings(
                nations=nations, regions=regions, filters=filters,
                limit=1))[0].id
        except IndexError:
            # Happenings before this point have all been deleted
            last_id = 0

        while True:
            # Sleep before the loop body to avoid wasting the first request
            await sleep(poll_period)

            # I don't think there's a cleaner solution, sadly.
            happenings = []
            async for happening in self.happenings(
                    nations=nations, regions=regions, filters=filters):
                if happening.id <= last_id:
                    break
                happenings.append(happening)

            with suppress(IndexError):
                last_id = happenings[0].id

            for happening in reversed(happenings):
                yield happening
