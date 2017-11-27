__author__ = 'pvde'

from os.path import join
import lxml.etree, logging
from copy import deepcopy

def resolve(schema_tree, this_dir):
    catalog_file = join(this_dir, 'catalog.xml')
    schema_tree = deepcopy(schema_tree)
    try:
        uri_map = {}
        catalog = lxml.etree.parse(catalog_file)
        for node in catalog.getroot():
            if node.tag == '{urn:oasis:names:tc:entity:xmlns:xml:catalog}uri':
                name = node.get('name')
                uri = 'file:///'+join(this_dir, node.get('uri'))
                uri_map[name] = uri
        import_elements = schema_tree.xpath(
            'xs:import', namespaces = {'xs':'http://www.w3.org/2001/XMLSchema'}
        )
        for import_element in import_elements:
            schema_location = import_element.get('schemaLocation')
            if schema_location != None:
                if schema_location in uri_map:
                    import_element.set('schemaLocation', uri_map[schema_location])
    except:
        raise
    else:
        return schema_tree



