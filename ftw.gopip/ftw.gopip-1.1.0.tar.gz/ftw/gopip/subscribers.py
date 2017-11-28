from plone import api


def root_page_order_changed(portal, event):
    catalog = api.portal.get_tool('portal_catalog')
    for brain in catalog.unrestrictedSearchResults({
            'path': {'query': '/'.join(portal.getPhysicalPath()),
                     'depth': 1}}):
        try:
            obj = brain.getObject()
        except KeyError:
            continue
        else:
            catalog.reindexObject(obj,
                                  idxs=['getObjPositionInParent'],
                                  update_metadata=False)
