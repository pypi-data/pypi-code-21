for ertype in ('Activity', 'associated_with', 'generated', 'used'):
    sync_schema_props_perms(ertype)

add_relation_definition('Activity', 'generated', 'SEDAArchiveTransfer')
add_relation_definition('Activity', 'used', 'SEDAArchiveTransfer')
