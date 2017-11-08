""" Migrate country names
"""
import logging
import json
import transaction
from zope.component import queryMultiAdapter
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from eea.geotags.rdf.country_groups import COUNTRY_GROUPS
try:
    from Products.EEAPloneAdmin.browser.migration_helper_data import (
        countryDicts,
    )
except ImportError:
    def countryDicts():
        """ EEAPloneAdmin not installed """
        return {}

logger = logging.getLogger(__name__)


def create_obj_uri(obj):
    """ """
    obj_url = obj.absolute_url(1)
    portalUrl = 'http://www.eea.europa.eu'
    if obj_url.find('www/SITE/') != -1:
        pub_url = portalUrl + obj_url[8:]
    else:
        pub_url = portalUrl + obj_url[3:]
    return pub_url


def set_location_field(obj, new_geotags, ping_cr_view):
    """ """
    loc_field = obj.getField('location')
    loc_field.set(obj, json.dumps(new_geotags))
    obj.reindexObject(idxs=['geotags', 'location'])
    ping_cr_view(create_obj_uri(obj))


def check_countries_from_grp(grp, features, country_groups_data):
    """ """
    missing_countries = {}
    for country in country_groups_data[grp]:
        for feature in features:
            title = feature['properties']['title']
            if country == title:
                try:
                    del missing_countries[country]
                except KeyError:
                    pass
                break
            missing_countries[country] = True
    return missing_countries


def migrate_country_names(context, content_type=None):
    """ migrate wrong country names and remove country groups
    """
    if not content_type:
        return 'Nothing to be done!'
    logger.info("Start fixing the country names!")
    request = getattr(context, 'REQUEST', None)
    ping_cr_view = queryMultiAdapter((context, request), name="ping_cr")
    pcat = getToolByName(context, "portal_catalog")
    query = {
        'portal_type': content_type,
        'Language': 'all',
    }
    brains = pcat(query)

    # create country names vocab
    country_name = {
        'Czechia': 'Czech Republic',
        'Macedonia (ARYM)': 'Former Yugoslav Republic of Macedonia, the',
        'Macedonia (FYR)': 'Former Yugoslav Republic of Macedonia, the',
        'Macedonia (FYROM)': 'Former Yugoslav Republic of Macedonia, the',
        'Macedonia': 'Former Yugoslav Republic of Macedonia, the',
        'Kosova (Kosovo)': 'Kosovo (UNSCR 1244/99)',
        'Kosovo': 'Kosovo (UNSCR 1244/99)'
    }

    # create the country groups
    country_groups = COUNTRY_GROUPS
    country_groups_vocab = ['EEA32', 'EEA33', 'EFTA4', 'EU15',
        'EU25', 'EU27', 'EU28', 'Pan-Europe']
    country_groups_data = {}
    for gr in country_groups.keys():
        if gr[0] == 'PANE':
            country_groups_data['Pan-Europe'] = country_groups[gr]
            continue
        if gr[0] in country_groups_vocab:
            country_groups_data[gr[0]] = country_groups[gr]

    total_brains_number = len(brains)
    logger.info("Start checking %s objects." % total_brains_number)
    obj_with_groups = {}
    obj_with_bad_country_name = {}
    obj_with_bad_russia = {}
    count_countries_detected = 0
    count_groups_detected = 0
    update_detected = False
    count_progress = 0

    for brain in brains:
        count_progress += 1
        update_detected = False
        obj = brain.getObject()
        obj_uri = obj.absolute_url()

        anno = getattr(obj, '__annotations__', {})
        geotags = anno.get('eea.geotags.tags')
        if not geotags:
            continue
        features = geotags.get('features')

        # detect country name containing "Russian Federation"
        for feature in features:
            title = feature['properties']['title']
            description = feature['properties']['description']
            if ('Russia' in title) or ('Russia' in description):
                update_detected = True
                obj_with_bad_russia[obj_uri] = True
            if 'Russian Federation' in title:
                title = title.replace('Russian Federation', 'Russia')
                feature['properties']['title'] = title
                update_detected = True
                obj_with_bad_russia[obj_uri] = True
            if 'Russian Federation' in description:
                description = description.replace('Russian Federation', 'Russia')
                feature['properties']['description'] = description
                update_detected = True
                obj_with_bad_russia[obj_uri] = True

        # detect country name to be replaced
        for country in country_name.keys():
            for feature in features:
                title = feature['properties']['title']
                description = feature['properties']['description']
                if country in title:
                    if country == "Macedonia" and 'Macedonia (ARYM)' in title:
                        continue
                    if country == "Macedonia" and 'Macedonia (FYR)' in title:
                        continue
                    if country == "Macedonia" and 'Macedonia (FYROM)' in title:
                        continue
                    if country == "Macedonia" and 'Former Yugoslav Republic of Macedonia, the' in title:
                        continue
                    if country == "Macedonia" and "Greece" in description:
                        continue
                    if country == "Kosovo" and 'Kosovo (UNSCR 1244/99)' in title:
                        continue
                    if country == "Kosovo" and 'Kosova (Kosovo)' in title:
                        continue
                    title = title.replace(country, country_name[country])
                    feature['properties']['title'] = title
                    update_detected = True
                    count_countries_detected += 1
                    obj_with_bad_country_name[obj_uri] = True
            for feature in features:
                description = feature['properties']['description']
                if country in description:
                    if country == "Macedonia" and 'Macedonia (ARYM)' in description:
                        continue
                    if country == "Macedonia" and 'Macedonia (FYR)' in description:
                        continue
                    if country == "Macedonia" and 'Macedonia (FYROM)' in description:
                        continue
                    if country == "Macedonia" and 'Former Yugoslav Republic of Macedonia, the' in description:
                        continue
                    if country == "Macedonia" and "Greece" in description:
                        continue
                    if country == "Kosovo" and 'Kosovo (UNSCR 1244/99)' in description:
                        continue
                    if country == "Kosovo" and 'Kosova (Kosovo)' in description:
                        continue
                    description = description.replace(country, country_name[country])
                    feature['properties']['description'] = description
                    update_detected = True
                    count_countries_detected += 1
                    obj_with_bad_country_name[obj_uri] = True

        # detect country group assigned
        features_to_remove = []
        features_to_be_added = []
        for grp in country_groups_data.keys():
            for feature in features:
                title = feature['properties']['title']
                if grp in title:
                    update_detected = True
                    count_groups_detected += 1
                    obj_with_groups[obj_uri] = True
                    # check if all countries from the group are in features
                    missing_countries = check_countries_from_grp(grp, features, country_groups_data)
                    # add missing countries data
                    for country in missing_countries:
                        features_to_be_added.append(countryDicts()[country])
                    # mark country group to be removed
                    features_to_remove.append(feature)
        for feature in features_to_remove:
            features.remove(feature)
        for feature in features_to_be_added:
            features.append(feature)

        # update object, reindex catalog and ping SDS
        if update_detected:
            geo_data = {}
            geo_data['features'] = features
            geo_data['type'] = geotags['type']
            set_location_field(obj, geo_data, ping_cr_view)
            logger.info("Updated: %s" % obj_uri)

        # display progress
        if not (count_progress % 10):
            transaction.commit()
            logger.info("#################### Progress: %s/%s objects checked." % (count_progress, total_brains_number))

    logger.info("#################### Found 'Russian Federation' in %s objects:" % len(obj_with_bad_russia.keys()))
    for k in obj_with_bad_russia.keys():
        logger.info(k)
    logger.info("#################### Found %s bad country names in %s objects:" % (count_countries_detected, len(obj_with_bad_country_name.keys())))
    for k in obj_with_bad_country_name.keys():
        logger.info(k)
    logger.info("#################### Found %s groups in %s objects:" % (count_groups_detected, len(obj_with_groups.keys())))
    for k in obj_with_groups.keys():
        logger.info(k)
    logger.info("Done fixing the country names!")


class MigrateCountryNames(BrowserView):
    """ Migrate country names and remove groups
    """
    def __call__(self, **kwargs):
        content_type = self.request.get('ctype', None)
        if content_type:
            migrate_country_names(self.context, content_type)
            return "Done!"
        else:
            return 'Please add "ctype" parameter!'

