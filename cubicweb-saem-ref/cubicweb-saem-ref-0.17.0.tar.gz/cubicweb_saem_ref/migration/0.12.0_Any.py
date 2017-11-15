from functools import partial
from cubicweb_saem_ref import workflows

sql = partial(sql, ask_confirm=False)

for etype, cols in (('ProfileDocument', ('file_type_code',
                                         'document_type_code',
                                         'character_set_code')),
                    ('SEDAFileTypeCode', ('file_type_code_value',))):
    for col in cols:
        sql('ALTER TABLE cw_{0} DROP COLUMN IF EXISTS cw_{1}'.format(etype, col))

db_indices = dict((idx, table) for idx, table, idx_def in sql(
    'SELECT indexname, tablename, indexdef FROM pg_indexes')
                  if not idx.startswith('pg_'))
for index in db_indices:
    if index.startswith('cw_') and '_pkey' not in index and '_cwuri_' not in index:
        if '_key' in index:
            sql('ALTER TABLE %s DROP CONSTRAINT %s' % (db_indices[index], index))
        else:
            sql('DROP INDEX %s' % index)


rename_entity_type('Agent', 'AuthorityRecord')
drop_relation_definition('AuthorityRecord', 'phone_number', 'PhoneNumber')
rename_entity_type('Authority', 'Organization')
add_entity_type('OrganizationUnit')
ou_wf = workflows.define_publication_workflow(add_workflow, 'OrganizationUnit')
add_entity_type('Agent')
agent_wf = workflows.define_publication_workflow(add_workflow, 'Agent')

# AuthorityRecord.ark_naa
add_relation_definition('AuthorityRecord', 'ark_naa', 'ArkNameAssigningAuthority')
rql('SET X ark_naa NAA WHERE X authority A, A ark_naa NAA')
commit()

# Cleanup database against things forbidden since a few releases that may make
# the migration fail if the migrated database isn't clean:
# * remove deposit role if agent has not archival_agent
rql('DELETE X archival_role R WHERE R name "deposit", NOT X archival_agent Y')
# * remove contact point if contact agent is not of the 'person' kind
rql('DELETE X contact_point Y WHERE NOT (Y agent_kind K, K name "person")')
# * remove contact point if agent is not of the 'authority' kind
rql('DELETE X contact_point Y WHERE NOT (X agent_kind K, K name "authority")')
# * remove agent user if agent is not of the 'person' kind
rql('DELETE X agent_user Y WHERE NOT (X agent_kind K, K name "person")')
# * remove archival agent if one of the end of the relation is not of the 'authority' kind
rql('DELETE X archival_agent Y WHERE NOT (X agent_kind K, K name "authority")')
rql('DELETE X archival_agent Y WHERE NOT (X agent_kind K, K name "authority")')
# * remove related schemes if the agent is not of the 'authority' kind
rql('DELETE X related_concept_scheme Y WHERE NOT (X agent_kind K, K name "authority")')
# * remove used profils if the agent is not of the 'authority' kind
rql('DELETE Y seda_transferring_agent X WHERE NOT (X agent_kind K, K name "authority")')

commit()

create_entity = partial(create_entity, ask_confirm=False)

def ou_for(authority_record_eid, name, state, authority, _cache={}):
    try:
        return _cache[authority_record_eid]
    except:
        ou = create_entity('OrganizationUnit', name=name,
                           in_state=ou_wf.state_by_name(state),
                           authority=authority,
                           authority_record=authority_record_eid)
        rql('SET A archival_role R WHERE A eid %(a)s, AR archival_role R, AR eid %(ar)s',
            {'a': ou.eid, 'ar': authority_record_eid})
        _cache[authority_record_eid] = ou
        return ou

def agent_for(authority_record_eid, name, state, authority, _cache={}):
    try:
        return _cache[authority_record_eid]
    except:
        agent = create_entity('Agent', name=name,
                              in_state=agent_wf.state_by_name(state),
                              authority=authority,
                              authority_record=authority_record_eid)
        _cache[authority_record_eid] = agent
        return agent


# Agent.agent_user
for x, name, state, authority, user in rql(
        'Any X,XN,XSN,XA, U WHERE X is AuthorityRecord, '
        'X name XN, X in_state XS, XS name XSN, X authority XA, '
        'X agent_user U'):
    agent = agent_for(x, name, state, authority)
    agent.cw_set(agent_user=user)

# OrganizationUnit.contact_point
for x, xname, xstate, xauthority, y, yname, ystate, yauthority in rql(
        'Any X,XN,XSN,XA, Y,YN,YSN,YA WHERE X is AuthorityRecord, '
        'X name XN, X in_state XS, XS name XSN, X authority XA, '
        'Y name YN, Y in_state YS, YS name YSN, Y authority YA, '
        'X contact_point Y'):
    ou = ou_for(x, xname, xstate, xauthority)
    ou.cw_set(contact_point=agent_for(y, yname, ystate, yauthority))

# Authority.archival_agent
for xauthority, y, yname, ystate, yauthority in rql(
        'DISTINCT Any XA, Y,YN,YSN,YA WHERE X is AuthorityRecord, '
        'X name XN, X authority XA, '
        'Y name YN, Y in_state YS, YS name YSN, Y authority YA, '
        'X archival_agent Y'):
    authority = cnx.entity_from_eid(xauthority)
    archival_ou = ou_for(y, yname, ystate, yauthority)
    if authority.archival_unit:
        if authority.archival_unit[0].eid != archival_ou.eid:
            print((u'authority {} has inconsistent archival unit {} and {}'.format(
                authority.name, authority.archival_unit[0].name, archival_ou.name
            )).encode('ascii', errors='replace'))
    else:
        authority.cw_set(archival_unit=archival_ou)


# OrganizationUnit.related_concept_scheme
for x, name, state, authority, scheme in rql(
        'Any X,XN,XSN,XA, CS WHERE X is AuthorityRecord, '
        'X name XN, X in_state XS, XS name XSN, X authority XA, '
        'X related_concept_scheme CS'):
    ou = ou_for(x, name, state, authority)
    ou.cw_set(related_concept_scheme=scheme)

# SEDAProfile.seda_transferring_agent
for x, name, state, authority, profile in rql(
        'Any X,XN,XSN,XA, P WHERE X is AuthorityRecord, '
        'X name XN, X in_state XS, XS name XSN, X authority XA, '
        'P seda_transferring_agent X'):
    ou = ou_for(x, name, state, authority)
    ou.cw_set(reverse_seda_transferring_agent=profile)

commit()

drop_relation_definition('SEDAProfile', 'seda_transferring_agent', 'AuthorityRecord')
drop_relation_definition('AuthorityRecord', 'agent_user', 'CWUser')
drop_relation_definition('AuthorityRecord', 'related_concept_scheme', 'ConceptScheme')
drop_relation_definition('AuthorityRecord', 'authority', 'Organization')
drop_relation_definition('AuthorityRecord', 'archival_role', 'ArchivalRole')
for rtype in ('contact_point', 'archival_agent'):
    drop_relation_definition('AuthorityRecord', rtype, 'AuthorityRecord')
