from typing import Tuple, Set, Union, MutableMapping, Any, Mapping, Iterable, Generator, List
import datetime

from datapipelines import Query, PipelineContext, QueryValidationError

from ..data import Region, Platform, Queue, Tier, Season

from ..dto.champion import ChampionListDto as ChampionStatusListDto, ChampionDto as ChampionStatusDto
from ..dto.championmastery import ChampionMasteryDto, ChampionMasteryListDto, ChampionMasteryScoreDto
from ..dto.league import LeagueListDto, LeaguePositionDto
from ..dto.staticdata import ChampionDto, ChampionListDto, ItemDto, ItemListDto, LanguageStringsDto, LanguagesDto, MasteryDto, MasteryListDto, ProfileIconDataDto, ProfileIconDetailsDto, RealmDto, RuneDto, RuneListDto, SummonerSpellDto, SummonerSpellListDto, MapDto, MapListDto, VersionListDto
from ..dto.status import ShardStatusDto
from ..dto.masterypage import MasteryPagesDto, MasteryPageDto
from ..dto.match import MatchDto, MatchReferenceDto, TimelineDto
from ..dto.runepage import RunePagesDto, RunePageDto
from ..dto.spectator import CurrentGameInfoDto, FeaturedGamesDto
from ..dto.summoner import SummonerDto

from ..core.common import provide_default_region
from ..core.championmastery import ChampionMastery, ChampionMasteries
from ..core.league import LeagueEntries, Leagues, ChallengerLeague, MasterLeague
from ..core.staticdata import Champion, Mastery, Rune, Item, SummonerSpell, Map, Locales, LanguageStrings, ProfileIcon, ProfileIcons, Realms, Versions, Items, Champions, Maps, SummonerSpells, Masteries, Runes
from ..core.status import ShardStatus
from ..core.masterypage import MasteryPage, MasteryPages
from ..core.match import Match, MatchHistory, Timeline
from ..core.runepage import RunePage, RunePages
from ..core.summoner import Summoner
from ..core.spectator import CurrentMatch, FeaturedMatches

from ..core.staticdata.champion import ChampionData
from ..core.staticdata.item import ItemData
from ..core.staticdata.summonerspell import SummonerSpellData
from ..core.staticdata.rune import RuneData
from ..core.staticdata.mastery import MasteryData
from ..core.staticdata.map import MapData
from ..core.summoner import Account, SummonerData

#############
# Utilities #
#############


def _rgetattr(obj, key):
    """Recursive getattr for handling dots in keys."""
    for k in key.split("."):
        obj = getattr(obj, k)
    return obj

def _hash_included_data(included_data: Set[str]) -> int:
    return hash(tuple(included_data))


def _get_default_version(query: Mapping[str, Any], context: PipelineContext) -> str:
    try:
        pipeline = context[PipelineContext.Keys.PIPELINE]
        versions = pipeline.get(VersionListDto, {"platform": query["platform"]})
        return versions["versions"][0]
    except TypeError as error:
        raise KeyError("`version` must be provided in query") from error


def _get_default_locale(query: Mapping[str, Any], context: PipelineContext) -> str:
    return query["platform"].default_locale


def _region_to_platform_generator(regions: Iterable[Region]) -> Generator[Platform, None, None]:
    for region in regions:
        try:
            yield Region(region).platform
        except ValueError as e:
            raise QueryValidationError from e


def convert_region_to_platform(query: MutableMapping[str, Any]) -> None:
    if "region" in query and "platform" not in query:
        try:
            query["platform"] = Region(query["region"]).platform
        except ValueError as e:
            raise QueryValidationError from e

    if "regions" in query and "platforms" not in query:
        query["platforms"] = _region_to_platform_generator(query["regions"])


#########################################
# Construct Query From kwargs Functions #
#########################################


def construct_query(cls, **kwargs) -> dict:
    if cls is ChampionMastery:
        return construct_champion_mastery_query(**kwargs)
    if cls is ChampionMasteries:
        return construct_champion_masteries_query(**kwargs)
    if cls is Summoner:
        return construct_summoner_query(**kwargs)
    if cls is CurrentMatch:
        return construct_current_match_query(**kwargs)
    if cls is Leagues or cls is LeagueEntries:
        return construct_leagues_query(**kwargs)
    if cls is MasteryPages or cls is RunePages:
        return construct_pages_query(**kwargs)
    if cls is MatchHistory:
        return construct_match_history_query(**kwargs)
    else:
        return kwargs


@provide_default_region
def construct_summoner_query(*, id: int = None, account: Union[Account, int] = None, name: str = None, region: Union[Region, str]) -> dict:
    query = {"region": region}
    if id is not None:
        query["id"] = id
    if name is not None:
        query["name"] = name
    if account and isinstance(account, Account):
        query["account.id"] = account.id
    elif account is not None:
        query["account.id"] = account
    return query


@provide_default_region
def construct_champion_mastery_query(*, summoner: Union[Summoner, int, str], champion: Union[Champion, int, str], region: Union[Region, str]) -> dict:
    query = {"region": region}
    if isinstance(summoner, Summoner):
        summoner_data = summoner._data[SummonerData]
        try:
            query["summoner.id"] = summoner_data.id
        except KeyError:
            try:
                query["summoner.account.id"] = summoner_data.account_id
            except KeyError:
                query["summoner.name"] = summoner_data.name
    elif isinstance(summoner, str):
        query["summoner.name"] = summoner
    else:  # int
        query["summoner.id"] = summoner

    if isinstance(champion, Champion):
        champion_data = champion._data[ChampionData]
        try:
            query["champion.id"] = champion_data.id
        except KeyError:
            query["champion.name"] = champion_data.name
    elif isinstance(champion, str):
        query["champion.name"] = champion
    else:  # int
        query["champion.id"] = champion
    return query


@provide_default_region
def construct_champion_masteries_query(*, summoner: Union[Summoner, int, str], region: Union[Region, str]) -> dict:
    query = {"region": region}
    if isinstance(summoner, Summoner):
        summoner_data = summoner._data[SummonerData]
        try:
            query["summoner.id"] = summoner_data.id
        except KeyError:
            try:
                query["summoner.account.id"] = summoner_data.account_id
            except KeyError:
                query["summoner.name"] = summoner_data.name
    elif isinstance(summoner, str):
        query["summoner.name"] = summoner
    else:  # int
        query["summoner.id"] = summoner
    return query


@provide_default_region
def construct_pages_query(*args, summoner: Union[Summoner, int, str], region: Union[Region, str]) -> dict:
    query = {"region": region}
    if isinstance(summoner, Summoner):
        summoner_data = summoner._data[SummonerData]
        try:
            query["summoner.id"] = summoner_data.id
        except KeyError:
            try:
                query["summoner.account.id"] = summoner_data.account_id
            except KeyError:
                query["summoner.name"] = summoner_data.name
    elif isinstance(summoner, str):
        query["summoner.name"] = summoner
    else:  # int
        query["summoner.id"] = summoner
    return query


@provide_default_region
def construct_current_match_query(*, summoner: Union[Summoner, int, str], region: Union[Region, str]) -> dict:
    query = {"region": region}
    if isinstance(summoner, Summoner):
        query["summoner.id"] = summoner.id
    elif isinstance(summoner, int):  # int
        query["summoner.id"] = summoner
    elif isinstance(summoner, str):
        query["summoner.id"] = Summoner(name=summoner, region=region).id
    assert "summoner.id" in query
    return query


@provide_default_region
def construct_leagues_query(*, summoner: Union[Summoner, int, str], region: Union[Region, str]) -> dict:
    query = {"region": region}
    if isinstance(summoner, Summoner):
        query["summoner.id"] = summoner.id
    elif isinstance(summoner, int):  # int
        query["summoner.id"] = summoner
    elif isinstance(summoner, str):
        query["summoner.id"] = Summoner(name=summoner, region=region).id
    assert "summoner.id" in query
    return query

@provide_default_region
def construct_match_history_query(*, summoner: Union[Summoner, str, int] = None, account_id: int = None, region: Union[Region, str] = None, begin_index: int = 0, end_index: int = None, begin_time: datetime.datetime = None, end_time: datetime.datetime = None, queues: Set[Queue] = None, seasons: Set[Season] = None, champions: Set[Champion] = None):
    query = {"region": region, "beginIndex": begin_index}
    if account_id is not None:
        query["account.id"] = account_id
    else:
        if isinstance(summoner, Summoner):
            query["account.id"] = summoner.account.id
        elif isinstance(summoner, str):
            summoner = Summoner(name=summoner, region=region)
            query["account.id"] = summoner.account.id
        else:  # int
            summoner = Summoner(id=summoner, region=region)
            query["account.id"] = summoner.account.id

    if end_index is not None:
        query["endIndex"] = end_index

    if begin_time is not None:
        if isinstance(begin_time, datetime.datetime):
            begin_time = int(begin_time.timestamp() * 1000)
        query["beginTime"] = begin_time

    if end_time is not None:
        if isinstance(end_time, datetime.datetime):
            end_time = int(end_time.timestamp() * 1000)
        query["endTime"] = end_time

    if queues is not None:
        query["queues"] = queues

    if seasons is not None:
        query["seasons"] = seasons

    if champions is not None:
        query["champions"] = champions

    return query


#######
# DTO #
#######


################
# Champion API #
################


validate_champion_status_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("id").as_(int)


validate_many_champion_status_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("ids").as_(Iterable)


def for_champion_status_dto(champion_status: ChampionStatusDto) -> Tuple[str, int]:
    return champion_status["platform"], champion_status["id"]


def for_champion_status_dto_query(query: Query) -> Tuple[str, int]:
    return query["platform"].value, query["id"]


def for_many_champion_status_dto_query(query: Query) -> Generator[Tuple[str, int], None, None]:
    for id in query["ids"]:
        try:
            id = int(id)
            yield query["platform"].value, id
        except ValueError as e:
            raise QueryValidationError from e


validate_champion_status_list_dto_query = Query. \
    has("platform").as_(Platform)


validate_many_champion_status_list_dto_query = Query. \
    has("platforms").as_(Iterable)


def for_champion_status_list_dto(champion_status_list: ChampionStatusListDto) -> str:
    return champion_status_list["platform"]


def for_champion_status_list_dto_query(query: Query) -> str:
    return query["platform"].value


def for_many_champion_status_list_dto_query(query: Query) -> Generator[str, None, None]:
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield platform.value
        except ValueError as e:
            raise QueryValidationError from e


########################
# Champion Mastery API #
########################


validate_champion_mastery_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("playerId").as_(int).also. \
    has("championId").as_(int)


validate_many_champion_mastery_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("playerId").as_(int).also. \
    has("championIds").as_(Iterable)


def for_champion_mastery_dto(champion_mastery: ChampionMasteryDto) -> Tuple[str, int, int]:
    return champion_mastery["platform"], champion_mastery["playerId"], champion_mastery["championId"]


def for_champion_mastery_dto_query(query: Query) -> Tuple[str, int, int]:
    return query["platform"].value, query["playerId"], query["championId"]


def for_many_champion_mastery_dto_query(query: Query) -> Generator[Tuple[str, int, int], None, None]:
    for champion_id in query["championIds"]:
        try:
            champion_id = int(champion_id)
            yield query["platform"].value, query["playerId"], champion_id
        except ValueError as e:
            raise QueryValidationError from e


validate_champion_mastery_list_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("playerId").as_(int)


validate_many_champion_mastery_list_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("playerIds").as_(Iterable)


def for_champion_mastery_list_dto(champion_mastery_list: ChampionMasteryListDto) -> Tuple[str, int]:
    return champion_mastery_list["platform"], champion_mastery_list["playerId"]


def for_champion_mastery_list_dto_query(query: Query) -> Tuple[str, int]:
    return query["platform"].value, query["playerId"]


def for_many_champion_mastery_list_dto_query(query: Query) -> Generator[Tuple[str, int], None, None]:
    for summoner_id in query["playerIds"]:
        try:
            summoner_id = int(summoner_id)
            yield query["platform"].value, summoner_id
        except ValueError as e:
            raise QueryValidationError from e


validate_champion_mastery_score_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("playerId").as_(int)


validate_many_champion_mastery_score_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("playerIds").as_(Iterable)


def for_champion_mastery_score_dto(champion_mastery_score: ChampionMasteryScoreDto) -> Tuple[str, int]:
    return champion_mastery_score["platform"], champion_mastery_score["playerId"]


def for_champion_mastery_score_dto_query(query: Query) -> Tuple[str, int]:
    return query["platform"].value, query["playerId"]


def for_many_champion_mastery_score_dto_query(query: Query) -> Generator[Tuple[str, int], None, None]:
    for summoner_id in query["playerIds"]:
        try:
            summoner_id = int(summoner_id)
            yield query["platform"].value, summoner_id
        except ValueError as e:
            raise QueryValidationError from e


##############
# League API #
##############


validate_league_list_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("queue").as_(Queue).also. \
    has("tier").as_(Tier).also. \
    has("name").as_(str)


validate_many_league_list_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("queue").as_(Queue).also. \
    has("tier").as_(Tier).also. \
    has("names").as_(Iterable)


def for_league_list_dto(league_list: LeagueListDto) -> Tuple[str, str, str, str]:
    return league_list["platform"], league_list["queue"], league_list["tier"], league_list["name"]


def for_league_list_dto_query(query: Query) -> Tuple[str, str, str, str]:
    return query["platform"].value, query["queue"].value, query["tier"].value, query["name"]


def for_many_league_list_dto_query(query: Query) -> Generator[Tuple[str, str, str, str], None, None]:
    for name in query["names"]:
        try:
            name = str(name)
            yield query["platform"].value, query["queue"].value, query["tier"].value, name
        except ValueError as e:
            raise QueryValidationError from e


validate_league_positions_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("summonerId").as_(int)


validate_many_league_positions_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("summonerIds").as_(Iterable)


def for_league_positions_dto(league_positions: LeaguePositionDto) -> Tuple[str, int]:
    return league_positions["platform"], league_positions["summonerId"]


def for_league_positions_dto_query(query: Query) -> Tuple[str, int]:
    return query["platform"].value, query["summonerId"]


def for_many_league_positions_dto_query(query: Query) -> Generator[Tuple[str, int], None, None]:
    for summoner_id in query["summonerIds"]:
        try:
            summoner_id = int(summoner_id)
            yield query["platform"].value, summoner_id
        except ValueError as e:
            raise QueryValidationError from e


###################
# Static Data API #
###################


# Champion

validate_champion_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("id").as_(int).or_("name").as_(str)


validate_many_champion_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("ids").as_(Iterable).or_("names").as_(Iterable)


def for_champion_dto(champion: ChampionDto, identifier: str = "id") -> Tuple[str, str, str, int, Union[int, str]]:
    return champion["platform"], champion["version"], champion["locale"], _hash_included_data(champion["includedData"]), champion[identifier]


def for_champion_dto_query(query: Query) -> Tuple[str, str, str, int, Union[int, str]]:
    identifier = "id" if "id" in query else "name"
    return query["platform"].value, query["version"], query["locale"], _hash_included_data(query["includedData"]), query[identifier]


def for_many_champion_dto_query(query: Query) -> Generator[Tuple[str, str, str, int, Union[int, str]], None, None]:
    identifiers, identifier_type = (query["ids"], int) if "ids" in query else (query["names"], str)
    included_data_hash = _hash_included_data(query["includedData"])
    for identifier in identifiers:
        try:
            identifier = identifier_type(identifier)
            yield query["platform"].value, query["version"], query["locale"], included_data_hash, identifier
        except ValueError as e:
            raise QueryValidationError from e


validate_champion_list_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


validate_many_champion_list_dto_query = Query. \
    has("platforms").as_(Iterable).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


def for_champion_list_dto(champion_list: ChampionListDto) -> Tuple[str, str, str, int]:
    return champion_list["platform"], champion_list["version"], champion_list["locale"], _hash_included_data(champion_list["includedData"])


def for_champion_list_dto_query(query: Query) -> Tuple[str, str, str, int]:
    return query["platform"].value, query["version"], query["locale"], _hash_included_data(query["includedData"])


def for_many_champion_list_dto_query(query: Query) -> Generator[Tuple[str, str, str, int], None, None]:
    included_data_hash = _hash_included_data(query["includedData"])
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield platform.value, query["version"], query["locale"], included_data_hash
        except ValueError as e:
            raise QueryValidationError from e


# Item


validate_item_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("id").as_(int).or_("name").as_(str)


validate_many_item_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("ids").as_(Iterable).or_("name").as_(Iterable)


def for_item_dto(item: ItemDto, identifier: str = "id") -> Tuple[str, str, str, int, Union[int, str]]:
    return item["platform"], item["version"], item["locale"], _hash_included_data(item["includedData"]), item[identifier]


def for_item_dto_query(query: Query) -> Tuple[str, str, str, int, Union[int, str]]:
    identifier = "id" if "id" in query else "name"
    return query["platform"].value, query["version"], query["locale"], _hash_included_data(query["includedData"]), query[identifier]


def for_many_item_dto_query(query: Query) -> Generator[Tuple[str, str, str, int, Union[int, str]], None, None]:
    identifiers, identifier_type = (query["ids"], int) if "ids" in query else (query["names"], str)
    included_data_hash = _hash_included_data(query["includedData"])
    for identifier in identifiers:
        try:
            identifier = identifier_type(identifier)
            yield query["platform"].value, query["version"], query["locale"], included_data_hash, identifier
        except ValueError as e:
            raise QueryValidationError from e


validate_item_list_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


validate_many_item_list_dto_query = Query. \
    has("platforms").as_(Iterable).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


def for_item_list_dto(item_list: ItemListDto) -> Tuple[str, str, str, int]:
    return item_list["platform"], item_list["version"], item_list["locale"], _hash_included_data(item_list["includedData"])


def for_item_list_dto_query(query: Query) -> Tuple[str, str, str, int]:
    return query["platform"].value, query["version"], query["locale"], _hash_included_data(query["includedData"])


def for_many_item_list_dto_query(query: Query) -> Generator[Tuple[str, str, str, int], None, None]:
    included_data_hash = _hash_included_data(query["includedData"])
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield platform.value, query["version"], query["locale"], included_data_hash
        except ValueError as e:
            raise QueryValidationError from e


# Language


validate_language_strings_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str)


validate_many_language_strings_dto_query = Query. \
    has("platforms").as_(Iterable).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str)


def for_language_strings_dto(language_strings: LanguageStringsDto) -> Tuple[str, str, str]:
    return language_strings["platform"], language_strings["version"], language_strings["locale"]


def for_language_strings_dto_query(query: Query) -> Tuple[str, str, str]:
    return query["platform"].value, query["version"], query["locale"]


def for_many_language_strings_dto_query(query: Query) -> Generator[Tuple[str, str, str], None, None]:
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield platform.value, query["version"], query["locale"]
        except ValueError as e:
            raise QueryValidationError from e


validate_languages_dto_query = Query. \
    has("platform").as_(Platform)


validate_many_languages_dto_query = Query. \
    has("platforms").as_(Iterable)


def for_languages_dto(languages: LanguagesDto) -> str:
    return languages["platform"]


def for_languages_dto_query(query: Query) -> str:
    return query["platform"].value


def for_many_languages_dto_query(query: Query) -> Generator[str, None, None]:
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield platform.value
        except ValueError as e:
            raise QueryValidationError from e


# Map

validate_map_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    has("mapId").as_(int).or_("mapName").as_(str)


validate_many_map_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    has("mapIds").as_(Iterable).or_("mapNames").as_(Iterable)


def for_map_dto(map: MapDto, identifier: str = "mapId") -> Tuple[str, str, str, Union[int, str]]:
    return map["platform"], map["version"], map["locale"], map[identifier]


def for_map_dto_query(query: Query) -> Tuple[str, str, str, Union[int, str]]:
    identifier = "mapId" if "mapId" in query else "mapName"
    return query["platform"].value, query["version"], query["locale"], query[identifier]


def for_many_map_dto_query(query: Query) -> Generator[Tuple[str, str, str, Union[int, str]], None, None]:
    identifiers, identifier_type = (query["mapIds"], int) if "mapIds" in query else (query["mapNames"], str)
    for identifier in identifiers:
        try:
            identifier = identifier_type(identifier)
            yield query["platform"].value, query["version"], query["locale"], identifier
        except ValueError as e:
            raise QueryValidationError from e


validate_map_list_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str)


validate_many_map_list_dto_query = Query. \
    has("platforms").as_(Iterable).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str)


def for_map_list_dto(map_list: MapListDto) -> Tuple[str, str, str]:
    return map_list["platform"], map_list["version"], map_list["locale"]


def for_map_list_dto_query(query: Query) -> Tuple[str, str, str]:
    return query["platform"].value, query["version"], query["locale"]


def for_many_map_list_dto_query(query: Query) -> Generator[Tuple[str, str, str], None, None]:
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield platform.value, query["version"], query["locale"]
        except ValueError as e:
            raise QueryValidationError from e


# Mastery

validate_mastery_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("id").as_(int).or_("name").as_(str)


validate_many_mastery_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("ids").as_(Iterable).or_("names").as_(Iterable)


def for_mastery_dto(mastery: MasteryDto, identifier: str = "id") -> Tuple[str, str, str, int, Union[int, str]]:
    return mastery["platform"], mastery["version"], mastery["locale"], _hash_included_data(mastery["includedData"]), mastery[identifier]


def for_mastery_dto_query(query: Query) -> Tuple[str, str, str, int, Union[int, str]]:
    identifier = "id" if "id" in query else "name"
    return query["platform"], query["version"], query["locale"], _hash_included_data(query["includedData"]), query[identifier]


def for_many_mastery_dto_query(query: Query) -> Generator[Tuple[str, str, str, int, Union[int, str]], None, None]:
    identifiers, identifier_type = (query["ids"], int) if "ids" in query else (query["names"], str)
    included_data_hash = _hash_included_data(query["includedData"])
    for identifier in identifiers:
        try:
            identifier = identifier_type(identifier)
            yield query["platform"].value, query["version"], query["locale"], included_data_hash, identifier
        except ValueError as e:
            raise QueryValidationError from e


validate_mastery_list_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


validate_many_mastery_list_dto_query = Query. \
    has("platforms").as_(Iterable).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


def for_mastery_list_dto(mastery_list: MasteryListDto) -> Tuple[str, str, str, int]:
    return mastery_list["platform"], mastery_list["version"], mastery_list["locale"], _hash_included_data(mastery_list["includedData"])


def for_mastery_list_dto_query(query: Query) -> Tuple[str, str, str, int]:
    return query["platform"], query["version"], query["locale"], _hash_included_data(query["includedData"])


def for_many_mastery_list_dto_query(query: Query) -> Generator[Tuple[str, str, str, int], None, None]:
    included_data_hash = _hash_included_data(query["includedData"])
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield platform.value, query["version"], query["locale"], included_data_hash
        except ValueError as e:
            raise QueryValidationError from e


# Profile Icon


validate_profile_icon_data_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str)


validate_many_profile_icon_data_dto_query = Query. \
    has("platforms").as_(Iterable).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str)


def for_profile_icon_data_dto(profile_icon_data: ProfileIconDataDto) -> Tuple[str, str, str]:
    return profile_icon_data["platform"], profile_icon_data["version"], profile_icon_data["locale"]


def for_profile_icon_data_dto_query(query: Query) -> Tuple[str, str, str]:
    return query["platform"].value, query["version"], query["locale"]


def for_many_profile_icon_data_dto_query(query: Query) -> Generator[Tuple[str, str, str], None, None]:
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield platform.value, query["version"], query["locale"]
        except ValueError as e:
            raise QueryValidationError from e


validate_profile_icon_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    has("id").as_(int)


validate_many_profile_icon_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    has("ids").as_(Iterable)


def for_profile_icon_dto(profile_icon: ProfileIconDetailsDto) -> Tuple[str, str, str, int]:
    return profile_icon["platform"], profile_icon["version"], profile_icon["locale"], profile_icon["id"]


def for_profile_icon_dto_query(query: Query) -> Tuple[str, str, str, int]:
    return query["platform"].value, query["version"], query["locale"], query["id"]


def for_many_profile_icon_dto_query(query: Query) -> Generator[Tuple[str, str, str, int], None, None]:
    for id in query["ids"]:
        try:
            id = int(id)
            yield query["platform"].value, query["version"], query["locale"], id
        except ValueError as e:
            raise QueryValidationError from e


# Realm


validate_realm_dto_query = Query. \
    has("platform").as_(Platform)


validate_many_realm_dto_query = Query. \
    has("platforms").as_(Iterable)


def for_realm_dto(realm: RealmDto) -> str:
    return realm["platform"]


def for_realm_dto_query(query: Query) -> str:
    return query["platform"].value


def for_many_realm_dto_query(query: Query) -> Generator[str, None, None]:
    return query["platform"].value


# Rune


validate_rune_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("id").as_(int).or_("name").as_(str)


validate_many_rune_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("ids").as_(Iterable).or_("names").as_(Iterable)


def for_rune_dto(rune: RuneDto, identifier: str = "id") -> Tuple[str, str, str, int, Union[int, str]]:
    return rune["platform"], rune["version"], rune["locale"], _hash_included_data(rune["includedData"]), rune[identifier]


def for_rune_dto_query(query: Query) -> Tuple[str, str, str, int, Union[int, str]]:
    identifier = "id" if "id" in query else "name"
    return query["platform"].value, query["version"], query["locale"], _hash_included_data(query["includedData"]), query[identifier]


def for_many_rune_dto_query(query: Query) -> Generator[Tuple[str, str, str, int, Union[int, str]], None, None]:
    identifiers, identifier_type = (query["ids"], int) if "ids" in query else (query["names"], str)
    included_data_hash = _hash_included_data(query["includedData"])
    for identifier in identifiers:
        try:
            identifier = identifier_type(identifier)
            yield query["platform"].value, query["version"], query["locale"], included_data_hash, identifier
        except ValueError as e:
            raise QueryValidationError from e


validate_rune_list_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


validate_many_rune_list_dto_query = Query. \
    has("platforms").as_(Iterable).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


def for_rune_list_dto(rune_list: RuneListDto) -> Tuple[str, str, str, int]:
    return rune_list["platform"], rune_list["version"], rune_list["locale"], _hash_included_data(rune_list["includedData"])


def for_rune_list_dto_query(query: Query) -> Tuple[str, str, str, int]:
    return query["platform"].value, query["version"], query["locale"], _hash_included_data(query["includedData"])


def for_many_rune_list_dto_query(query: Query) -> Generator[Tuple[str, str, str, int], None, None]:
    included_data_hash = _hash_included_data(query["includedData"])
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield platform.value, query["version"], query["locale"], included_data_hash
        except ValueError as e:
            raise QueryValidationError from e


# Summoner Spell


validate_summoner_spell_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("id").as_(int).or_("name").as_(str)


validate_many_summoner_spell_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("ids").as_(Iterable).or_("names").as_(Iterable)


def for_summoner_spell_dto(summoner_spell: SummonerSpellDto, identifier: str = "id") -> Tuple[str, str, str, int, Union[int, str]]:
    return summoner_spell["platform"], summoner_spell["version"], summoner_spell["locale"], _hash_included_data(summoner_spell["includedData"]), summoner_spell[identifier]


def for_summoner_spell_dto_query(query: Query) -> Tuple[str, str, str, int, Union[int, str]]:
    identifier = "id" if "id" in query else "name"
    return query["platform"].value, query["version"], query["locale"], _hash_included_data(query["includedData"]), query[identifier]


def for_many_summoner_spell_dto_query(query: Query) -> Generator[Tuple[str, str, str, int, Union[int, str]], None, None]:
    identifiers, identifier_type = (query["ids"], int) if "ids" in query else (query["names"], str)
    included_data_hash = _hash_included_data(query["includedData"])
    for identifier in identifiers:
        try:
            identifier = identifier_type(identifier)
            yield query["platform"].value, query["version"], query["locale"], included_data_hash, identifier
        except ValueError as e:
            raise QueryValidationError from e


validate_summoner_spell_list_dto_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


validate_many_summoner_spell_list_dto_query = Query. \
    has("platforms").as_(Iterable).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


def for_summoner_spell_list_dto(summoner_spell_list: SummonerSpellListDto) -> Tuple[str, str, str, int]:
    return summoner_spell_list["platform"], summoner_spell_list["version"], summoner_spell_list["locale"], _hash_included_data(summoner_spell_list["includedData"])


def for_summoner_spell_list_dto_query(query: Query) -> Tuple[str, str, str, int]:
    return query["platform"].value, query["version"], query["locale"], _hash_included_data(query["includedData"])


def for_many_summoner_spell_list_dto_query(query: Query) -> Generator[Tuple[str, str, str, int], None, None]:
    included_data_hash = _hash_included_data(query["includedData"])
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield platform.value, query["version"], query["locale"], included_data_hash
        except ValueError as e:
            raise QueryValidationError from e


# Version


validate_version_list_dto_query = Query. \
    has("platform").as_(Platform)


validate_many_version_list_dto_query = Query. \
    has("platforms").as_(Iterable)


def for_version_list_dto(version_list: VersionListDto) -> str:
    return version_list["platform"]


def for_version_list_dto_query(query: Query) -> str:
    return query["platform"].value


def for_many_version_list_dto_query(query: Query) -> Generator[str, None, None]:
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield platform.value
        except ValueError as e:
            raise QueryValidationError from e


##############
# Status API #
##############


validate_shard_status_dto_query = Query. \
    has("platform").as_(Platform)


validate_many_shard_status_dto_query = Query. \
    has("platforms").as_(Iterable)


def for_shard_status_dto(shard_status: ShardStatusDto) -> str:
    return shard_status["platform"]


def for_shard_status_dto_query(query: Query) -> str:
    return query["platform"].value


def for_many_shard_status_dto_query(query: Query) -> Generator[str, None, None]:
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield platform.value
        except ValueError as e:
            raise QueryValidationError from e


#################
# Masteries API #
#################


validate_mastery_page_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("summonerId").also. \
    has("id").as_(int)


validate_many_mastery_page_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("summonerId").also. \
    has("ids").as_(Iterable)


def for_mastery_page_dto(mastery_page: MasteryPageDto) -> Tuple[str, int, int]:
    return mastery_page["platform"], mastery_page["summonerId"], mastery_page["id"]


def for_mastery_page_dto_query(query: Query) -> Tuple[str, int, int]:
    return query["platform"].value, query["summonerId"], query["id"]


def for_many_mastery_page_dto_query(query: Query) -> Generator[Tuple[str, int, int], None, None]:
    for id in query["ids"]:
        try:
            id = int(id)
            yield query["platform"].value, query["summonerId"], id
        except ValueError as e:
            raise QueryValidationError from e


validate_mastery_pages_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("summonerId").as_(int)


validate_many_mastery_pages_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("summonerIds").as_(Iterable)


def for_mastery_pages_dto(mastery_pages: MasteryPagesDto) -> Tuple[str, int]:
    return mastery_pages["platform"], mastery_pages["summonerId"]


def for_mastery_pages_dto_query(query: Query) -> Tuple[str, int]:
    return query["platform"].value, query["summonerId"]


def for_many_mastery_pages_dto_query(query: Query) -> Generator[Tuple[str, int], None, None]:
    for summoner_id in query["summonerIds"]:
        try:
            summoner_id = int(summoner_id)
            yield query["platform"].value, summoner_id
        except ValueError as e:
            raise QueryValidationError from e


#############
# Match API #
#############


validate_match_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("gameId").as_(int)


validate_many_match_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("gameIds").as_(Iterable)


def for_match_dto(match: MatchDto) -> Tuple[str, int]:
    return match["platform"], match["gameId"]


def for_match_dto_query(query: Query) -> Tuple[str, int]:
    return query["platform"].value, query["gameId"]


def for_many_match_dto_query(query: Query) -> Generator[Tuple[str, int], None, None]:
    for game_id in query["gameIds"]:
        try:
            game_id = int(game_id)
            yield query["platform"].value, game_id
        except ValueError as e:
            raise QueryValidationError from e


validate_match_reference_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("gameId").as_(int)


validate_many_match_reference_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("gameIds").as_(Iterable)


def for_match_reference_dto(match_reference: MatchReferenceDto) -> Tuple[str, int]:
    return match_reference["platform"], match_reference["gameId"]


def for_match_reference_dto_query(query: Query) -> Tuple[str, int]:
    return query["platform"].value, query["gameId"]


def for_many_match_reference_dto_query(query: Query) -> Generator[Tuple[str, int], None, None]:
    for game_id in query["gameIds"]:
        try:
            game_id = int(game_id)
            yield query["platform"].value, game_id
        except ValueError as e:
            raise QueryValidationError from e


validate_match_timeline_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("matchId").as_(int)


validate_many_match_timeline_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("matchIds").as_(Iterable)


def for_match_timeline_dto(match_timeline: TimelineDto) -> Tuple[str, int]:
    return match_timeline["platform"], match_timeline["matchId"]


def for_match_timeline_dto_query(query: Query) -> Tuple[str, int]:
    return query["platform"].value, query["matchId"]


def for_many_match_timeline_dto_query(query: Query) -> Generator[Tuple[str, int], None, None]:
    for match_id in query["matchIds"]:
        try:
            match_id = int(match_id)
            yield query["platform"].value, match_id
        except ValueError as e:
            raise QueryValidationError from e


#############
# Runes API #
#############


validate_rune_page_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("summonerId").as_(int).also. \
    has("id").as_(int)


validate_many_rune_page_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("summonerId").also. \
    has("ids").as_(Iterable)


def for_rune_page_dto(rune_page: RunePageDto) -> Tuple[str, int, int]:
    return rune_page["platform"], rune_page["summonerId"], rune_page["id"]


def for_rune_page_dto_query(query: Query) -> Tuple[str, int, int]:
    return query["platform"].value, query["summonerId"], query["id"]


def for_many_rune_page_dto_query(query: Query) -> Generator[Tuple[str, int, int], None, None]:
    for id in query["ids"]:
        try:
            id = int(id)
            yield query["platform"].value, query["summonerId"], id
        except ValueError as e:
            raise QueryValidationError from e


validate_rune_pages_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("summonerId").as_(int)


validate_many_rune_pages_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("summonerIds").as_(Iterable)


def for_rune_pages_dto(rune_pages: RunePagesDto) -> Tuple[str, int]:
    return rune_pages["platform"], rune_pages["summonerId"]


def for_rune_pages_dto_query(query: Query) -> Tuple[str, int]:
    return query["platform"].value, query["summonerId"]


def for_many_rune_pages_dto_query(query: Query) -> Generator[Tuple[str, int], None, None]:
    for summoner_id in query["summonerIds"]:
        try:
            summoner_id = int(summoner_id)
            yield query["platform"].value, summoner_id
        except ValueError as e:
            raise QueryValidationError from e


#################
# Spectator API #
#################


validate_current_game_info_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("gameId").as_(int)


validate_many_current_game_info_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("gameIds").as_(Iterable)


def for_current_game_info_dto(current_game_info: CurrentGameInfoDto) -> Tuple[str, int]:
    return current_game_info["platform"], current_game_info["gameId"]


def for_current_game_info_dto_query(query: Query) -> Tuple[str, int]:
    return query["platform"].value, query["gameId"]


def for_many_current_game_info_dto_query(query: Query) -> Generator[Tuple[str, int], None, None]:
    for game_id in query["gameIds"]:
        try:
            game_id = int(game_id)
            yield query["platform"].value, game_id
        except ValueError as e:
            raise QueryValidationError from e


validate_featured_game_dto_query = Query. \
    has("platform").as_(Platform)


validate_many_featured_game_dto_query = Query. \
    has("platforms").as_(Iterable)


def for_featured_games_dto(featured_games: FeaturedGamesDto) -> str:
    return featured_games["platform"]


def for_featured_games_dto_query(query: Query) -> str:
    return query["platform"].value


def for_many_featured_games_dto_query(query: Query) -> Generator[str, None, None]:
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield platform.value
        except ValueError as e:
            raise QueryValidationError from e


################
# Summoner API #
################


validate_summoner_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("id").as_(int).or_("accountId").as_(int).or_("name").as_(str)


validate_many_summoner_dto_query = Query. \
    has("platform").as_(Platform).also. \
    has("ids").as_(Iterable).or_("accountIds").as_(Iterable).or_("names").as_(Iterable)


def for_summoner_dto(summoner: SummonerDto, identifier: str = "id") -> Tuple[str, Union[int, str]]:
    return summoner["platform"], summoner[identifier]


def for_summoner_dto_query(query: Query) -> Tuple[str, Union[int, str]]:
    if "id" in query:
        identifier = "id"
    elif "accountId" in query:
        identifier = "accountId"
    else:
        identifier = "name"
    return query["platform"].value, query[identifier]


def for_many_summoner_dto_query(query: Query) -> Generator[Tuple[str, Union[int, str]], None, None]:
    if "ids" in query:
        identifiers, identifier_type = query["ids"], int
    elif "accountIds" in query:
        identifiers, identifier_type = query["accountIds"], int
    else:
        identifiers, identifier_type = query["names"], str
    for identifier in identifiers:
        try:
            identifier = identifier_type(identifier)
            yield query["platform"].value, identifier
        except ValueError as e:
            raise QueryValidationError from e


########
# Core #
########


##########################################################
# Champion API (Covered by Static Data Champion in core) #
##########################################################


########################
# Champion Mastery API #
########################


validate_champion_mastery_query = Query. \
    has("platform").as_(Platform).also. \
    has("summoner.id").as_(int).or_("summoner.account.id").as_(int).or_("summoner.name").as_(str).also. \
    has("champion.id").as_(int).or_("champion.name").as_(str)


validate_many_champion_mastery_query = Query. \
    has("platform").as_(Platform).also. \
    has("summoner.id").as_(int).or_("summoner.account.id").as_(int).or_("summoner.name").as_(str).also. \
    has("champions.id").as_(Iterable).or_("champions.name").as_(Iterable)


def for_champion_mastery(champion_mastery: ChampionMastery) -> List[Tuple]:
    keys = []
    try:
        keys.append((champion_mastery.platform.value, champion_mastery.summoner._data[SummonerData].id, champion_mastery.champion._data[ChampionData].id))
    except KeyError:
        pass
    try:
        keys.append((champion_mastery.platform.value, champion_mastery.summoner._data[SummonerData].id, champion_mastery.champion._data[ChampionData].name))
    except KeyError:
        pass
    try:
        keys.append((champion_mastery.platform.value, champion_mastery.summoner._data[SummonerData].name, champion_mastery.champion._data[ChampionData].id))
    except KeyError:
        pass
    try:
        keys.append((champion_mastery.platform.value, champion_mastery.summoner._data[SummonerData].name, champion_mastery.champion._data[ChampionData].name))
    except KeyError:
        pass
    try:
        keys.append((champion_mastery.platform.value, champion_mastery.summoner._data[SummonerData].account_id, champion_mastery.champion._data[ChampionData].id))
    except KeyError:
        pass
    try:
        keys.append((champion_mastery.platform.value, champion_mastery.summoner._data[SummonerData].account_id, champion_mastery.champion._data[ChampionData].name))
    except KeyError:
        pass
    return keys


def for_champion_mastery_query(query: Query) -> List[Tuple]:
    keys = []
    if "summoner.id" in query and "champion.id" in query:
        keys.append((query["platform"].value, query["summoner.id"], query["champion.id"]))
    if "summoner.id" in query and "champion.name" in query:
        keys.append((query["platform"].value, query["summoner.id"], query["champion.name"]))
    if "summoner.name" in query and "champion.id" in query:
        keys.append((query["platform"].value, query["summoner.name"], query["champion.id"]))
    if "summoner.name" in query and "champion.name" in query:
        keys.append((query["platform"].value, query["summoner.name"], query["champion.name"]))
    if "summoner.account.id" in query and "champion.id" in query:
        keys.append((query["platform"].value, query["summoner.account.id"], query["champion.id"]))
    if "summoner.account.id" in query and "champion.name" in query:
        keys.append((query["platform"].value, query["summoner.account.id"], query["champion.name"]))
    return keys


def for_many_champion_mastery_query(query: Query) -> Generator[Tuple[str, str, str, int, Union[int, str]], None, None]:
    grouped_identifiers = []
    identifier_types = []
    if "champions.id" in query:
        grouped_identifiers.append(query["ids"])
        identifier_types.append(int)
    if "champions.name" in query:
        grouped_identifiers.append(query["names"])
        identifier_types.append(str)
    for identifiers in zip(*grouped_identifiers):
        keys = []
        for identifier, identifier_type in zip(identifiers, identifier_types):
            identifier = identifier_type(identifier)
            if "summoner.id" in query:
                keys.append((query["platform"].value, query["summoner.id"], identifier))
            if "summoner.name" in query:
                keys.append((query["platform"].value, query["summoner.name"], identifier))
            if "summoner.account.id" in query:
                keys.append((query["platform"].value, query["summoner.account.id"], identifier))
        if len(keys) == 0:
            raise QueryValidationError
        yield keys


##############
# League API #
##############


# League Entries

validate_league_entries_query = Query. \
    has("platform").as_(Platform).also. \
    has("summoner.id").as_(int)


validate_many_league_entries_query = Query. \
    has("platform").as_(Platform).also. \
    has("summoners.id").as_(Iterable)


def for_league_entries(leagues: Leagues) -> List[Tuple[str, int]]:
    return [(leagues.platform.value, leagues._LeagueEntries__summoner.id)]


def for_league_entries_query(query: Query) -> List[Tuple[str, int]]:
    return [(query["platform"].value, query["summoner.id"])]


def for_many_league_entries_query(query: Query) -> Generator[List[Tuple[str, int]], None, None]:
    for id in query["summoners.id"]:
        try:
            yield [(query["platform"].value, id)]
        except ValueError as e:
            raise QueryValidationError from e

# Leagues

validate_leagues_query = Query. \
    has("platform").as_(Platform).also. \
    has("summoner.id").as_(int)


validate_many_leagues_query = Query. \
    has("platform").as_(Platform).also. \
    has("summoners.id").as_(Iterable)


def for_leagues(leagues: Leagues) -> List[Tuple[str, int]]:
    return [(leagues.platform.value, leagues._Leagues__summoner.id)]


def for_leagues_query(query: Query) -> List[Tuple[str, int]]:
    return [(query["platform"].value, query["summoner.id"])]


def for_many_leagues_query(query: Query) -> Generator[List[Tuple[str, int]], None, None]:
    for id in query["summoners.id"]:
        try:
            yield [(query["platform"].value, id)]
        except ValueError as e:
            raise QueryValidationError from e

# Challenger

validate_challenger_league_query = Query. \
    has("platform").as_(Platform).also. \
    has("queue").as_(Queue)


validate_many_challenger_league_query = Query. \
    has("platform").as_(Platform).also. \
    has("queues").as_(Iterable)


def for_challenger_league(league: ChallengerLeague) -> List[Tuple[str, str]]:
    return [(league.platform.value, league.queue.value)]


def for_challenger_league_query(query: Query) -> List[Tuple[str, str]]:
    return [(query["platform"].value, query["queue"].value)]


def for_many_challenger_league_query(query: Query) -> Generator[List[Tuple[str, str]], None, None]:
    for queue in query["queues"]:
        try:
            yield [(query["platform"].value, queue.value)]
        except ValueError as e:
            raise QueryValidationError from e

# Master

validate_master_league_query = Query. \
    has("platform").as_(Platform).also. \
    has("queue").as_(Queue)


validate_many_master_league_query = Query. \
    has("platform").as_(Platform).also. \
    has("queues").as_(Iterable)


def for_master_league(league: MasterLeague) -> List[Tuple[str, str]]:
    return [(league.platform.value, league.queue.value)]


def for_master_league_query(query: Query) -> List[Tuple[str, str]]:
    return [(query["platform"].value, query["queue"].value)]


def for_many_master_league_query(query: Query) -> Generator[List[Tuple[str, str]], None, None]:
    for queue in query["queues"]:
        try:
            yield [(query["platform"].value, queue.value)]
        except ValueError as e:
            raise QueryValidationError from e


###################
# Static Data API #
###################


# Champion

validate_champion_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("id").as_(int).or_("name").as_(str)


validate_many_champion_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("ids").as_(Iterable).or_("names").as_(Iterable)


def for_champion(champion: Champion) -> List[Tuple]:
    keys = []
    try:
        keys.append((champion.platform.value, champion.version, champion.locale, _hash_included_data(champion.included_data), champion._data[ChampionData].id))
    except KeyError:
        pass
    try:
        keys.append((champion.platform.value, champion.version, champion.locale, _hash_included_data(champion.included_data), champion._data[ChampionData].name))
    except KeyError:
        pass
    return keys


def for_champion_query(query: Query) -> List[Tuple]:
    keys = []
    included_data_hash = _hash_included_data(query["includedData"])
    if "id" in query:
        keys.append((query["platform"].value, query["version"], query["locale"], included_data_hash, query["id"]))
    if "name" in query:
        keys.append((query["platform"].value, query["version"], query["locale"], included_data_hash, query["name"]))
    return keys


def for_many_champion_query(query: Query) -> Generator[Tuple[str, str, str, int, Union[int, str]], None, None]:
    included_data_hash = _hash_included_data(query["includedData"])
    grouped_identifiers = []
    identifier_types = []
    if "ids" in query:
        grouped_identifiers.append(query["ids"])
        identifier_types.append(int)
    if "names" in query:
        grouped_identifiers.append(query["names"])
        identifier_types.append(str)
    for identifiers in zip(*grouped_identifiers):
        keys = []
        for identifier, identifier_type in zip(identifiers, identifier_types):
            try:
                identifier = identifier_type(identifier)
                keys.append((query["platform"].value, query["version"], query["locale"], included_data_hash, identifier))
            except ValueError as e:
                raise QueryValidationError from e
        yield keys


validate_champions_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


validate_many_champions_query = Query. \
    has("platforms").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


def for_champions(champions: Champions) -> List[Tuple[str, str, str, int]]:
    return [(champions.platform.value, champions.version, champions.locale, _hash_included_data(champions.included_data))]


def for_champions_query(query: Query) -> List[Tuple[str, str, str, int]]:
    included_data_hash = _hash_included_data(query["includedData"])
    return [(query["platform"].value, query["version"], query["locale"], included_data_hash)]


def for_many_champions_query(query: Query) -> Generator[List[Tuple[str, str, str, int, Union[int, str]]], None, None]:
    included_data_hash = _hash_included_data(query["includedData"])
    for platform in query["platforms"]:
        try:
            yield [(platform.value, query["version"], query["locale"], included_data_hash)]
        except ValueError as e:
            raise QueryValidationError from e


# Item

validate_item_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("id").as_(int).or_("name").as_(str)


validate_many_item_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("ids").as_(Iterable).or_("names").as_(Iterable)


def for_item(item: Item) -> List[Tuple]:
    keys = []
    try:
        keys.append((item.platform.value, item.version, item.locale, _hash_included_data(item.included_data), item._data[ItemData].id))
    except KeyError:
        pass
    try:
        keys.append((item.platform.value, item.version, item.locale, _hash_included_data(item.included_data), item._data[ItemData].name))
    except KeyError:
        pass
    return keys


def for_item_query(query: Query) -> List[Tuple]:
    keys = []
    included_data_hash = _hash_included_data(query["includedData"])
    if "id" in query:
        keys.append((query["platform"].value, query["version"], query["locale"], included_data_hash, query["id"]))
    if "name" in query:
        keys.append((query["platform"].value, query["version"], query["locale"], included_data_hash, query["name"]))
    return keys


def for_many_item_query(query: Query) -> Generator[Tuple[str, str, str, int, Union[int, str]], None, None]:
    included_data_hash = _hash_included_data(query["includedData"])
    grouped_identifiers = []
    identifier_types = []
    if "ids" in query:
        grouped_identifiers.append(query["ids"])
        identifier_types.append(int)
    if "names" in query:
        grouped_identifiers.append(query["names"])
        identifier_types.append(str)
    for identifiers in zip(*grouped_identifiers):
        keys = []
        for identifier, identifier_type in zip(identifiers, identifier_types):
            try:
                identifier = identifier_type(identifier)
                keys.append((query["platform"].value, query["version"], query["locale"], included_data_hash, identifier))
            except ValueError as e:
                raise QueryValidationError from e
        yield keys


validate_items_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


validate_many_items_query = Query. \
    has("platforms").as_(Iterable).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


def for_items(items: Items) -> List[Tuple[str, str, str, int]]:
    return [(items.platform.value, items.version, items.locale, _hash_included_data(items.included_data))]


def for_items_query(query: Query) -> List[Tuple[str, str, str, int]]:
    included_data_hash = _hash_included_data(query["includedData"])
    return [(query["platform"].value, query["version"], query["locale"], included_data_hash)]


def for_many_items_query(query: Query) -> Generator[List[Tuple[str, str, str, int, Union[int, str]]], None, None]:
    included_data_hash = _hash_included_data(query["includedData"])
    for platform in query["platforms"]:
        try:
            yield [(platform.value, query["version"], query["locale"], included_data_hash)]
        except ValueError as e:
            raise QueryValidationError from e


# Language

validate_languages_query = Query. \
    has("platform").as_(Platform)


validate_many_languages_query = Query. \
    has("platforms").as_(Iterable)


def for_languages(languages: Locales) -> List[str]:
    return [languages.platform.value]


def for_languages_query(query: Query) -> List[str]:
    return [query["platform"].value]


def for_many_languages_query(query: Query) -> Generator[List[str], None, None]:
    for platform in query["platforms"]:
        yield [platform.value]


validate_language_strings_query = Query. \
    has("platform").as_(Platform)


validate_many_language_strings_query = Query. \
    has("platforms").as_(Iterable)


def for_language_strings(languages: LanguageStrings) -> List[str]:
    return [languages.platform.value]


def for_language_strings_query(query: Query) -> List[str]:
    return [query["platform"].value]


def for_many_language_strings_query(query: Query) -> Generator[List[str], None, None]:
    for platform in query["platforms"]:
        yield [platform.value]


# Map

validate_map_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    has("id").as_(int).or_("name").as_(str)


validate_many_map_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    has("ids").as_(Iterable).or_("names").as_(Iterable)


def for_map(map: Map) -> List[Tuple]:
    keys = []
    try:
        keys.append((map.platform.value, map.version, map.locale, map._data[MapData].id))
    except KeyError:
        pass
    try:
        keys.append((map.platform.value, map.version, map.locale, map._data[MapData].name))
    except KeyError:
        pass
    return keys


def for_map_query(query: Query) -> List[Tuple]:
    keys = []
    if "id" in query:
        keys.append((query["platform"].value, query["version"], query["locale"], query["id"]))
    if "name" in query:
        keys.append((query["platform"].value, query["version"], query["locale"], query["name"]))
    return keys


def for_many_map_query(query: Query) -> Generator[Tuple[str, str, str, int, Union[int, str]], None, None]:
    grouped_identifiers = []
    identifier_types = []
    if "ids" in query:
        grouped_identifiers.append(query["ids"])
        identifier_types.append(int)
    if "names" in query:
        grouped_identifiers.append(query["names"])
        identifier_types.append(str)
    for identifiers in zip(*grouped_identifiers):
        keys = []
        for identifier, identifier_type in zip(identifiers, identifier_types):
            try:
                identifier = identifier_type(identifier)
                keys.append((query["platform"].value, query["version"], query["locale"], identifier))
            except ValueError as e:
                raise QueryValidationError from e
        yield keys


validate_maps_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str)


validate_many_maps_query = Query. \
    has("platforms").as_(Iterable).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str)


def for_maps(maps: Maps) -> List[Tuple[str, str, str]]:
    return [(maps.platform.value, maps.version, maps.locale)]


def for_maps_query(query: Query) -> List[Tuple[str, str, str]]:
    return [(query["platform"].value, query["version"], query["locale"])]


def for_many_maps_query(query: Query) -> Generator[List[Tuple[str, str, str]], None, None]:
    for platform in query["platforms"]:
        yield [(platform.value, query["version"], query["locale"])]


# Mastery

validate_mastery_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("id").as_(int).or_("name").as_(str)


validate_many_mastery_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("ids").as_(Iterable).or_("names").as_(Iterable)


def for_mastery(mastery: Mastery) -> List[Tuple]:
    keys = []
    try:
        keys.append((mastery.platform.value, mastery.version, mastery.locale, _hash_included_data(mastery.included_data), mastery._data[MasteryData].id))
    except KeyError:
        pass
    try:
        keys.append((mastery.platform.value, mastery.version, mastery.locale, _hash_included_data(mastery.included_data), mastery._data[MasteryData].name))
    except KeyError:
        pass
    return keys


def for_mastery_query(query: Query) -> List[Tuple]:
    keys = []
    included_data_hash = _hash_included_data(query["includedData"])
    if "id" in query:
        keys.append((query["platform"].value, query["version"], query["locale"], included_data_hash, query["id"]))
    if "name" in query:
        keys.append((query["platform"].value, query["version"], query["locale"], included_data_hash, query["name"]))
    return keys


def for_many_mastery_query(query: Query) -> Generator[Tuple[str, str, str, int, Union[int, str]], None, None]:
    included_data_hash = _hash_included_data(query["includedData"])
    grouped_identifiers = []
    identifier_types = []
    if "ids" in query:
        grouped_identifiers.append(query["ids"])
        identifier_types.append(int)
    if "names" in query:
        grouped_identifiers.append(query["names"])
        identifier_types.append(str)
    for identifiers in zip(*grouped_identifiers):
        keys = []
        for identifier, identifier_type in zip(identifiers, identifier_types):
            try:
                identifier = identifier_type(identifier)
                keys.append((query["platform"].value, query["version"], query["locale"], included_data_hash, identifier))
            except ValueError as e:
                raise QueryValidationError from e
        yield keys


validate_masteries_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


validate_many_masteries_query = Query. \
    has("platforms").as_(Iterable).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


def for_masteries(masteries: Masteries) -> List[Tuple[str, str, str, int]]:
    return [(masteries.platform.value, masteries.version, masteries.locale, _hash_included_data(masteries.included_data))]


def for_masteries_query(query: Query) -> List[Tuple[str, str, str, int]]:
    included_data_hash = _hash_included_data(query["includedData"])
    return [(query["platform"].value, query["version"], query["locale"], included_data_hash)]


def for_many_masteries_query(query: Query) -> Generator[List[Tuple[str, str, str, int, Union[int, str]]], None, None]:
    included_data_hash = _hash_included_data(query["includedData"])
    for platform in query["platforms"]:
        try:
            yield [(platform.value, query["version"], query["locale"], included_data_hash)]
        except ValueError as e:
            raise QueryValidationError from e


# Profile Icon

validate_profile_icons_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str)


validate_many_profile_icons_query = Query. \
    has("platforms").as_(Iterable).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str)


def for_profile_icons(profile_icon: ProfileIcons) -> List[Tuple[str, str, str]]:
    return [(profile_icon["platform"], profile_icon["version"], profile_icon["locale"])]


def for_profile_icons_query(query: Query) -> List[Tuple[str, str, str]]:
    return [(query["platform"].value, query["version"], query["locale"])]


def for_many_profile_icons_query(query: Query) -> Generator[List[Tuple[str, str, str]], None, None]:
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield [(platform.value, query["version"], query["locale"])]
        except ValueError as e:
            raise QueryValidationError from e


validate_profile_icon_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    has("id").as_(int)


validate_many_profile_icon_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    has("ids").as_(Iterable)


def for_profile_icon(profile_icon: ProfileIcon) -> List[Tuple[str, str, str, int]]:
    return [(profile_icon.platform.value, profile_icon.version, profile_icon.locale, profile_icon.id)]


def for_profile_icon_query(query: Query) -> List[Tuple[str, str, str, int]]:
    return [(query["platform"].value, query["version"], query["locale"], query["id"])]


def for_many_profile_icon_query(query: Query) -> Generator[List[Tuple[str, str, str, int]], None, None]:
    for id in query["ids"]:
        try:
            id = int(id)
            yield [(query["platform"].value, query["version"], query["locale"], id)]
        except ValueError as e:
            raise QueryValidationError from e


# Realm

validate_realms_query = Query. \
    has("platform").as_(Platform)


validate_many_realms_query = Query. \
    has("platforms").as_(Iterable)


def for_realms(realm: Realms) -> List[str]:
    return [(realm.platform.value)]


def for_realms_query(query: Query) -> List[str]:
    return [(query["platform"].value)]


def for_many_realms_query(query: Query) -> Generator[List[str], None, None]:
    for platform in query["platforms"]:
        yield [(platform.value)]


# Rune

validate_rune_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("id").as_(int).or_("name").as_(str)


validate_many_rune_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("ids").as_(Iterable).or_("names").as_(Iterable)


def for_rune(rune: Rune) -> List[Tuple]:
    keys = []
    try:
        keys.append((rune.platform.value, rune.version, rune.locale, _hash_included_data(rune.included_data), rune._data[RuneData].id))
    except KeyError:
        pass
    try:
        keys.append((rune.platform.value, rune.version, rune.locale, _hash_included_data(rune.included_data), rune._data[RuneData].name))
    except KeyError:
        pass
    return keys


def for_rune_query(query: Query) -> List[Tuple]:
    keys = []
    included_data_hash = _hash_included_data(query["includedData"])
    if "id" in query:
        keys.append((query["platform"].value, query["version"], query["locale"], included_data_hash, query["id"]))
    if "name" in query:
        keys.append((query["platform"].value, query["version"], query["locale"], included_data_hash, query["name"]))
    return keys


def for_many_rune_query(query: Query) -> Generator[Tuple[str, str, str, int, Union[int, str]], None, None]:
    included_data_hash = _hash_included_data(query["includedData"])
    grouped_identifiers = []
    identifier_types = []
    if "ids" in query:
        grouped_identifiers.append(query["ids"])
        identifier_types.append(int)
    if "names" in query:
        grouped_identifiers.append(query["names"])
        identifier_types.append(str)
    for identifiers in zip(*grouped_identifiers):
        keys = []
        for identifier, identifier_type in zip(identifiers, identifier_types):
            try:
                identifier = identifier_type(identifier)
                keys.append((query["platform"].value, query["version"], query["locale"], included_data_hash, identifier))
            except ValueError as e:
                raise QueryValidationError from e
        yield keys


validate_runes_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


validate_many_runes_query = Query. \
    has("platforms").as_(Iterable).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


def for_runes(runes: Runes) -> List[Tuple[str, str, str, int]]:
    return [(runes.platform.value, runes.version, runes.locale, _hash_included_data(runes.included_data))]


def for_runes_query(query: Query) -> List[Tuple[str, str, str, int]]:
    included_data_hash = _hash_included_data(query["includedData"])
    return [(query["platform"].value, query["version"], query["locale"], included_data_hash)]


def for_many_runes_query(query: Query) -> Generator[List[Tuple[str, str, str, int, Union[int, str]]], None, None]:
    included_data_hash = _hash_included_data(query["includedData"])
    for platform in query["platforms"]:
        try:
            yield [(platform.value, query["version"], query["locale"], included_data_hash)]
        except ValueError as e:
            raise QueryValidationError from e


# Summoner Spell

validate_summoner_spell_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("id").as_(int).or_("name").as_(str)


validate_many_summoner_spell_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"}).also. \
    has("ids").as_(Iterable).or_("names").as_(Iterable)


def for_summoner_spell(summoner_spell: SummonerSpell) -> List[Tuple]:
    keys = []
    try:
        keys.append((summoner_spell.platform.value, summoner_spell.version, summoner_spell.locale, _hash_included_data(summoner_spell.included_data), summoner_spell._data[SummonerSpellData].id))
    except KeyError:
        pass
    try:
        keys.append((summoner_spell.platform.value, summoner_spell.version, summoner_spell.locale, _hash_included_data(summoner_spell.included_data), summoner_spell._data[SummonerSpellData].name))
    except KeyError:
        pass
    return keys


def for_summoner_spell_query(query: Query) -> List[Tuple]:
    keys = []
    included_data_hash = _hash_included_data(query["includedData"])
    if "id" in query:
        keys.append((query["platform"].value, query["version"], query["locale"], included_data_hash, query["id"]))
    if "name" in query:
        keys.append((query["platform"].value, query["version"], query["locale"], included_data_hash, query["name"]))
    return keys


def for_many_summoner_spell_query(query: Query) -> Generator[Tuple[str, str, str, int, Union[int, str]], None, None]:
    included_data_hash = _hash_included_data(query["includedData"])
    grouped_identifiers = []
    identifier_types = []
    if "ids" in query:
        grouped_identifiers.append(query["ids"])
        identifier_types.append(int)
    if "names" in query:
        grouped_identifiers.append(query["names"])
        identifier_types.append(str)
    for identifiers in zip(*grouped_identifiers):
        keys = []
        for identifier, identifier_type in zip(identifiers, identifier_types):
            try:
                identifier = identifier_type(identifier)
                keys.append((query["platform"].value, query["version"], query["locale"], included_data_hash, identifier))
            except ValueError as e:
                raise QueryValidationError from e
        yield keys


validate_summoner_spells_query = Query. \
    has("platform").as_(Platform).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


validate_many_summoner_spells_query = Query. \
    has("platforms").as_(Iterable).also. \
    can_have("version").with_default(_get_default_version, supplies_type=str).also. \
    can_have("locale").with_default(_get_default_locale, supplies_type=str).also. \
    can_have("includedData").with_default({"all"})


def for_summoner_spells(summoner_spells: SummonerSpells) -> List[Tuple[str, str, str, int]]:
    return [(summoner_spells.platform.value, summoner_spells.version, summoner_spells.locale, _hash_included_data(summoner_spells.included_data))]


def for_summoner_spells_query(query: Query) -> List[Tuple[str, str, str, int]]:
    included_data_hash = _hash_included_data(query["includedData"])
    return [(query["platform"].value, query["version"], query["locale"], included_data_hash)]


def for_many_summoner_spells_query(query: Query) -> Generator[List[Tuple[str, str, str, int, Union[int, str]]], None, None]:
    included_data_hash = _hash_included_data(query["includedData"])
    for platform in query["platforms"]:
        try:
            yield [(platform.value, query["version"], query["locale"], included_data_hash)]
        except ValueError as e:
            raise QueryValidationError from e


# Version

validate_versions_query = Query. \
    has("platform").as_(Platform)


validate_many_versions_query = Query. \
    has("platforms").as_(Iterable)


def for_versions(versions: Versions) -> List[str]:
    return [versions.platform.value]


def for_versions_query(query: Query) -> List[str]:
    return [query["platform"].value]


def for_many_versions_query(query: Query) -> Generator[List[str], None, None]:
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield [platform.value]
        except ValueError as e:
            raise QueryValidationError from e


##############
# Status API #
##############

validate_shard_status_query = Query. \
    has("platform").as_(Platform)


validate_many_shard_status_query = Query. \
    has("platforms").as_(Iterable)


def for_shard_status(shard_status: ShardStatus) -> List[str]:
    return [shard_status.platform.value]


def for_shard_status_query(query: Query) -> List[str]:
    return [query["platform"].value]


def for_many_shard_status_query(query: Query) -> Generator[List[str], None, None]:
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield [platform.value]
        except ValueError as e:
            raise QueryValidationError from e


#################
# Masteries API #
#################


validate_mastery_page_query = Query. \
    has("platform").as_(Platform).also. \
    has("summoner.id").as_(int).or_("summoner.account.id").as_(int).or_("summoner.name").as_(str).also. \
    has("id").as_(int)


validate_many_mastery_page_query = Query. \
    has("platform").as_(Platform).also. \
    has("summoner.id").as_(int).or_("summoner.account.id").as_(int).or_("summoner.name").as_(str).also. \
    has("ids").as_(Iterable)


def for_mastery_page(mastery_page: MasteryPage) -> List[Tuple]:
    keys = []
    try:
        keys.append((mastery_page.platform.value, mastery_page.summoner[SummonerData].id, mastery_page.id))
    except KeyError:
        pass
    try:
        keys.append((mastery_page.platform.value, mastery_page.summoner[SummonerData].name, mastery_page.id))
    except KeyError:
        pass
    try:
        keys.append((mastery_page.platform.value, mastery_page.summoner[SummonerData].account_id, mastery_page.id))
    except KeyError:
        pass
    return keys


def for_mastery_page_query(query: Query) -> List[Tuple]:
    keys = []
    if "summoner.id" in query:
        keys.append((query["platform"].value, query["summoner.id"], query["id"]))
    if "summoner.account.id" in query:
        keys.append((query["platform"].value, query["summoner.account.id"], query["id"]))
    if "summoner.name" in query:
        keys.append((query["platform"].value, query["summoner.name"], query["id"]))
    return keys


def for_many_mastery_page_query(query: Query) -> Generator[Tuple[str, Union[int, str], int], None, None]:
    for id_ in query["ids"]:
        id_ = int(id_)
        keys = []
        if "summoner.id" in query:
            keys.append((query["platform"].value, query["summoner.id"], id_))
        if "summoner.account.id" in query:
            keys.append((query["platform"].value, query["summoner.account.id"], id_))
        if "summoner.name" in query:
            keys.append((query["platform"].value, query["summoner.name"], id_))
        if len(keys) == 0:
            raise QueryValidationError
        yield keys


#############
# Match API #
#############


validate_match_query = Query. \
    has("platform").as_(Platform).also. \
    has("id").as_(int)


validate_many_match_query = Query. \
    has("platform").as_(Platform).also. \
    has("ids").as_(Iterable)


def for_match(match: Match) -> List[Tuple[str, int]]:
    return [(match.platform.value, match.id)]


def for_match_query(query: Query) -> List[Tuple[str, int]]:
    return [(query["platform"].value, query["id"])]


def for_many_match_query(query: Query) -> Generator[List[Tuple[str, int]], None, None]:
    for id in query["ids"]:
        try:
            id = int(id)
            yield [(query["platform"].value, id)]
        except ValueError as e:
            raise QueryValidationError from e

validate_match_timeline_query = Query. \
    has("platform").as_(Platform).also. \
    has("id").as_(int)


validate_many_match_timeline_query = Query. \
    has("platform").as_(Platform).also. \
    has("ids").as_(Iterable)


def for_match_timeline(timeline: Timeline) -> List[Tuple[str, int]]:
    return [(timeline.platform.value, timeline.id)]


def for_match_timeline_query(query: Query) -> List[Tuple[str, int]]:
    return [(query["platform"].value, query["id"])]


def for_many_match_timeline_query(query: Query) -> Generator[List[Tuple[str, int]], None, None]:
    for id in query["ids"]:
        try:
            id = int(id)
            yield [(query["platform"].value, id)]
        except ValueError as e:
            raise QueryValidationError from e


#############
# Runes API #
#############


validate_rune_page_query = Query. \
    has("platform").as_(Platform).also. \
    has("summoner.id").as_(int).or_("summoner.account.id").as_(int).or_("summoner.name").as_(str).also. \
    has("id").as_(int)


validate_many_rune_page_query = Query. \
    has("platform").as_(Platform).also. \
    has("summoner.id").as_(int).or_("summoner.account.id").as_(int).or_("summoner.name").as_(str).also. \
    has("ids").as_(Iterable)


def for_rune_page(rune_page: RunePage) -> List[Tuple]:
    keys = []
    try:
        keys.append((rune_page.platform.value, rune_page.summoner[SummonerData].id, rune_page.id))
    except KeyError:
        pass
    try:
        keys.append((rune_page.platform.value, rune_page.summoner[SummonerData].name, rune_page.id))
    except KeyError:
        pass
    try:
        keys.append((rune_page.platform.value, rune_page.summoner[SummonerData].account_id, rune_page.id))
    except KeyError:
        pass
    return keys


def for_rune_page_query(query: Query) -> List[Tuple]:
    keys = []
    if "summoner.id" in query:
        keys.append((query["platform"].value, query["summoner.id"], query["id"]))
    if "summoner.account.id" in query:
        keys.append((query["platform"].value, query["summoner.account.id"], query["id"]))
    if "summoner.name" in query:
        keys.append((query["platform"].value, query["summoner.name"], query["id"]))
    return keys


def for_many_rune_page_query(query: Query) -> Generator[Tuple[str, Union[int, str], int], None, None]:
    for id_ in query["ids"]:
        id_ = int(id_)
        keys = []
        if "summoner.id" in query:
            keys.append((query["platform"].value, query["summoner.id"], id_))
        if "summoner.account.id" in query:
            keys.append((query["platform"].value, query["summoner.account.id"], id_))
        if "summoner.name" in query:
            keys.append((query["platform"].value, query["summoner.name"], id_))
        if len(keys) == 0:
            raise QueryValidationError
        yield keys


#################
# Spectator API #
#################

validate_current_match_query = Query. \
    has("platform").as_(Platform).also. \
    has("summoner.id").as_(int)


validate_many_current_match_query = Query. \
    has("platform").as_(Platform).also. \
    has("summoner.ids").as_(Iterable)


def for_current_match(current_match_info: CurrentMatch) -> List[Tuple[str, int]]:
    return [(current_match_info.platform, current_match_info._CurrentMatch__summoner.id)]


def for_current_match_query(query: Query) -> List[Tuple[str, int]]:
    return [(query["platform"].value, query["summoner.id"])]


def for_many_current_match_query(query: Query) -> Generator[List[Tuple[str, int]], None, None]:
    for summoner_id in query["summoner.ids"]:
        try:
            summoner_id = int(summoner_id)
            yield [(query["platform"].value, summoner_id)]
        except ValueError as e:
            raise QueryValidationError from e


validate_featured_matches_query = Query. \
    has("platform").as_(Platform)


validate_many_featured_matches_query = Query. \
    has("platforms").as_(Iterable)


def for_featured_matches(featured_matches: FeaturedMatches) -> List[str]:
    return [featured_matches.platform]


def for_featured_matches_query(query: Query) -> List[str]:
    return [query["platform"].value]


def for_many_featured_matches_query(query: Query) -> Generator[List[str], None, None]:
    for platform in query["platforms"]:
        try:
            platform = Platform(platform)
            yield [platform.value]
        except ValueError as e:
            raise QueryValidationError from e


################
# Summoner API #
################


validate_summoner_query = Query. \
    has("platform").as_(Platform).also. \
    has("id").as_(int).or_("account.id").as_(int).or_("name").as_(str)


validate_many_summoner_query = Query. \
    has("platform").as_(Platform).also. \
    has("ids").as_(Iterable).or_("accounts.id").as_(Iterable).or_("names").as_(Iterable)


def for_summoner(summoner: Summoner) -> List[Tuple]:
    keys = []
    try:
        keys.append((summoner.platform.value, summoner._data[SummonerData].id))
    except KeyError:
        pass
    try:
        keys.append((summoner.platform.value, summoner._data[SummonerData].name))
    except KeyError:
        pass
    try:
        keys.append((summoner.platform.value, summoner._data[SummonerData].account_id))
    except KeyError:
        pass
    return keys


def for_summoner_query(query: Query) -> List[Tuple]:
    keys = []
    if "id" in query:
        keys.append((query["platform"].value, query["id"]))
    if "name" in query:
        keys.append((query["platform"].value, query["name"]))
    if "account.id" in query:
        keys.append((query["platform"].value, query["account.id"]))
    return keys


def for_many_summoner_query(query: Query) -> Generator[List[Tuple], None, None]:
    grouped_identifiers = []
    identifier_types = []
    if "ids" in query:
        grouped_identifiers.append(query["ids"])
        identifier_types.append(int)
    elif "accounts.id" in query:
        grouped_identifiers.append(query["accounts.id"])
        identifier_types.append(int)
    elif "names" in query:
        grouped_identifiers.append(query["names"])
        identifier_types.append(str)
    for identifiers in zip(*grouped_identifiers):
        keys = []
        for identifier, identifier_type in zip(identifiers, identifier_types):
            try:
                identifier = identifier_type(identifier)
                keys.append((query["platform"].value, identifier))
            except ValueError as e:
                raise QueryValidationError from e
        yield keys
