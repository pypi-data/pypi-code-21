# TODO slots

import html
from contextlib import suppress
from enum import Flag, Enum, auto
from functools import reduce, total_ordering
from operator import or_

import aionationstates
from aionationstates.utils import timestamp, banner_url, unscramble_encoding
from aionationstates.ns_to_human import banner, census_info


__all__ = (
    'RateLimitError',
    'SessionConflictError',
    'AuthenticationError',
    'NotFound',
    'CensusScaleCurrent',
    'CensusScaleHistory',
    'CensusPoint',
    'Dispatch',
    'Poll',
    'PollOption',
    'Freedom',
    'FreedomScores',
    'Govt',
    'Sectors',
    'Issue',
    'IssueOption',
    'IssueResult',
    'CensusScaleChange',
    'Reclassifications',
    'Reclassification',
    'Embassies',
    'Officer',
    'Authority',
    'EmbassyPostingRights',
    'Post',
    'PostStatus',
    'Zombie',
)


class RateLimitError(Exception):
    pass


class SessionConflictError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class NotFound(Exception):
    pass



class CensusScaleCurrent:
    """World Census scale data about a nation.

    .. warning::

        With the exception of score, you must not expect the fields
        to update instantly.

        For the exact same reason of NationStates' excessive
        quirkiness, those fields may be missing (set to ``None``) on
        newly-founded nations (perhaps also in other cases, there is
        not a way to reliably test).  You will need to account for
        that in your code.

    Attributes
    ----------
    info : :class:`CensusInfo`
        Static information about the scale.
    score : float
        The absolute census score.  All the other scale values are
        calculated (by NationStates) from scale scores of multiple
        nations.  Should always be there.
    rank : int
        World rank by the scale.
    prank : float
        Percentage World rank by the scale.
    rrank : int
        Regional rank by the scale.
    prrank : float
        Percentage Regional rank by the scale.
    """

    def __init__(self, elem):
        self.info = census_info[int(elem.get('id'))]
        self.score = float(elem.find('SCORE').text)
        # For recently-founded nations (and maybe in other cases as well, who
        # knows) the ranks & percentages may not show up even if requested.
        self.rank = self.prank = self.rrank = self.prrank = None
        with suppress(AttributeError, TypeError):
            self.rank = int(elem.find('RANK').text)
        with suppress(AttributeError, TypeError):
            self.prank = float(elem.find('PRANK').text)
        with suppress(AttributeError, TypeError):
            self.rrank = int(elem.find('RRANK').text)
        with suppress(AttributeError, TypeError):
            self.prrank = float(elem.find('PRRANK').text)

    def __repr__(self):
        return f'<CensusScaleCurrent #{self.info.id} {self.info.title}>'


class CensusPoint:
    """What the scale score was on a particular date.

    Attributes
    ----------
    timestamp : naive UTC :class:`datetime.datetime`
        When the score was recorded.
    score : float
        What it was.
    """

    def __init__(self, elem):
        self.timestamp = timestamp(elem.find('TIMESTAMP').text)
        self.score = float(elem.find('SCORE').text)


class CensusScaleHistory:
    """Change of a World Census scale score of a nation through time.

    Attributes
    ----------
    info : :class:`ScaleInfo`
        Static information about the scale.
    history : list of :class:`CensusPoint`
        The data itself.
    """

    def __init__(self, elem):
        self.info = census_info[int(elem.get('id'))]
        self.history = [CensusPoint(sub_elem) for sub_elem in elem]

    def __repr__(self):
        return f'<CensusScaleHistory #{self.info.id} {self.info.title}>'



class Dispatch:
    """A dispatch.

    Attributes
    ----------
    id : int
        The dispatch id.
    title : str
        The dispatch title.
    author : :class:`Nation`
        Nation that posted the dispatch.
    category : str
        The dispatch category.
    subcategory : str
        The dispatch subcategory.
    views : int
        Number of times the dispatch got viewed.
    score : int
        Number of votes the dispatch received.
    created : naive UTC :class:`datetime.datetime`
        When the dispatch was created.
    edited : naive UTC :class:`datetime.datetime`
        When the dispatch last got edited.  Equal to ``created`` for
        dispatches that were never edited.
    text : str or None
        The dispatch text.  ``None`` if the dispatch came from anywhere
        other than the World dispatch shard.
    """

    def __init__(self, elem):
        self.id = int(elem.get('id'))
        self.title = unscramble_encoding(
            html.unescape(elem.find('TITLE').text))
        self.author = aionationstates.Nation(elem.find('AUTHOR').text)
        self.category = elem.find('CATEGORY').text
        self.subcategory = elem.find('SUBCATEGORY').text
        self.views = int(elem.find('VIEWS').text)
        self.score = int(elem.find('SCORE').text)

        created = int(elem.find('CREATED').text)
        # Otherwise it's 0 for dispatches that were never edited
        edited = int(elem.find('EDITED').text) or created
        self.created = timestamp(created)
        self.edited = timestamp(edited)

        self.text = None
        with suppress(AttributeError):
            self.text = unscramble_encoding(
                html.unescape(elem.find('TEXT').text))

    def full(self):
        """Request the full dispatch (with text).

        Returns
        -------
        an :class:`ApiQuery` of :class:`Dispatch`
        """
        return aionationstates.world.dispatch(self.id)

    def __repr__(self):
        return f'<Dispatch id={self.id}>'


class PollOption:
    """An option in a poll.

    Attributes
    ----------
    text : str
        Text of the option.
    voters : list of :class:`Nation`
        Nations that picked this option.
    """

    def __init__(self, elem):
        self.text = html.unescape(elem.findtext('OPTIONTEXT'))
        voters = elem.find('VOTERS').text
        self.voters = voters.split(':') if voters else []


class Poll:
    """A regional poll.

    Attributes
    ----------
    id : int
        The poll id.
    title : str
        The poll title.
    text : str
        The poll text.
    region : :class:`Region`
        Region the poll was posted in.
    author : :class:`Nation`
        Nation that posted the poll.
    options : list of :class:`PollOption`
        The poll options.
    """

    def __init__(self, elem):
        self.id = int(elem.get('id'))
        self.title = html.unescape(elem.findtext('TITLE'))
        try:
            self.text = html.unescape(elem.findtext('TEXT'))
        except AttributeError:
            self.text = None
        self.region = aionationstates.Region(elem.find('REGION').text)
        self.author = aionationstates.Nation(elem.find('AUTHOR').text)
        self.start = timestamp(elem.find('START').text)
        self.stop = timestamp(elem.find('STOP').text)
        self.options = [PollOption(option_elem)
                        for option_elem in elem.find('OPTIONS')]

    def __repr__(self):
        return f'<Poll id={self.id}>'



class Freedom:
    """Nation's `Freedoms`: three basic indicators of the nation's
    Civil Rights, Economy, and Political Freedom, as expressive
    adjectives.

    Attributes
    ----------
    civilrights : str
        Nation's Civil Rights.
    economy : str
        Nation's Economic Prosperity.
    politicalfreedom : str
        Nation's Political Freedom.
    """

    def __init__(self, elem):
        self.civilrights = elem.find('CIVILRIGHTS').text
        self.economy = elem.find('ECONOMY').text
        self.politicalfreedom = elem.find('POLITICALFREEDOM').text


class FreedomScores:
    """Nation's `Freedoms`: three basic indicators of the nation's
    Civil Rights, Economy, and Political Freedom, as percentages.

    Attributes
    ----------
    civilrights : str
        Nation's Civil Rights.
    economy : str
        Nation's Economic Prosperity.
    politicalfreedom : str
        Nation's Political Freedom.
    """

    def __init__(self, elem):
        self.civilrights = int(elem.find('CIVILRIGHTS').text)
        self.economy = int(elem.find('ECONOMY').text)
        self.politicalfreedom = int(elem.find('POLITICALFREEDOM').text)


class Govt:
    """Nation's government expenditure, as percentages.

    Attributes
    ----------
    administration : float
        The percentage of nation's budget spent on Administration.
    defence : float
        The percentage of nation's budget spent on Defence.
    education : float
        The percentage of nation's budget spent on Public Education.
    environment : float
        The percentage of nation's budget spent on Enviromental Protection.
    healthcare : float
        The percentage of nation's budget spent on Public Healthcare.
    commerce : float
        The percentage of nation's budget spent on Industry.
    internationalaid : float
        The percentage of nation's budget spent on International Aid.
    lawandorder : float
        The percentage of nation's budget spent on Law & Order.
    publictransport : float
        The percentage of nation's budget spent on Public Transportation.
    socialequality : float
        The percentage of nation's budget spent on Social Policy.
    spirituality : float
        The percentage of nation's budget spent on Spirituality.
    welfare : float
        The percentage of nation's budget spent on Welfare.
    """

    def __init__(self, elem):
        self.administration = float(elem.find('ADMINISTRATION').text)
        self.defence = float(elem.find('DEFENCE').text)
        self.education = float(elem.find('EDUCATION').text)
        self.environment = float(elem.find('ENVIRONMENT').text)
        self.healthcare = float(elem.find('HEALTHCARE').text)
        self.commerce = float(elem.find('COMMERCE').text)
        self.internationalaid = float(elem.find('INTERNATIONALAID').text)
        self.lawandorder = float(elem.find('LAWANDORDER').text)
        self.publictransport = float(elem.find('PUBLICTRANSPORT').text)
        self.socialequality = float(elem.find('SOCIALEQUALITY').text)
        self.spirituality = float(elem.find('SPIRITUALITY').text)
        self.welfare = float(elem.find('WELFARE').text)


class Sectors:
    """Components of a nation's economy.

    Attributes
    ----------
    blackmarket : float
        Part of the economy taken up by Black Market.
    government : float
        Part of the economy taken up by Government.
    industry : float
        Part of the economy taken up by Private Industry.
    public : float
        Part of the economy taken up by State-Owned Industry.
    """

    def __init__(self, elem):
        self.blackmarket = float(elem.find('BLACKMARKET').text)
        self.government = float(elem.find('GOVERNMENT').text)
        self.industry = float(elem.find('INDUSTRY').text)
        self.public = float(elem.find('PUBLIC').text)



class Reclassification:
    """Change in a `Freedom` classification or the WA Category.

    Attributes
    ----------
    before : str
        The old category or `Freedom` adjective.
    after : str
        The new category or `Freedom` adjective.
    """

    def __init__(self, elem):
        self.before = elem.find('FROM').text
        self.after = elem.find('TO').text


class Reclassifications:
    """Reclassifications of the nation's `Freedoms` and WA Category.
    For convenience, this is falsey when no reclassifications occured.

    Attributes
    ----------
    civilrights : :class:`Reclassification` or None
        Reclassification of nation's Civil Rights.
    economy : :class:`Reclassification` or None
        Reclassification of nation's Economy.
    politicalfreedom : :class:`Reclassification` or None
        Reclassification of nation's Political Freedom.
    govt : :class:`Reclassification` or None
        Change of nation's World Assembly Category.
    """

    def __init__(self, elem):
        self.civilrights = self.economy = \
            self.politicalfreedom = self.govt = None
        if elem is None:
            return
        attr_names = {
            '0': 'civilrights',
            '1': 'economy',
            '2': 'politicalfreedom',
            'govt': 'govt'
        }
        for sub_elem in elem:
            setattr(
                self, attr_names[sub_elem.get('type')],
                Reclassification(sub_elem)
            )

    def __bool__(self):
        return (self.civilrights or self.economy
                or self.politicalfreedom or self.govt)


class CensusScaleChange:
    """Change in one of the World Census scales of a nation

    Attributes
    ---------
    info : :class:`CensusInfo`
        Static information about the scale.
    score : float
        The scale score, after the change.
    change : float
        Change of the score.
    pchange : float
        The semi-user-friendly percentage change NationStates shows by default.
    """

    def __init__(self, elem):
        self.info = census_info[int(elem.get('id'))]
        self.score = float(elem.find('SCORE').text)
        self.change = float(elem.find('CHANGE').text)
        self.pchange = float(elem.find('PCHANGE').text)


class IssueResult:
    """Result of an issue.

    Attributes
    ----------
    happening : str
        The issue effect line.  Not a sentence, mind you -- it's
        uncapitalized and does not end with a period.  ``None`` if the
        issue was dismissed.
    census : list of :class:`CensusScaleChange`
        Changes in census scores of the nation.
    banners : list of :class:`Banner`
        The banners unlocked by answering the issue.
    reclassifications : :class:`Reclassifications`
        WA Category and Freedoms reclassifications.
    headlines : list of str
        Newspaper headlines.  NationStates returns this field with
        unexpanded macros.  I did my best to try and expand them all
        client-side, however there does not exist a document in which
        they are formally defined (that is sort of a pattern throughout
        NationStates, maybe you've noticed), so I can only do so much.
        Please report any unexpanded macros you encounter as bugs.
    """

    def __init__(self, elem):
        with suppress(AttributeError):
            error = elem.find('ERROR').text
            if error == 'Invalid choice.':
                raise ValueError('invalid option')
            elif error == 'Issue already processed!':
                # I know it may not be obvious, but that's exactly
                # what NS is trying to say here.
                raise ValueError('invalid issue')
        assert elem.find('OK').text == '1'  # honestly no idea

        self.happening = elem.findtext('DESC')  # TODO rename
        self.census = [
            CensusScaleChange(sub_elem) for sub_elem
            in elem.find('RANKINGS') or ()
        ]
        self.banners = [
            banner(sub_elem.text) for sub_elem
            in elem.find('UNLOCKS') or ()
        ]
        self.reclassifications = Reclassifications(
            elem.find('RECLASSIFICATIONS'))
        self.headlines = [
            sub_elem.text for sub_elem
            in elem.find('HEADLINES') or ()
        ]



class IssueOption:
    """An option of an issue.

    Attributes
    ----------
    text : str
        The option text. May contain HTML elements and character references.
    """

    def __init__(self, elem, issue):
        self._issue = issue
        self._id = int(elem.get('id'))
        self.text = unscramble_encoding(elem.text)

    def accept(self):
        """Accept the option.

        Returns
        -------
        an :class:`ApiQuery` of :class:`IssueResult`
        """
        return self._issue._nation._accept_issue(self._issue.id, self._id)

    # TODO repr


class Issue:
    """An issue.

    Attributes
    ----------
    id : str
        The issue id.
    title : str
        The issue title.  May contain HTML elements and character references.
    text : str
        The issue text.  May contain HTML elements and character references.
    author : str
        Author of the issue, usually a nation.
    editor : str
        Editor of the issue, usually a nation.
    options : list of :class:`IssueOption`
        Issue options.
    banners : str
        URLs of issue banners.
    """

    def __init__(self, elem, nation):
        self._nation = nation
        self.id = int(elem.get('id'))
        self.title = elem.find('TITLE').text
        self.text = unscramble_encoding(elem.find('TEXT').text)
        self.author = elem.findtext('AUTHOR')
        self.editor = elem.findtext('EDITOR')
        self.options = [
            IssueOption(sub_elem, self)
            for sub_elem in elem.findall('OPTION')
        ]
        def issue_banners(elem):
            for x in range(1, 10):  # Should be more than enough.
                try:
                    yield banner_url(elem.find(f'PIC{x}').text)
                except AttributeError:
                    break
        self.banners = list(issue_banners(elem))

    def dismiss(self):
        """Dismiss the issue."""
        return self._nation._accept_issue(self.id, -1)

    # TODO repr



class Embassies:
    """Embassies of a region.

    Attributes
    ----------
    active : list of :class:`Region`
        Normal, alive embassies.
    closing : list of :class:`Region`
        Embassies the demolition of which has been initiated, but did
        not yet finish.
    pending : list of :class:`Region`
        Embassies the creation of which has been initiated, but did not
        yet finish.
    invited : list of :class:`Region`
        Embassy invitations that have not yet been processed.
    rejected : list of :class:`Region`
        Embassy invitations that have been denied.
    """

    def __init__(self, elem):
        # I know I'm iterating through them five times; I don't care.
        self.active = [aionationstates.Region(sub_elem.text)
                       for sub_elem in elem
                       if sub_elem.get('type') is None]
        self.closing = [aionationstates.Region(sub_elem.text)
                        for sub_elem in elem
                        if sub_elem.get('type') == 'closing']
        self.pending = [aionationstates.Region(sub_elem.text)
                        for sub_elem in elem
                        if sub_elem.get('type') == 'pending']
        self.invited = [aionationstates.Region(sub_elem.text)
                        for sub_elem in elem
                        if sub_elem.get('type') == 'invited']
        self.rejected = [aionationstates.Region(sub_elem.text)
                         for sub_elem in elem
                         if sub_elem.get('type') == 'rejected']



class Authority(Flag):
    """Authority of a Regional Officer, Delegate, or Founder."""
    EXECUTIVE      = X = auto()
    WORLD_ASSEMBLY = W = auto()
    APPEARANCE     = A = auto()
    BORDER_CONTROL = B = auto()
    COMMUNICATIONS = C = auto()
    EMBASSIES      = E = auto()
    POLLS          = P = auto()

    @classmethod
    def _from_ns(cls, string):
        """This is the only sane way I could find to make Flag enums
        work with individual characters as flags.
        """
        return reduce(or_, (cls[char] for char in string))

    def __repr__(self):
        return f'<OfficerAuthority.{self.name}>'


class Officer:
    """A Regional Officer.

    Attributes
    ----------
    nation : :class:`Nation`
        Officer's nation.
    office : str
        The (user-specified) office held by the officer.
    authority : :class:`OfficerAuthority`
        Officer's authority.
    appointed_at : naive UTC :class:`datetime.datetime`
        When the officer got appointed.
    appointed_by : :class:`Nation`
        The nation that appointed the officer.
    """

    def __init__(self, elem):
        self.nation = aionationstates.Nation(elem.find('NATION').text)
        self.office = elem.findtext('OFFICE')
        self.authority = Authority._from_ns(elem.find('AUTHORITY').text)
        self.appointed_at = timestamp(elem.find('TIME').text)
        self.appointed_by = aionationstates.Nation(elem.find('BY').text)



@total_ordering
class EmbassyPostingRights(Enum):
    """Who out of embassy regions' residents can post on the Regional
    Message Board.
    """
    NOBODY = 1
    DELEGATES_AND_FOUNDERS = 2
    COMMUNICATIONS_OFFICERS = 3
    OFFICERS = 4
    EVERYBODY = 5

    @classmethod
    def _from_ns(cls, string):
        values = {
            '0': 1,  # The reason I have to do all this nonsense.
            'con': 2,
            'com': 3,
            'off': 4,
            'all': 5,
        }
        return cls(values[string])

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class PostStatus(Enum):
    """Status of a post on a Regional Message Board.

    Attributes:
        NORMAL: A regular post.
        SUPPRESSED: The post got suppressed by a regional official.
        DELETED: The post got deleted by its author.
        MODERATED: The post got suppressed by a game moderator.
    """
    NORMAL = 0
    SUPPRESSED = 1
    DELETED = 2
    MODERATED = 9

    @property
    def viewable(self) -> bool:
        """Whether the post content can still be accessed.  Shortcut
        for ``PostStatus.NORMAL or PostStatus.SUPPRESSED``.
        """
        return self.value in (0, 1)


class Post:
    """A post on a Regional Message Board.

    Attributes
    ----------
    id : int
        The unique id of the post.
    timestamp : naive UTC :class:`datetime.datetime`
        When the post was put up.
    author : :class:`Nation`
        The author nation.
    status : :class:`PostStatus`
        Status of the post.
    text : str
        The post text.
    likers : list of :class:`Nation`
        Nations that liked the post.
    suppressor : :class:`Nation` of None
        Nation that suppressed the post.  ``None`` if the post has not
        been suppressed or has been suppressed by moderators.
    """

    def __init__(self, elem):
        self.id = int(elem.get('id'))
        self.timestamp = timestamp(elem.find('TIMESTAMP').text)
        self.author = aionationstates.Nation(elem.find('NATION').text)
        self.status = PostStatus(int(elem.find('STATUS').text))
        self.text = elem.find('MESSAGE').text  # TODO unescape?

        likers_elem = elem.find('LIKERS')
        self.likers = likers_elem.text.split(':') if likers_elem else []

        suppressor_str = elem.findtext('SUPPRESSOR')
        if suppressor_str in ('!mod', None):
            self.suppressor = None
        else:
            self.suppressor = aionationstates.Nation()

    # TODO repr



class Zombie:
    """The situation in a nation/region during the annual Z-Day event.

    Attributes
    ----------
    survivors : int
        The number of citizens surviving, in millions.
    zombies : int
        The number of undead citizens, in millions.
    dead : int
        The number of dead citizens, in millions.
    action : str or None
        The nation's strategy for dealing with the disaster.  Either
        "research", "exterminate", or "export".  ``None`` if the
        instance represents regional situation.
    """

    def __init__(self, elem):
        self.survivors = int(elem.find('SURVIVORS').text)
        self.zombies = int(elem.find('ZOMBIES').text)
        self.dead = int(elem.find('DEAD').text)
        self.action = elem.findtext('ZACTION')


# TODO gavote, scvote
