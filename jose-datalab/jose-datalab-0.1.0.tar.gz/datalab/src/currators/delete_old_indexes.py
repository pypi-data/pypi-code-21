
import curator
import elasticsearch

ONE_WEEK_INDEXES_PREFIX = ['.monitoring-es-6-', '.watcher-history-6' ]
ONE_MONTH_INDEXES_PREFIX = []
ONE_YEAR_INDEXES_PREFIX = []

client = elasticsearch.Elasticsearch("134.171.189.10:9200")

for my_prefix in ONE_WEEK_INDEXES_PREFIX:

    ilo = curator.IndexList(client)

    ilo.filter_by_regex(kind='prefix', value=my_prefix)

    ilo.filter_by_age(source='creation_date', direction='older', unit='days', unit_count=7)

    try :
        curator.DeleteIndices(ilo=ilo, master_timeout=60*60*12).do_action()
    except curator.NoIndices:
        pass



for my_prefix in ONE_MONTH_INDEXES_PREFIX:

    ilo = curator.IndexList(client)

    ilo.filter_by_regex(kind='prefix', value=my_prefix)

    ilo.filter_by_age(source='creation_date', direction='older', unit='months', unit_count=1)

    try:
        curator.DeleteIndices(ilo=ilo, master_timeout=60 * 60 * 12).do_action()
    except curator.NoIndices:
        pass

for my_prefix in ONE_YEAR_INDEXES_PREFIX:

    ilo = curator.IndexList(client)

    ilo.filter_by_regex(kind='prefix', value=my_prefix)

    ilo.filter_by_age(source='creation_date', direction='older', unit='years', unit_count=1)

    try:
        curator.DeleteIndices(ilo=ilo, master_timeout=60 * 60 * 12).do_action()
    except curator.NoIndices:
        pass






