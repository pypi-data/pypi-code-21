""" Migrate sparqls with the new arguments format (name:type query)
"""

import logging
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger("eea.sparql.upgrades")

def migrate_sparqls(context):
    """ Migrate sparqls with the new arguments format (name:type query)
    """

    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults(portal_type='Sparql')

    logger.info('Migrating %s Sparqls ...', len(brains))
    nbr_updated = 0

    for brain in brains:
        obj = brain.getObject()
        field = obj.getField('arg_spec')
        argspec = field.getAccessor(obj)()

        if argspec and not isinstance(argspec, tuple):
            nbr_updated += 1
            args = argspec.split()
            new_args = ()
            for arg in args:
                arg_map = {}
                arg_map['name'] = arg
                arg_map['query'] = ''
                new_args = new_args + (arg_map, )
            field.getMutator(obj)(new_args)

    logger.info('Migrated %s Sparqls ...', nbr_updated)
    return "Sparql Migration Done"
