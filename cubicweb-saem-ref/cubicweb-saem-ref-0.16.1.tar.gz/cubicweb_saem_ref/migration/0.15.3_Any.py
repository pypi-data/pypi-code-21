for etype in ('ChronologicalRelation', 'HierarchicalRelation',
              'AssociationRelation', 'ConceptScheme',
              'use_profile', 'related_concept_scheme'):
    sync_schema_props_perms(etype)
