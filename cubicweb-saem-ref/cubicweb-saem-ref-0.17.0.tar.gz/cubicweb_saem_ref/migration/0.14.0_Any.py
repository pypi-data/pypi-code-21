add_relation_definition('Activity', 'associated_with', 'CWUser')
rql('SET A associated_with U WHERE A associated_with AG, AG agent_user U')
commit()
drop_relation_definition('Activity', 'associated_with', 'Agent')

sync_schema_props_perms(('CWUser', 'authority', 'Organization'))

add_relation_definition(
    'OrganizationUnit', 'use_authorityrecord', 'AuthorityRecord')

# Set default "use_authorityrecord" relation to existing AuthorityRecord
with cnx.deny_all_hooks_but():
    rql('SET OU use_authorityrecord X WHERE OU archival_role AR, AR name "archival"')
    commit(ask_confirm=False)

add_attribute('Organization', 'ark')

drop_cube('pyramid')

schema_wf = get_workflow_for('ConceptScheme')
with cnx.deny_all_hooks_but():
    rql('SET X in_state S WHERE X is ConceptScheme, S eid %(s)s, NOT X in_state Y',
        {'s': schema_wf.state_by_name('published').eid})
commit()


try:
    sql('CREATE UNIQUE INDEX words_unique_idx ON words (etype, word)')
    sql('CREATE INDEX words_word_idx ON words USING gin(word gin_trgm_ops)')
    commit(ask_confirm=False)
except Exception:
    rollback()
