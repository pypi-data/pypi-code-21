# quick and dirty deduplicate of agent with duplicated name within an authority
for agent in rql('DISTINCT Any X WHERE X is Agent, X name XN, X authority A, '
                 'Y is Agent, Y name XN, Y authority A, '
                 'Y eid YE, X eid >YE').entities():
    agent.cw_delete()
commit()

for ertype in ('generated', 'used', 'associated_with', 'place_address', 'new_version_of',
               'agent_kind', 'authority_record', 'use_profile',
               'OrganizationUnit', 'Agent', 'ArkNameAssigningAuthority'):
    sync_schema_props_perms(ertype)


sql("DELETE FROM container_relation WHERE EXISTS("
    "SELECT FROM entities WHERE eid_to=eid AND "
    "type IN ('AuthorityRecord', 'ConceptScheme', 'Concept'))")
commit()
