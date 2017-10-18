from es_wrapper.general.datatypes import extract_value, class_name, func_name, merge_dicts
from es_wrapper.configuration.parameters import ES_MAX_QUERY_SIZE, BAND_24GHz


def create_index_template(template_prefix, mapping):
    """
    Create an index template with mapping
    :param string template_prefix:
    :param dictionary mapping:
    :return dictionary template_dict:
    """
    template_dict = {"template": template_prefix,
                     "mappings": mapping
                     }
    return template_dict


def parse_es_insert_response(es_response):
    """
    This method parses the returned response after inserting data to ES
    :param dict es_response:
    :return bool: returned status
    """
    created_status = extract_value(es_response, "created")
    if created_status:
        return True
    else:
        return False


class ESInterval:
    """
    Creates a correct interval for ES histogram
    """
    SECONDS = "s"
    MINUTES = "m"
    HOURS = "h"
    DAYS = "d"
    MONTHS = "m"
    YEARS = "y"

    def __init__(self, count, scale):
        self.count = count
        self.scale = scale

    def get(self):
        return str(self.count) + self.scale


class ESOrder:

    COUNT = "_count"
    DESCENDING = "desc"
    ASCENDING = "asc"

    def __init__(self, measure=COUNT, order_type=DESCENDING):
        """
        :param measure: Field or aggregation to sort by
        :param order_type: How to order, descending, ascending
        :return:
        """
        self.measure = measure
        self.order_type = order_type

    def get_order(self, measure=None, order_type=None):
        """
        :param measure: Field or aggregation to sort by
        :param order_type:
        :return:
        """
        if measure:
            self.measure = measure
        if order_type:
            self.order_type = order_type
        return {self.measure: self.order_type}


class ESQuery:

    SUM = "sum"
    AVERAGE = "avg"
    TERMS = "terms"
    CARDINALITY = "cardinality"
    MAX = "max"
    MIN = "min"
    EXTENDED_STATS = "extended_stats"
    STATS = "stats"
    HISTOGRAM = "date_histogram"
    TOP_HITS = "top_hits"

    DEFAULT_ORDER = ESOrder(ESOrder.COUNT, ESOrder.DESCENDING).get_order()
    DEFAULT_AGG_SIZE = ES_MAX_QUERY_SIZE

    # Types of queries
    FIELD_UPDATE = 0
    SEARCH = 1

    def __init__(self, query_type=SEARCH, size=ES_MAX_QUERY_SIZE):
        """
        :param int size: Size for the query we return
        """
        self.size = size
        self.must_list = []
        self.should_list = []
        self.must_not_list = []
        self.aggs_dict = {}
        self.update_dict = {}
        self.filter_query = ""
        self.query_type = query_type

    def must_match_single_value(self, field, value):
        """
        Add a single match query to the list
        :param str field: The name of the field in ES
        :param value:
        """
        self.must_list.append(self._match_single_value(field, value))

    def must_match_multiple_values(self, field, value_list):
        """
        Add a single match query to the list
        :param str field:
        :param list value_list:
        """
        self.must_list.append(self._match_multiple_values(field, value_list))

    def must_match_range(self, field, gte=None, lte=None, gt=None, lt=None):
        """
        Match A timestamp value
        :param str field: The name of the field in ES
        :param gte: Min timestamp
        :param lte: Max timestamp
        :param gt: Greater than time
        :param gt: Less than time
        """
        self.must_list.append(self._match_range(field, gte, lte, gt, lt))

    def must_match_timestamp(self, field, gte=None, lte=None, gt=None, lt=None):
        """
        Match A timestamp value
        :param str field: The name of the field in ES
        :param str gte: Min timestamp
        :param str lte: Max timestamp
        :param gt: Greater than time
        :param gt: Less than time
        """
        self.must_match_range(field, gte, lte, gt, lt)

    def should_match_single_value(self, field, value):
        """
        Add a single match query to the list
        :param str field:
        :param value:
        """
        self.should_list.append(self._match_single_value(field, value))

    def should_match_multiple_values(self, field, value_list):
        """
        Add a single match query to the list
        :param str field: The name of the field in ES
        :param list value_list:
        """
        self.should_list.append(self._match_multiple_values(field, value_list))

    def should_match_range(self, field, gte=None, lte=None):
        """
        Match A timestamp value
        :param str field: The name of the field in ES
        :param gte: Min timestamp
        :param lte: Max timestamp
        """
        self.should_list.append(self._match_range(field, gte, lte))

    def should_match_timestamp(self, field, gte=None, lte=None):
        """
        Match A timestamp value
        :param field:
        :param gte: Min timestamp
        :param lte: Max timestamp
        """
        self.should_match_range(field, gte, lte)

    def must_not_match_single_value(self, field, value):
        """
        Add a single match query to the list
        :param str field: The name of the field in ES
        :param value:
        """
        self.must_not_list.append(self._match_single_value(field, value))

    def must_not_match_multiple_values(self, field, value_list):
        """
        Add a single match query to the list
        :param str field:
        :param list value_list:
        """
        self.must_not_list.append(self._match_multiple_values(field, value_list))

    def must_not_match_range(self, field, gte=None, lte=None):
        """
        Match A timestamp value
        :param str field: The name of the field in ES
        :param gte: Min timestamp
        :param lte: Max timestamp
        """
        self.must_not_list.append(self._match_range(field, gte, lte))

    def must_not_match_timestamp(self, field, gte=None, lte=None):
        """
        Match A timestamp value
        :param str field: The name of the field in ES
        :param str gte: Min timestamp
        :param str lte: Max timestamp
        :return dict:
        """
        self.must_not_match_range(field, gte, lte)

    def add_filter_query(self, filter_query):
        """
        Adding a filter query string to the query
        :param str filter_query:
        """
        self.filter_query = filter_query

    def add_histogram(self, hist_name, field, interval):
        """
        Adds an aggregation to the internal dictionary
        :param str hist_name:
        :param str field:
        :param str interval:
        """

        self.aggs_dict.update({hist_name: self._create_aggregation_field_dict(field,
                                                                              agg_type=self.HISTOGRAM,
                                                                              interval=interval)})

    def add_aggregation(self,
                        agg_name,
                        field,
                        agg_type,
                        order=DEFAULT_ORDER,
                        size=DEFAULT_AGG_SIZE):
        """
        Adds an aggregation to the internal dictionary
        :param str agg_name:
        :param str field:
        :param str agg_type:
        :param dict order:
        :param int size: The number of terms to bring in an aggregations
        """

        self.aggs_dict.update({agg_name: self._create_aggregation_field_dict(field, agg_type, order, size)})

    def add_sub_aggregation(self,
                            top_agg_name,
                            sub_agg_name,
                            field, agg_type,
                            order=DEFAULT_ORDER,
                            size=DEFAULT_AGG_SIZE):
        """
        Adds an aggregation to the internal dictionary
        :param top_agg_name: Name of the father aggregation
        :param str sub_agg_name: Name of the current aggregation
        :param str field: The name of the field in ES
        :param str agg_type: One of the types of the aggregation, must be of ESAdapter constant
        :param dict order:
        :param int size: The number of terms to bring in an aggregations
        """
        # If top_agg_name wasn't received as a list, convert it to such
        if type(top_agg_name) != list:
            top_agg_names = [top_agg_name]
        else:
            top_agg_names = top_agg_name

        # Create a key list of the arguments
        doc = self._create_aggregation_field_dict(field, agg_type, order, size)
        # Add the new doc's mapping to the original dictionary
        self.aggs_dict = merge_dicts(self.aggs_dict,
                                     self._build_nested_mapping_dictionary([top_agg_names], sub_agg_name, doc))

    @staticmethod
    def _build_nested_mapping_dictionary(key_list, doc_name, doc):
        """
        key_list = [["key1", "nested_key1"], ["key2]]
        :param list key_list:
        :param str doc_name:
        :param dict doc:
        :return dict:
        """
        index_dict = {}
        for path in key_list:
            current_level = index_dict
            for part in path:
                if part not in current_level:
                    current_level[part] = {"aggs": {}}
                current_level = current_level[part]["aggs"]
            current_level.update({doc_name: doc})
        return index_dict

    @staticmethod
    def _create_aggregation_field_dict(field,
                                       agg_type,
                                       order=DEFAULT_ORDER,
                                       size=DEFAULT_AGG_SIZE,
                                       interval=None):
        """
        Adds an aggregation dictionary to the main aggs_dict
        :param str field: The name of the field in ES
        :param str agg_type: One of the types of the aggregation, must be of ESAdapter constant
        :param dict order:
        :param int size: The number of terms to bring in an aggregations
        :return dict:
        """

        if agg_type == ESQuery.SUM or\
           agg_type == ESQuery.AVERAGE or\
           agg_type == ESQuery.MAX or\
           agg_type == ESQuery.MIN or\
           agg_type == ESQuery.STATS:
            return {agg_type: {"field": field}}

        elif agg_type == ESQuery.CARDINALITY:
            return {agg_type: {"field": field, "precision_threshold": 100}}

        elif agg_type == ESQuery.TOP_HITS:

            if not size:
                size = 1

            source = {"include": field}
            sort = {"@timestamp": {"order": "desc"}}

            return {ESQuery.TOP_HITS: {"size": size,
                                       "_source": source,
                                       "sort": [sort]
                                       }}

        # show extended statistics,
        # std_deviation_bounds provides an interval of plus/minus 1 standard deviations from the mean
        elif agg_type == ESQuery.EXTENDED_STATS:
            return {ESQuery.EXTENDED_STATS: {"field": field, "sigma": 1}}

        elif agg_type == ESQuery.TERMS:
            return {ESQuery.TERMS: {"field": field,
                                    "size": size,
                                    "order": order
                                    }
                    }
        elif agg_type == ESQuery.HISTOGRAM:
            return {ESQuery.HISTOGRAM: {"field": field,
                                        "interval": interval,
                                        }
                    }
        else:
            raise TypeError("%s received wrong aggregation type %s" % (class_name(ESQuery), agg_type))

    @staticmethod
    def _match_range(field, gte=None, lte=None, gt=None, lt=None):
        """
        Match A timestamp value
        :param str field: The name of the field in ES:
        :param str gte: Min timestamp
        :param str lte: Max timestamp
        :return dict query:
        """
        query = {"range": {field: {}}}
        if gte:
            query["range"][field]["gte"] = gte
        if lte:
            query["range"][field]["lte"] = lte
        if gt:
            query["range"][field]["gt"] = gt
        if lt:
            query["range"][field]["lt"] = lt
        return query

    @staticmethod
    def _match_single_value(field, value):
        """
        Match list for a single value
        :param str field: The name of the field in ES
        :param value:
        :return dict:
        """
        return {"query": {"match": {field: value}}}

    @staticmethod
    def _match_multiple_values(field, value_list):
        """
        Match list for a single value
        :param str field: The name of the field in ES
        :param list value_list:
        :return dict:
        """
        # Make sure input is a list
        if type(value_list) != list:
            raise TypeError("%s in %s didn't received a list: %s" % (func_name(), class_name(ESQuery), value_list))

        return {"terms": {field: value_list}}

    def _get_search_query(self, agg_size=ES_MAX_QUERY_SIZE, include_size=True):
        """
        This method returns a valid ES query
        :param bool include_size: Whether or not to include size field in the search
        :param int agg_size: If set to
        :return dict: Full query for elasticsearch
        """
        query = {}

        if self.must_list or self.must_not_list or self.should_list or self.filter_query:
            query = {"query": {"bool": {}}
                     }

            if self.must_list:
                query["query"]["bool"]["must"] = self.must_list
            if self.must_not_list:
                query["query"]["bool"]["must_not"] = self.must_not_list
            if self.should_list:
                query["query"]["bool"]["should"] = self.should_list

            # if self.filter_query:
            #     query["query"].update({"query": {"query_string": {"query": self.filter_query,
            #                                                                   "analyze_wildcard": True
            #                                                                   }
            #                                                  }
            #                                        })
        if self.aggs_dict:
            query["aggs"] = self.aggs_dict
            # We set the aggregation size to 0 because we don't want to get the attached documents
            # in the response
            agg_size = 0

        if include_size:
            query["size"] = agg_size

        return query

    def update_object_field(self, field_name, value):
        """
        Creating a query to update a single or several fields in ES by a specific field name
        such as: "generalInfo.apId" OR "interfaces.profileInfo.profileName"

        :param str field_name: The full name of the objects field
        :param value: The full name of the objects field
        """
        self.update_dict = self._update_query_dict(self.update_dict, field_name, value)

    @staticmethod
    def _update_query_dict(dict_to_update, field_name, value):
        """
        Adds values to the field update dictionary
        :param dict_to_update:
        :param field_name:
        :param value:
        :return dict:
        """

        query = {"doc": {}}
        path = ESQuery._split_fields_list_and_protect_band_constant(field_name)
        current_level = query["doc"]
        for part in path:
            if part not in current_level:
                # Set the value at the last part of the list
                if path[-1] == part:
                    current_level[part] = value
                else:
                    current_level[part] = {}
            current_level = current_level[part]

        return merge_dicts(dict_to_update, query)

    @staticmethod
    def _split_fields_list_and_protect_band_constant(field_name):
        """
        This method is a patch to keep "2.4Ghz" together and not split
        :param str field_name:
        :return list field_list:
        """
        field_list = field_name.split(".")

        # Check if "2.4Ghz" was split into two values
        if set(BAND_24GHz.split(".")).issubset(set(field_list)):
            i = field_list.index("4ghz")
            field_list[i] = BAND_24GHz
            field_list.pop(field_list.index("2"))
        return field_list

    def _get_field_update_query(self):
        """
        Returns the update query dict
        :return dict:
        """
        return self.update_dict

    def get_query(self, *args, **kwargs):
        """
        Returns the query by its type
        :param args:
        :param kwargs:
        :return dict:
        """
        if self.query_type == self.SEARCH:
            return self._get_search_query(*args, **kwargs)
        elif self.query_type == self.FIELD_UPDATE:
            return self._get_field_update_query()
