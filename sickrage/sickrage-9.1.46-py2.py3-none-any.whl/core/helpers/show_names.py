# Author: echel0n <echel0n@sickrage.ca>
# URL: https://sickrage.ca
#
# This file is part of SickRage.
#
# SickRage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SickRage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickRage.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import fnmatch
import os
import re
from datetime import date
from functools import partial

import sickrage
from sickrage.core.common import DOWNLOADED, Quality, SNATCHED, WANTED, \
    countryList
from sickrage.core.helpers import sanitizeSceneName
from sickrage.core.nameparser import InvalidNameException, InvalidShowException, \
    NameParser
from sickrage.core.scene_exceptions import get_scene_exceptions

resultFilters = [
    "sub(bed|ed|pack|s)",
    "(dir|sub|nfo)fix",
    "(?<!shomin.)sample",
    "(dvd)?extras",
    "dub(bed)?"
]

if hasattr('General', 'ignored_subs_list') and sickrage.srCore.srConfig.IGNORED_SUBS_LIST:
    resultFilters.append("(" + sickrage.srCore.srConfig.IGNORED_SUBS_LIST.replace(",", "|") + ")sub(bed|ed|s)?")


def containsAtLeastOneWord(name, words):
    """
    Filters out results based on filter_words

    name: name to check
    words : string of words separated by a ',' or list of words

    Returns: False if the name doesn't contain any word of words list, or the found word from the list.
    :return:
    :param name:
    :param words:
    :return:
    :rtype: unicode
    """
    if isinstance(words, basestring):
        words = words.split(',')
    items = [(re.compile('(^|[\W_])%s($|[\W_])' % re.escape(word.strip()), re.I), word.strip()) for word in words]
    for regexp, word in items:
        if regexp.search(name):
            return word
    return False


def filterBadReleases(name, parse=True):
    """
    Filters out non-english and just all-around stupid releases by comparing them
    to the resultFilters contents.

    name: the release name to check

    Returns: True if the release name is OK, False if it's bad.
    :return:
    :param name:
    :param parse:
    :return:
    """

    try:
        if parse:
            NameParser().parse(name)
    except InvalidNameException:
        sickrage.srCore.srLogger.debug("Unable to parse the filename " + name + " into a valid episode")
        return False
    except InvalidShowException:
        pass
    # LOGGER.debug(u"Unable to parse the filename " + name + " into a valid show")
    #    return False

    # if any of the bad strings are in the name then say no
    ignore_words = list(resultFilters)
    if sickrage.srCore.srConfig.IGNORE_WORDS:
        ignore_words.extend(sickrage.srCore.srConfig.IGNORE_WORDS.split(','))
    word = containsAtLeastOneWord(name, ignore_words)
    if word:
        sickrage.srCore.srLogger.debug("Invalid scene release: " + name + " contains " + word + ", ignoring it")
        return False

    # if any of the good strings aren't in the name then say no
    if sickrage.srCore.srConfig.REQUIRE_WORDS:
        require_words = sickrage.srCore.srConfig.REQUIRE_WORDS
        if not containsAtLeastOneWord(name, require_words):
            sickrage.srCore.srLogger.debug(
                "Invalid scene release: " + name + " doesn't contain any of " + sickrage.srCore.srConfig.REQUIRE_WORDS +
                ", ignoring it")
            return False

    return True


def sceneToNormalShowNames(name):
    """
        Takes a show name from a scene dirname and converts it to a more "human-readable" format.

    name: The show name to convert

    Returns: a list of all the possible "normal" names
    :return:
    :param name:
    """

    if not name:
        return []

    name_list = [name]

    # use both and and &
    new_name = re.sub('(?i)([\. ])and([\. ])', '\\1&\\2', name, re.I)
    if new_name not in name_list:
        name_list.append(new_name)

    results = []

    for cur_name in name_list:
        # add brackets around the year
        results.append(re.sub('(\D)(\d{4})$', '\\1(\\2)', cur_name))

        # add brackets around the country
        country_match_str = '|'.join(countryList.values())
        results.append(re.sub('(?i)([. _-])(' + country_match_str + ')$', '\\1(\\2)', cur_name))

    results += name_list

    return list(set(results))


def makeSceneShowSearchStrings(show, season=-1, anime=False):
    """

    :rtype: list[unicode]
    """
    showNames = allPossibleShowNames(show, season=season)

    # scenify the names
    if anime:
        sanitizeSceneNameAnime = partial(sanitizeSceneName, anime=True)
        return map(sanitizeSceneNameAnime, showNames)
    else:
        return map(sanitizeSceneName, showNames)


def makeSceneSeasonSearchString(show, ep_obj, extraSearchType=None):
    numseasons = 0

    if show.air_by_date or show.sports:
        # the search string for air by date shows is just
        seasonStrings = [str(ep_obj.airdate).split('-')[0]]
    elif show.is_anime:
        seasonEps = show.getAllEpisodes(ep_obj.season)

        # get show qualities
        anyQualities, bestQualities = Quality.splitQuality(show.quality)

        # compile a list of all the episode numbers we need in this 'season'
        seasonStrings = []
        for episode in seasonEps:

            # get quality of the episode
            curCompositeStatus = episode.status
            curStatus, curQuality = Quality.splitCompositeStatus(curCompositeStatus)

            if bestQualities:
                highestBestQuality = max(bestQualities)
            else:
                highestBestQuality = 0

            # if we need a better one then add it to the list of episodes to fetch
            if (curStatus in (
                    DOWNLOADED,
                    SNATCHED) and curQuality < highestBestQuality) or curStatus == WANTED:
                ab_number = episode.scene_absolute_number
                if ab_number > 0:
                    seasonStrings.append("%02d" % ab_number)

    else:
        numseasons = len({x['doc']['season'] for x in
                          sickrage.srCore.mainDB.db.get_many('tv_episodes', show.indexerid, with_doc=True)
                          if x['doc']['season'] != 0})

        seasonStrings = ["S%02d" % int(ep_obj.scene_season)]

    showNames = set(makeSceneShowSearchStrings(show, ep_obj.scene_season))

    toReturn = []

    # search each show name
    for curShow in showNames:
        # most providers all work the same way
        if not extraSearchType:
            # if there's only one season then we can just use the show name straight up
            if numseasons == 1:
                toReturn.append(curShow)
            # for providers that don't allow multiple searches in one request we only search for Sxx style stuff
            else:
                for cur_season in seasonStrings:
                    if ep_obj.show.is_anime:
                        if ep_obj.show.release_groups is not None:
                            if len(show.release_groups.whitelist) > 0:
                                for keyword in show.release_groups.whitelist:
                                    toReturn.append(keyword + '.' + curShow + "." + cur_season)
                    else:
                        toReturn.append(curShow + "." + cur_season)

    return toReturn


def makeSceneSearchString(show, ep_obj):
    toReturn = []

    numseasons = len(
        {x['doc']['season'] for x in sickrage.srCore.mainDB.db.get_many('tv_episodes', show.indexerid, with_doc=True)
         if x['doc']['season'] != 0})

    # see if we should use dates instead of episodes
    if (show.air_by_date or show.sports) and ep_obj.airdate != date.fromordinal(1):
        epStrings = [str(ep_obj.airdate)]
    elif show.is_anime:
        epStrings = [
            "%02i" % int(ep_obj.scene_absolute_number if ep_obj.scene_absolute_number > 0 else ep_obj.scene_episode)]
    else:
        epStrings = ["S%02iE%02i" % (int(ep_obj.scene_season), int(ep_obj.scene_episode)),
                     "%ix%02i" % (int(ep_obj.scene_season), int(ep_obj.scene_episode))]

    # for single-season shows just search for the show name -- if total ep count (exclude s0) is less than 11
    # due to the amount of qualities and releases, it is easy to go over the 50 result limit on rss feeds otherwise
    if numseasons == 1 and not ep_obj.show.is_anime:
        epStrings = []

    for curShow in set(makeSceneShowSearchStrings(show, ep_obj.scene_season)):
        for curEpString in epStrings:
            if ep_obj.show.is_anime:
                if ep_obj.show.release_groups is not None:
                    if len(ep_obj.show.release_groups.whitelist) > 0:
                        for keyword in ep_obj.show.release_groups.whitelist:
                            toReturn.append(keyword + '.' + curShow + '.' + curEpString)
                    elif len(ep_obj.show.release_groups.blacklist) == 0:
                        # If we have neither whitelist or blacklist we just append what we have
                        toReturn.append(curShow + '.' + curEpString)
            else:
                toReturn += [curShow + '.' + curEpString]
        else:
            toReturn += [curShow]

    return toReturn


def isGoodResult(name, show, log=True, season=-1):
    """
    Use an automatically-created regex to make sure the result actually is the show it claims to be
    """

    all_show_names = allPossibleShowNames(show, season=season)
    showNames = map(sanitizeSceneName, all_show_names) + all_show_names

    for curName in set(showNames):
        if not show.is_anime:
            escaped_name = re.sub('\\\\[\\s.-]', '\W+', re.escape(curName))
            if show.startyear:
                escaped_name += "(?:\W+" + str(show.startyear) + ")?"
            curRegex = '^' + escaped_name + '\W+(?:(?:S\d[\dE._ -])|(?:\d\d?x)|(?:\d{4}\W\d\d\W\d\d)|(?:(?:part|pt)[\._ -]?(\d|[ivx]))|Season\W+\d+\W+|E\d+\W+|(?:\d{1,3}.+\d{1,}[a-zA-Z]{2}\W+[a-zA-Z]{3,}\W+\d{4}.+))'
        else:
            escaped_name = re.sub('\\\\[\\s.-]', '[\W_]+', re.escape(curName))
            # FIXME: find a "automatically-created" regex for anime releases # test at http://regexr.com?2uon3
            curRegex = '^((\[.*?\])|(\d+[\.-]))*[ _\.]*' + escaped_name + '(([ ._-]+\d+)|([ ._-]+s\d{2})).*'

        if log:
            sickrage.srCore.srLogger.debug("Checking if show " + name + " matches " + curRegex)

        match = re.search(curRegex, name, re.I)
        if match:
            sickrage.srCore.srLogger.debug("Matched " + curRegex + " to " + name)
            return True

    if log:
        sickrage.srCore.srLogger.info(
            "Provider gave result " + name + " but that doesn't seem like a valid result for " + show.name + " so I'm ignoring it")
    return False


def allPossibleShowNames(show, season=-1):
    """
    Figures out every possible variation of the name for a particular show. Includes TVDB name, TVRage name,
    country codes on the end, eg. "Show Name (AU)", and any scene exception names.

    show: a TVShow object that we should get the names of

    Returns: a list of all the possible show names
    :rtype: list[unicode]
    """

    showNames = get_scene_exceptions(show.indexerid, season=season)[:]
    if not showNames:  # if we dont have any season specific exceptions fallback to generic exceptions
        season = -1
        showNames = get_scene_exceptions(show.indexerid, season=season)[:]

    if season in [-1, 1]:
        showNames.append(show.name)

    if not show.is_anime:
        newShowNames = []
        country_list = countryList
        country_list.update(dict(zip(countryList.values(), countryList.keys())))
        for curName in set(showNames):
            if not curName:
                continue

            # if we have "Show Name Australia" or "Show Name (Australia)" this will add "Show Name (AU)" for
            # any countries defined in common.countryList
            # (and vice versa)
            for curCountry in country_list:
                if curName.endswith(' ' + curCountry):
                    newShowNames.append(curName.replace(' ' + curCountry, ' (' + country_list[curCountry] + ')'))
                elif curName.endswith(' (' + curCountry + ')'):
                    newShowNames.append(curName.replace(' (' + curCountry + ')', ' (' + country_list[curCountry] + ')'))

                    # # if we have "Show Name (2013)" this will strip the (2013) show year from the show name
                    # newShowNames.append(re.sub('\(\d{4}\)', '', curName))

        showNames += newShowNames

    return showNames


def determineReleaseName(dir_name=None, nzb_name=None):
    """Determine a release name from an nzb and/or folder name
    :param dir_name:
    :param nzb_name:
    :return:
    """

    if nzb_name is not None:
        sickrage.srCore.srLogger.info("Using nzb_name for release name.")
        return nzb_name.rpartition('.')[0]

    if dir_name is None:
        return None

    # try to get the release name from nzb/nfo
    file_types = ["*.nzb", "*.nfo"]

    for search in file_types:

        reg_expr = re.compile(fnmatch.translate(search), re.IGNORECASE)
        files = [file_name for file_name in os.listdir(dir_name) if
                 os.path.isfile(os.path.join(dir_name, file_name))]
        results = filter(reg_expr.search, files)

        if len(results) == 1:
            found_file = os.path.basename(results[0])
            found_file = found_file.rpartition('.')[0]
            if filterBadReleases(found_file):
                sickrage.srCore.srLogger.info("Release name (" + found_file + ") found from file (" + results[0] + ")")
                return found_file.rpartition('.')[0]

    # If that fails, we try the folder
    folder = os.path.basename(dir_name)
    if filterBadReleases(folder):
        # NOTE: Multiple failed downloads will change the folder name.
        # (e.g., appending #s)
        # Should we handle that?
        sickrage.srCore.srLogger.debug("Folder name (" + folder + ") appears to be a valid release name. Using it.")
        return folder

    return None


def searchDBForShow(regShowName, log=False):
    """
    Searches if show names are present in the DB

    :param regShowName: list of show names to look for
    :param log: Boolean, log debug results of search (defaults to False)
    :return: Indexer ID of found show
    """

    showNames = [re.sub('[. -]', ' ', regShowName)]

    yearRegex = r"([^()]+?)\s*(\()?(\d{4})(?(2)\))$"

    for showName in showNames:
        dbData = [x['doc'] for x in sickrage.srCore.mainDB.db.all('tv_shows', with_doc=True) if
                  x['doc']['show_name'] == showName]
        if len(dbData) == 1:
            return int(dbData[0]["indexer_id"])
        else:
            # if we didn't get exactly one result then try again with the year stripped off if possible
            match = re.match(yearRegex, showName)
            if match and match.group(1):
                if log:
                    sickrage.srCore.srLogger.debug(
                        "Unable to match original name but trying to manually strip and specify show year")

                dbData = [x['doc'] for x in sickrage.srCore.mainDB.db.all('tv_shows', with_doc=True)
                          if match.group(1) in x['doc']['show_name']
                          and x['doc']['startyear'] == match.group(3)]

            if len(dbData) == 0:
                if log:
                    sickrage.srCore.srLogger.debug("Unable to match a record in the DB for " + showName)
                continue
            elif len(dbData) > 1:
                if log:
                    sickrage.srCore.srLogger.debug(
                        "Multiple results for " + showName + " in the DB, unable to match show name")
                continue
            else:
                return int(dbData[0]["indexer_id"])
