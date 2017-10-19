add_attribute('Label', 'kind')
add_relation_definition('Label', 'label_of', 'Concept')
for kind, rtype in [('preferred', 'pref_label_of'),
                    ('alternative', 'alt_label_of'),
                    ('hidden', 'hidden_label_of')]:
    sql("UPDATE cw_Label SET cw_kind='%s', cw_label_of=cw_%s WHERE NOT cw_%s IS NULL"
        % (kind, rtype, rtype))
    sql("UPDATE cw_Label SET cw_%s=NULL" % rtype)
    commit()
    drop_relation_type(rtype)
sync_schema_props_perms('Label')  # drop unique together constraint

# renaming of computed relation type is broken, drop then add
drop_relation_type('pref_label')
add_relation_type('preferred_label')
drop_relation_type('alt_label')
add_relation_type('alternative_label')
sync_schema_props_perms('hidden_label')
