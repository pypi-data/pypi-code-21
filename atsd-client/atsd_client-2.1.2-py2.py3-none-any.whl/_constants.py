#------------------------------------------------------------------------------INNER
display_series_threshold = 20
display_series_part = 10

#------------------------------------------------------------------------------URLS
#---------------------------------------------Data
series_insert_url            = 'v1/series/insert'
series_query_url             = 'v1/series/query'
properties_insert_url        = 'v1/properties/insert'
properties_query_url         = 'v1/properties/query'
properties_types_url         = 'v1/properties/{entity}/types'
properties_delete_url        = 'v1/properties/delete'
alerts_query_url             = 'v1/alerts/query'
alerts_update_url            = 'v1/alerts/update'
alerts_history_url           = 'v1/alerts/history/query'
alerts_delete_url            = 'v1/alerts/delete'
messages_insert_url          = 'v1/messages/insert'
messages_query_url           = 'v1/messages/query'
messages_statistics_url      = 'v1/messages/stats/query'
#---------------------------------------------Meta
metric_get_url               = 'v1/metrics/{metric}'
metric_list_url              = 'v1/metrics'
metric_update_url            = 'v1/metrics/{metric}'
metric_create_or_replace_url = 'v1/metrics/{metric}'
metric_delete_url            = 'v1/metrics/{metric}'
metric_series_url            = 'v1/metrics/{metric}/series'
ent_get_url                  = "v1/entities/{entity}"
ent_list_url                 = "v1/entities"
ent_update_url               = "v1/entities/{entity}"
ent_create_or_replace_url    = "v1/entities/{entity}"
ent_delete_url               = "v1/entities/{entity}"
ent_metrics_url               = "v1/entities/{entity}/metrics"
eg_get_url                   = "v1/entity-groups/{group}"
eg_list_url                  = "v1/entity-groups"
eg_update_url                = "v1/entity-groups/{group}"
eg_delete_url                = "v1/entity-groups/{group}"
eg_create_or_replace_url     = "v1/entity-groups/{group}"
eg_get_entities_url          = "v1/entity-groups/{group}/entities"
eg_add_entities_url          = "v1/entity-groups/{group}/entities/add"
eg_set_entities_url          = "v1/entity-groups/{group}/entities/set"
eg_delete_entities_url       = "v1/entity-groups/{group}/entities/delete"
sql_query_url                = "sql"
sql_cancel_url               = "sql/cancel"
commands_url                 = "v1/command"