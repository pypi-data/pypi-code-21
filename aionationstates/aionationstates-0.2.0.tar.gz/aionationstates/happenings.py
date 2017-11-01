"""Digest all NationStates happenings, extracting their type and useful data.

A great undertaking to be sure.
"""

import re
import html
from contextlib import suppress

from aionationstates.utils import timestamp, unscramble_encoding
import aionationstates



class UnrecognizedHappening:
    """A happening that wasn't recognized by the system.

    Most likely cause of this is the futility of this measly effort
    against the inescapable and ever-growing chaos of our Universe.

    Not necessarily an error in the parsing system, rather an indicator
    of its incompleteness.

    Note that all the other classes in the `happenings` module inherit
    from this import class, so all the attributes listed below are
    present on them as well.

    Attributes:
        id: The happening id.  `None` if the happening is from a national or
            regional archive.
        timestamp: Time of the happening.
        text: The happening text.
    """

    def __init__(self, text, params):
        self.id, self.timestamp = params
        self.text = text

    def __repr__(self):
        return f'<Happening #{self.id}>'



class Move(UnrecognizedHappening):
    """A nation moving regions.

    Attributes
    ----------
    nation : :class:`Nation`
    region_from : :class:`Region`
    region_to : :class:`Region`
    """

    def __init__(self, text, params):
        match = re.match(
            r'@@(.+?)@@ relocated from %%(.+?)%% to %%(.+?)%%', text)
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        self.region_from = aionationstates.Region(match.group(2))
        self.region_to = aionationstates.Region(match.group(3))
        super().__init__(text, params)


class Founding(UnrecognizedHappening):
    """A nation being founded.

    Attributes
    ----------
    nation : :class:`Nation`
    region : :class:`Region`
        The feeder region nation spawned in.
    """

    def __init__(self, text, params):
        match = re.match('@@(.+?)@@ was founded in %%(.+?)%%', text)
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        self.region = aionationstates.Region(match.group(2))
        super().__init__(text, params)


class CTE(UnrecognizedHappening):
    """A nation ceasing to exist.

    Attributes
    ----------
    nation : :class:`Nation`
    region : :class:`Region`
        Region the nation CTEd in.
    """

    def __init__(self, text, params):
        match = re.match('@@(.+?)@@ ceased to exist in %%(.+?)%%', text)
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        self.region = aionationstates.Region(match.group(2))
        super().__init__(text, params)


class Legislation(UnrecognizedHappening):
    """A nation answering an issue.

    Attributes
    ----------
    nation : :class:`Nation`
    effect_line : str
        May contain HTML elements and character references.
    """

    def __init__(self, text, params):
        match = re.match(
            r'Following new legislation in @@(.+?)@@, (.+)\.', text)
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        self.effect_line = match.group(2)
        super().__init__(text, params)


class FlagChange(UnrecognizedHappening):
    """A nation altering its flag.

    Attributes
    ----------
    nation : :class:`Nation`
    """

    def __init__(self, text, params):
        match = re.match('@@(.+?)@@ altered its national flag', text)
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        super().__init__(text, params)


class SettingsChange(UnrecognizedHappening):
    """A nation modifying its customizeable fields.

    Attributes
    ----------
    nation : :class:`Nation`
    changes : dict with keys and values of str
        A mapping of field names (such as "currency", "motto", etc.) to
        their new values.
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ changed its national', text)
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        self.changes = {}
        super().__init__(text, params)
        # If you harbor any sort of motivation to refactor this, feel free.
        index = text.index('@@ changed its national') + 23
        text = 'its' + text[index:]

        for substr in text.replace('" and', '",').split(','):
            # none of the fields are supposed to contain quotes
            match = re.search('its (.+?) to "(.+?)"', substr)
            value = unscramble_encoding(html.unescape(match.group(2)))
            self.changes[match.group(1)] = value



class DispatchPublication(UnrecognizedHappening):
    """A dispatch being published.

    In case you're wondering, deleting a dispatch doesn't produce a happening.

    Attributes
    ----------
    nation : :class:`Nation`
    dispatch_id : int
    title : str
    category : str
    subcategory : str
    """

    def __init__(self, text, params):
        match = re.match(
            r'@@(.+?)@@ published "<a href="page=dispatch/id=(.+?)">(.+?)</a>" \((.+?): (.+?)\).',
            text
        )
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        self.dispatch_id = int(match.group(2))
        self.title = unscramble_encoding(html.unescape(match.group(3)))
        self.category = match.group(4)
        self.subcategory = match.group(5)
        super().__init__(text, params)

    def dispatch(self):
        """Request the full dispatch.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Dispatch`
            Full dispatch (with text).
        """
        return aionationstates.world.dispatch(self.dispatch_id)



class WorldAssemblyApplication(UnrecognizedHappening):
    """A nation applying to join the World Assembly.

    Attributes
    ----------
    nation : :class:`Nation`
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ applied to join the World Assembly.',
            text
        )
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        super().__init__(text, params)


class WorldAssemblyAdmission(UnrecognizedHappening):
    """A nation being admitted to the World Assembly.

    Attributes
    ----------
    nation : :class:`Nation`
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ was admitted to the World Assembly.',
            text
        )
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        super().__init__(text, params)


class WorldAssemblyResignation(UnrecognizedHappening):
    """A nation resigning from World Assembly.

    Attributes
    ----------
    nation : :class:`Nation`
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ resigned from the World Assembly.',
            text
        )
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        super().__init__(text, params)


class DelegateChange(UnrecognizedHappening):
    """A region changing World Assembly Delegates.

    Note that NationStates spreads this out to three distinct happenings:
        - delegates changing;
        - a nation taking the free delegate position; and
        - a delegate being removed, leaving the position empty.

    As I believe this to be superfluous, this class represents all three.
    In case either the old of new delegate is missing, the corresponding
    attribute will ne `None`.

    Attributes
    ----------
    new_delegate : :class:`Nation`
    old_delegate : :class:`Nation`
    region : :class:`Region`
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ seized the position of %%(.+?)%% WA Delegate from @@(.+?)@@.',
            text
        )
        if match:
            self.new_delegate = aionationstates.Nation(match.group(1))
            self.region = aionationstates.Region(match.group(2))
            self.old_delegate = aionationstates.Nation(match.group(3))
            return
        super().__init__(text, params)
        match = re.match(
            '@@(.+?)@@ became WA Delegate of %%(.+?)%%.',
            text
        )
        if match:
            self.new_delegate = aionationstates.Nation(match.group(1))
            self.region = aionationstates.Region(match.group(2))
            self.old_delegate = None
            return

        match = re.match(
            '@@(.+?)@@ lost WA Delegate status in %%(.+?)%%.',
            text
        )
        if match:
            self.old_delegate = aionationstates.Nation(match.group(1))
            self.region = aionationstates.Region(match.group(2))
            self.new_delegate = None
            return

        raise ValueError



class CategoryChange(UnrecognizedHappening):
    """A nation being reclassified to a different WA Category.

    Attributes
    ----------
    nation : :class:`Nation`
    catogory_before : str
    category_after : str
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ was reclassified from "(.+?)" to "(.+?)".',
            text
        )
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        self.category_before = match.group(2)
        self.category_after = match.group(3)
        super().__init__(text, params)


class BannerCreation(UnrecognizedHappening):
    """A nation creating a custom banner.

    Attributes
    ----------
    nation : :class:`Nation`
    """

    def __init__(self, text, params):
        match = re.match('@@(.+?)@@ created a custom banner.', text)
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        super().__init__(text, params)


class EmbassyConstructionRequest(UnrecognizedHappening):
    """A nation proposing construction of embassies between two regions.

    Attributes
    ----------
    nation : :class:`Nation`
        Nation performing the action.
    regions : tuple of two :class:`Region` objects
        Regions involved in the embassy request.  The order is not
        guaranteed, as it mimics the one from the happening, but the
        first one appears to be one the request was sent from.
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ proposed constructing embassies between %%(.+?)%% and %%(.+?)%%.',
            text
        )
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        self.regions = (
            aionationstates.Region(match.group(2)),
            aionationstates.Region(match.group(3))
        )
        super().__init__(text, params)


class EmbassyConstructionConfirmation(UnrecognizedHappening):
    """A nation accepting a request to construct embassies between two regions.

    Attributes
    ----------
    nation : :class:`Nation`
        Nation performing the action.
    regions : tuple of two :class:`Region` objects
        Regions involved in the embassy request.  The order is not
        guaranteed, as it mimics the one from the happening, but the
        first one appears to be one the request was accepted from.
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ agreed to construct embassies between %%(.+?)%% and %%(.+?)%%.',
            text
        )
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        self.regions = (
            aionationstates.Region(match.group(2)),
            aionationstates.Region(match.group(3))
        )
        super().__init__(text, params)


class EmbassyConstructionRequestWithdrawal(UnrecognizedHappening):
    """A nation withdrawing a request to construct embassies between two regions.

    Attributes
    ----------
    nation : :class:`Nation`
        Nation performing the action.
    regions : tuple of two :class:`Region` objects
        Regions involved in the embassy request.  The order is not
        guaranteed, as it mimics the one from the happening.
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ withdrew a request for embassies between %%(.+?)%% and %%(.+?)%%.',
            text
        )
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        self.regions = (
            aionationstates.Region(match.group(2)),
            aionationstates.Region(match.group(3))
        )
        super().__init__(text, params)


class EmbassyConstructionAbortion(UnrecognizedHappening):
    """A nation aborting construction of embassies between two regions.

    Attributes
    ----------
    nation : :class:`Nation`
        Nation performing the action.
    regions : tuple of two :class:`Region` objects
        Regions involved in the embassy request.  The order is not
        guaranteed, as it mimics the one from the happening.
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ aborted construction of embassies between %%(.+?)%% and %%(.+?)%%.',
            text
        )
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        self.regions = (
            aionationstates.Region(match.group(2)),
            aionationstates.Region(match.group(3))
        )
        super().__init__(text, params)


class EmbassyClosureOrder(UnrecognizedHappening):
    """A nation ordering closure of embassies between two regions.

    Attributes
    ----------
    nation : :class:`Nation`
        Nation performing the action.
    regions : tuple of two :class:`Region` objects
        Regions involved in the embassy request.  The order is not
        guaranteed, as it mimics the one from the happening.
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ ordered the closure of embassies between %%(.+?)%% and %%(.+?)%%.',
            text
        )
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        self.regions = (
            aionationstates.Region(match.group(2)),
            aionationstates.Region(match.group(3))
        )
        super().__init__(text, params)


class EmbassyEstablishment(UnrecognizedHappening):
    """Embassy being established between two regions.

    Attributes
    ----------
    regions : tuple of two :class:`Region` objects
        Regions involved in the embassy request.  The order is not
        guaranteed, as it mimics the one from the happening.
    """

    def __init__(self, text, params):
        match = re.match(
            'Embassy established between %%(.+?)%% and %%(.+?)%%.',
            text
        )
        if not match:
            raise ValueError
        self.regions = (
            aionationstates.Region(match.group(1)),
            aionationstates.Region(match.group(2))
        )
        super().__init__(text, params)


class EmbassyCancellation(UnrecognizedHappening):
    """Embassy being cancelled between two regions.

    Attributes
    ----------
    regions : tuple of two :class:`Region` objects
        Regions involved in the embassy request.  The order is not
        guaranteed, as it mimics the one from the happening.
    """

    def __init__(self, text, params):
        match = re.match(
            'Embassy cancelled between %%(.+?)%% and %%(.+?)%%.',
            text
        )
        if not match:
            raise ValueError
        self.regions = (
            aionationstates.Region(match.group(1)),
            aionationstates.Region(match.group(2))
        )
        super().__init__(text, params)


class Endorsement(UnrecognizedHappening):
    """A nation endorsing another nation.

    Attributes
    ----------
    endorser : :class:`Nation`
    endorsee : :class:`Nation`
    """

    def __init__(self, text, params):
        match = re.match('@@(.+?)@@ endorsed @@(.+?)@@', text)
        if not match:
            raise ValueError
        self.endorser = aionationstates.Nation(match.group(1))
        self.endorsee = aionationstates.Nation(match.group(2))
        super().__init__(text, params)


class EndorsementWithdrawal(UnrecognizedHappening):
    """A nation withdrawing its endorsement of another nation.

    Attributes
    ----------
    endorser : :class:`Nation`
    endorsee : :class:`Nation`
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ withdrew its endorsement from @@(.+?)@@', text)
        if not match:
            raise ValueError
        self.endorser = aionationstates.Nation(match.group(1))
        self.endorsee = aionationstates.Nation(match.group(2))
        super().__init__(text, params)


class PollCreation(UnrecognizedHappening):
    """A nation creating a new regional poll.

    Note that the poll id is inaccessible from the happening, so the
    created poll can't be linked directly.  The best you can do is
    request the current poll of the region from the happening.

    Attributes
    ----------
    nation : :class:`Nation`
    region : :class:`Region`
    title : str
        Poll title.  Don't rely on this being accurate, some characters
        (such as brackets) are for whatever horror inducing reason
        stripped from the happening.
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ created a new poll in %%(.+?)%%: "(.+?)".', text)
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        self.region = aionationstates.Region(match.group(2))
        self.title = html.unescape(match.group(3))
        super().__init__(text, params)


class PollDeletion(UnrecognizedHappening):
    """A nation deleting a regional poll.

    Attributes
    ----------
    nation : :class:`Nation`
    region : :class:`Region`
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ deleted a regional poll in %%(.+?)%%.', text)
        if not match:
            raise ValueError
        self.nation = aionationstates.Nation(match.group(1))
        self.region = aionationstates.Region(match.group(2))
        super().__init__(text, params)


class ZombieAction(UnrecognizedHappening):
    def __init__(self, match, text, params):
        self.recepient = aionationstates.Nation(match.group(1))
        self.weapon = match.group(2)
        self.sender = aionationstates.Nation(match.group(3))
        self.impact = int(match.group(4))
        super().__init__(text, params)


class ZombieCureAction(ZombieAction):
    """A nation curing another nation during Z-Day.

    Attributes
    ----------
    recepient : :class:`Nation`
    sender : :class:`Nation`
    weapon : str
        Weapon type used, for example *"Mk II (Sterilizer) Cure Missile"*.
    impact : int
        Citizens affected, in millions.
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ was struck by a (.+?) from @@(.+?)@@, curing ([0-9]+) million infected.',
            text
        )
        if not match:
            raise ValueError
        super().__init__(match, text, params)


class ZombieKillAction(ZombieAction):
    """A nation cleansing another nation during Z-Day.

    Attributes
    ----------
    recepient : :class:`Nation`
    sender : :class:`Nation`
    weapon : str
        Weapon type used, for example *"Level 3 Mechanized Tactical
        Zombie Elimination Squad"*.
    impact : int
        Citizens affected, in millions.
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ was cleansed by a (.+?) from @@(.+?)@@, killing ([0-9]+) million zombies.',
            text
        )
        if not match:
            raise ValueError
        super().__init__(match, text, params)


class ZombieInfectAction(ZombieAction):
    """A nation infecting another nation during Z-Day.

    Attributes
    ----------
    recepient : :class:`Nation`
    sender : :class:`Nation`
    weapon : str
        Weapon type used, for example *"Zombie Walker Horde"*.
    impact : int
        Citizens affected, in millions.
    convert : bool
        Whether the nation is converted to a zombie exporter.
    """

    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ was ravaged by a (.+?) from @@(.+?)@@, infecting ([0-9]+) million survivors.',
            text
        )
        if not match:
            raise ValueError
        self.convert = text.endswith('converting to a zombie exporter! Oh no!')
        super().__init__(match, text, params)


happening_classes = (
    Move,
    Founding,
    CTE,
    Legislation,
    FlagChange,
    SettingsChange,
    DispatchPublication,
    WorldAssemblyApplication,
    WorldAssemblyAdmission,
    WorldAssemblyResignation,
    DelegateChange,
    CategoryChange,
    BannerCreation,
    EmbassyConstructionRequest,
    EmbassyConstructionConfirmation,
    EmbassyConstructionRequestWithdrawal,
    EmbassyConstructionAbortion,
    EmbassyClosureOrder,
    EmbassyEstablishment,
    EmbassyCancellation,
    Endorsement,
    EndorsementWithdrawal,
    PollCreation,
    PollDeletion,
    ZombieCureAction,
    ZombieKillAction,
    ZombieInfectAction,
)

__all__ = [cls.__name__ for cls in happening_classes + (UnrecognizedHappening,)]



def process_happening(params):
    # Call ElementTree methods only once, to get a bit of extra performance.
    try:
        params_id = int(params.get('id'))
    except TypeError:
        params_id = None
    params_timestamp = timestamp(params.find('TIMESTAMP').text)
    text = params.findtext('TEXT')
    params = (text, (params_id, params_timestamp))

    for cls in happening_classes:
        with suppress(ValueError):
            return cls(*params)
    # TODO logging
    return UnrecognizedHappening(*params)
