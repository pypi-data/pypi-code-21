from os.path import join, dirname


process_script(join(dirname(__file__), 'import_dcat_vocabularies.py'))

drop_attribute('Dataset', 'theme')
drop_attribute('Agent', 'dcat_type')
add_relation_definition('Agent', 'publisher_type', 'Concept')
drop_attribute('Dataset', 'frequency')
add_relation_definition('Dataset', 'dataset_frequency', 'Concept')

drop_attribute('DataCatalog', 'license')
drop_attribute('Distribution', 'licence')
add_entity_type('LicenseDocument')
