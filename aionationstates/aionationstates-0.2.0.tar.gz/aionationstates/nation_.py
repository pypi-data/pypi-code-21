import re
import html

from aionationstates.utils import normalize, timestamp, unscramble_encoding
from aionationstates.types import (
    Freedom, FreedomScores, Govt, Sectors, Dispatch)
from aionationstates.session import Session, api_query
from aionationstates.shards import NationRegion
from aionationstates.ns_to_human import banner
import aionationstates


class Nation(NationRegion, Session):
    """A class to interact with the NationStates Nation public API.

    Shards absent (incomplete):

    * **lastactivity** - There is no timestamp version, and the value
      is kind of useless anyways.
    * **govtpriority** - Use the govt shard.
    * **factbooks**, **dispatches**, **factbooklist** - Use the
      dispatchlist shard.
    * **income**, **poorest**, **richest** - Use census scales 72, 73,
      and 74 respectively.  The gdp shard has been kept, as it appears
      to be slightly different from scale 76.

    Attributes
    ----------
    id : str
        The defining characteristic of a nation, its normalized name.
        No two nations share the same id, and no one id is shared by
        multiple nations.
    """

    def __init__(self, name: str):
        self.id = normalize(name)

    def _call_api(self, params, **kwargs):
        params['nation'] = self.id
        return super()._call_api(params, **kwargs)


    @property
    def url(self):
        """str: URL of the nation."""
        return f'https://www.nationstates.net/nation={self.id}'

    @api_query('name')
    async def name(self, root):
        """Name of the nation, for example 'Testlandia'.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('NAME').text

    @api_query('type')
    async def type(self, root):
        """Type of the nation, for example 'Hive Mind'.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('TYPE').text

    @api_query('fullname')
    async def fullname(self, root):
        """Full name of the nation, for example 'The Hive Mind of
        Testlandia'.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('FULLNAME').text

    @api_query('motto')
    async def motto(self, root):
        """Motto of the nation.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return unscramble_encoding(html.unescape(root.find('MOTTO').text))

    @api_query('category')
    async def category(self, root):
        """Nation's World Assembly Category.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('CATEGORY').text

    @api_query('region')
    async def region(self, root):
        """Region in which the nation resides.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Region`
        """
        return aionationstates.Region(root.find('REGION').text)

    @api_query('animal')
    async def animal(self, root):
        """Nation's national animal.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('ANIMAL').text

    @api_query('currency')
    async def currency(self, root):
        """Nation's national currency.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('CURRENCY').text

    @api_query('demonym')
    async def demonym(self, root):
        """Nation's demonym, as an adjective.

        Example: Testlandish, as in 'I'm proud to be Testlandish.'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('DEMONYM').text

    @api_query('demonym2')
    async def demonym2(self, root):
        """Nation's demonym, as a noun.

        Example: Testlandian, as in 'I'm a proud Testlandian.'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('DEMONYM2').text

    @api_query('demonym2plural')
    async def demonym2plural(self, root):
        """Plural of the nation's noun demonym.

        Example: Testlandians, as in 'Here come the Testlandians!'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('DEMONYM2PLURAL').text

    @api_query('flag')
    async def flag(self, root):
        """URL of the nation's flag.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('FLAG').text

    @api_query('majorindustry')
    async def majorindustry(self, root):
        """The industry prioritized by the nation.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('MAJORINDUSTRY').text

    @api_query('influence')
    async def influence(self, root):
        """An adjective describing nation's regional influence.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('INFLUENCE').text

    @api_query('leader')
    async def leader(self, root):
        """Nation's leader.  Either set by the user or the default
        'Leader'.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('LEADER').text

    @api_query('capital')
    async def capital(self, root):
        """Nation's capital. Either set by the user or the default
        '`name` City.'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('CAPITAL').text

    @api_query('religion')
    async def religion(self, root):
        """Nation's main religion.  Either set by the user or the
        default 'a major religion.'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('RELIGION').text

    @api_query('admirable')
    async def admirable(self, root):
        """One of the nation's qualities, at random.

        Example: 'environmentally stunning'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('ADMIRABLE').text

    @api_query('animaltrait')
    async def animaltrait(self, root):
        """Short characteristic of the nation's national animal.

        Example: 'frolics freely in the nation's sparkling oceans'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('ANIMALTRAIT').text

    @api_query('crime')
    async def crime(self, root):
        """A sentence describing the nation's crime levels.

        Example: 'Crime is totally unknown, thanks to a very
        well-funded police force and progressive social policies in
        education and welfare.'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('CRIME').text

    @api_query('govtdesc')
    async def govtdesc(self, root):
        """A couple of sentences describing the nation's government.

        Example: 'It is difficult to tell where the omnipresent
        government stops and the rest of society begins, but it
        juggles the competing demands of Defense, Environment, and
        Healthcare. It meets to discuss matters of state in the
        capital city of Test City.'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('GOVTDESC').text

    @api_query('industrydesc')
    async def industrydesc(self, root):
        """A couple of sentences describing the nation's economy,
        industry, and average income.

        Example: 'The strong Testlandish economy, worth a remarkable
        2,212 trillion denarii a year, is driven almost entirely by
        government activity. The industrial sector, which is extremely
        specialized, is mostly made up of the Arms Manufacturing
        industry, with major contributions from Book Publishing.
        Average income is 73,510 denarii, with the richest citizens
        earning 6.0 times as much as the poorest.'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('INDUSTRYDESC').text

    @api_query('notable')
    async def notable(self, root):
        """A few of nation's peculiarities, at random.

        Example: 'museums and concert halls, multi-spousal wedding
        ceremonies, and devotion to social welfare'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('NOTABLE').text

    @api_query('sensibilities')
    async def sensibilities(self, root):
        """A couple of adjectives describing the nation's citizens.

        Example: 'compassionate, devout'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('SENSIBILITIES').text


    @api_query('population')
    async def population(self, root):
        """Nation's population, in millions.

        Returns
        -------
        an :class:`ApiQuery` of int
        """
        return int(root.find('POPULATION').text)

    @api_query('gdp')
    async def gdp(self, root):
        """Nation's gross domestic product.

        Returns
        -------
        an :class:`ApiQuery` of int
        """
        return int(root.find('GDP').text)

    @api_query('foundedtime')
    async def founded(self, root):
        """When the nation was founded.

        ``1970-01-01 00:00`` for nations founded in Antiquity.

        Returns
        -------
        an :class:`ApiQuery` of a naive UTC :class:`datetime.datetime`
        """
        return timestamp(root.find('FOUNDEDTIME').text)

    @api_query('firstlogin')
    async def firstlogin(self, root):
        """When the nation was first logged into.

        ``1970-01-01 00:00`` for nations first logged into during
        Antiquity.

        Returns
        -------
        an :class:`ApiQuery` of a naive UTC :class:`datetime.datetime`
        """
        return timestamp(root.find('FIRSTLOGIN').text)

    @api_query('lastlogin')
    async def lastlogin(self, root):
        """When the nation was last logged into.

        Returns
        -------
        an :class:`ApiQuery` of a naive UTC :class:`datetime.datetime`
        """
        return timestamp(root.find('LASTLOGIN').text)

    @api_query('wa')
    async def wa(self, root):
        """Whether the nation is a member of the World Assembly or not.

        Returns
        -------
        an :class:`ApiQuery` of bool
        """
        return root.find('UNSTATUS').text == 'WA Member'

    @api_query('freedom')
    async def freedom(self, root):
        """Nation's `Freedoms`: three basic indicators of the nation's
        Civil Rights, Economy, and Political Freedom, as expressive
        adjectives.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Freedom`
        """
        return Freedom(root.find('FREEDOM'))

    @api_query('freedomscores')
    async def freedomscores(self, root):
        """Nation's `Freedoms`: three basic indicators of the nation's
        Civil Rights, Economy, and Political Freedom, as percentages.

        Returns
        -------
        an :class:`ApiQuery` of :class:`FreedomScores`
        """
        return FreedomScores(root.find('FREEDOMSCORES'))

    @api_query('govt')
    async def govt(self, root):
        """Nation's government expenditure, as percentages.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Govt`
        """
        return Govt(root.find('GOVT'))

    @api_query('deaths')
    async def deaths(self, root):
        """Causes of death in the nation, as percentages.

        Returns
        -------
        an :class:`ApiQuery` of dict with keys of str and values of float
        """
        return {
            elem.get('type'): float(elem.text)
            for elem in root.find('DEATHS')
        }

    @api_query('endorsements')
    async def endorsements(self, root):
        """Endorsements the nation has received.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Nation`
        """
        text = root.find('ENDORSEMENTS').text
        return [Nation(name) for name in text.split(',')] if text else []

    @api_query('legislation')
    async def legislation(self, root):
        """Effects of the most recently passed legislation.

        May contain HTML elements and character references.

        Returns
        -------
        an :class:`ApiQuery` of a list of str
        """
        return [elem.text for elem in root.find('LEGISLATION')]

    @api_query('sectors')
    async def sectors(self, root):
        """Components of the nation's economy, as percentages.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Sectors`
        """
        return Sectors(root.find('SECTORS'))

    @api_query('dispatchlist')
    async def dispatchlist(self, root):
        """Nation's published dispatches.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Dispatch`
        """
        return [
            Dispatch(elem)
            for elem in root.find('DISPATCHLIST')
        ]

    def verify(self, checksum, *, token=None):
        """Interface to the `NationStates Verification API
        <https://www.nationstates.net/pages/api.html#verification>`_.

        Parameters
        ----------
        checksum : str
            The user-supplied verification code.  Expires if the nation
            logs out, if it performs a significant in-game action such
            as moving regions or endorsing another nation, and after it
            is successfully verified.
        token : str
            A token specific to your service and the nation being verified.
        """
        params = {'a': 'verify', 'checksum': checksum}
        if token:
            params['token'] = token
        # Needed so that we get output in xml, as opposed to
        # plain text. It doesn't actually matter what the
        # q param is, it's just important that it's not empty.
        @api_query('i_need_the_output_in_xml', **params)
        async def result(self, root):
            return bool(int(root.find('VERIFY').text))
        return result(self)

    def verification_url(self, *, token=None):
        """URL the user needs to follow in order to get the
        verification code for the nation.

        Parameters
        ----------
        token : str
            A token specific to your service and the nation being verified.
        """
        if token:
            return ('https://www.nationstates.net/'
                    f'page=verify_login?token={token}')
        return f'https://www.nationstates.net/page=verify_login'

    @api_query('banners')
    async def banners(self, root):
        """Nation's visible banners.  If the user has set a primary
        banner, it will be the first element in the list.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Banner`
        """
        expand_macros = self._get_macros_expander()
        return [
            await banner(elem.text)._expand_macros(expand_macros)
            for elem in root.find('BANNERS')
        ]

    def _get_macros_expander(self):
        # The only macros present in the banner names are name,
        # demonym, and faith.  If the NS admins ever choose to answer
        # my request and fix the unexpanded macros in issue effect
        # headlines, the rest should be removed as unnecessary.
        query = (
            self.demonym() + self.demonym2() + self.demonym2plural()
            + self.name() + self.religion() + self.animal() + self.capital()
            + self.leader() + self.currency()
        )
        query_result = None

        async def expand_macros(line):
            nonlocal query_result
            if '@@' in line:
                if query_result is None:
                    # Only request macros data if we need it
                    query_result = await query
                return (
                    line
                    .replace('@@DEMONYM@@', query_result[0])
                    .replace('@@DEMONYM2@@', query_result[1])
                    # Not documented, or even mentioned anywhere.
                    # Discovered through experimentation.  No idea if
                    # that's a pattern or not.
                    # More experimentation will tell, I guess?
                    .replace('@@PL(DEMONYM2)@@', query_result[2])
                    # I feel filthy just looking at this.  Surely, NS
                    # wouldn't put bits of Perl code to be executed
                    # into macros?  Surely, their implementation can't
                    # be that bad?
                    # Yeah right.  Ha ha.  Ha.
                    .replace('@@uc($nation->query("name"))@@',
                             query_result[3].upper())
                    # I wasn't that nihilistic before starting to write
                    # this library, was I?
                    .replace('@@NAME@@', query_result[3])
                    .replace('@@FAITH@@', query_result[4])
                    .replace('@@ANIMAL@@', query_result[5])
                    # Am I surprised that even in their code they have
                    # two ways to query data, used interchangeably?
                    # At this point, not really, no.
                    .replace('@@$nation->query_capital()@@', query_result[6])
                    # I just hope there aren't enough headlines with
                    # macros to force me into using regex.
                    .replace('@@LEADER@@', query_result[7])
                    .replace('@@CURRENCY@@', query_result[8])
                )
            return line

        return expand_macros

    async def description(self):
        """Nation's full description, as seen on its in-game page.

        Returns
        -------
        an awaitable of str
        """
        resp = await self._call_web(f'nation={self.id}')
        return html.unescape(
            re.search(
                '<div class="nationsummary">(.+?)<p class="nationranktext">',
                resp.text,
                flags=re.DOTALL
            )
            .group(1)
            .replace('\n', '')
            .replace('</p>', '')
            .replace('<p>', '\n\n')
            .strip()
        )
