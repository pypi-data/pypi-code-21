""" Add countries_mapping vocabulary
"""
import logging
from Products.ATVocabularyManager.utils.vocabs import createSimpleVocabs
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger(__name__)


def install_countries_map_vocabulary(context):
    """ See IVocabularyFactory interface
    """
    atvm = getToolByName(context, "portal_vocabularies")

    countries_id = "countries_mapping"
    countries = {countries_id: (
        ("Czechia", "Czech Republic"),
        ("Macedonia (ARYM)", "Former Yugoslav Republic of Macedonia, the"),
        ("Macedonia (FYR)", "Former Yugoslav Republic of Macedonia, the"),
        ("Macedonia (FYROM)", "Former Yugoslav Republic of Macedonia, the"),
        ("Macedonia", "Former Yugoslav Republic of Macedonia, the"),
        ("Kosova (Kosovo)", "Kosovo (UNSCR 1244/99)"),
        ("Kosovo", "Kosovo (UNSCR 1244/99)")
    )}
    if atvm.get(countries_id):
        atvm.manage_delObjects('countries_mapping')
    if not atvm.get(countries_id):
        createSimpleVocabs(atvm, countries)
        atvm[countries_id].setTitle("EEA Custom Country Name Mappings")
        logger.info("Added EEA Custom Country Name Mappings vocabulary")
    else:
        logger.info("Already added EEA Custom Country Name Mappings vocabulary")
