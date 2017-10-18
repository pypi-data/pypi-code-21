
from datetime import date, timedelta
from logging import getLogger
from pprint import pprint

from elasticsearch import Elasticsearch, TransportError, ConnectionError, helpers
import jsonpickle
import json
import time

from es_wrapper.general.datatypes import extract_value, multi_getattr, class_name, func_name
from es_wrapper.general.formats import current_utc_time, extract_day_from_timestamp_string
from es_wrapper.general.log import LoggerInfo
from es_wrapper.configuration.parameters import ES_TIMEOUT_TRIALS

from es_wrapper.configuration.queries import query_get_multiple_documents_from_list, delete_multiple_documents_from_list, \
    query_params_from_object





def retry_updates_to_es(func_to_decorate):
    """
    @decorator
    This decorator implements send retries to ES
    :param func_to_decorate:
    """
    def retry(*original_args, **original_kwargs):
        try_count = 0
        exc_str = ""
        # Try count
        while try_count < ES_TIMEOUT_TRIALS:
            try:
                return func_to_decorate(*original_args, **original_kwargs)
            except ConnectionError as exc:
                raise ESAdapterException(exc)
            except TransportError as exc:
                try_count += 1
                exc_str = exc
                time.sleep(0.5)
        raise ESAdapterException("Couldn't update ES object: %s" % exc_str)
    return retry


def es_get_wrapper(es_get_func):
    """
    @decorator
    This decorator implements ES exception handling
    :param es_get_func:
    """
    def wrapper(*original_args, **original_kwargs):
        try:
            return es_get_func(*original_args, **original_kwargs)
        except ConnectionError as exc:
            raise ESAdapterException(exc)
        except TransportError as exc:
            print(exc)
            # pass
    return wrapper


def es_save_wrapper(es_save_func):
    """
    @decorator
    This decorator implements ES exception handling
    :param es_save_func:
    """
    def wrapper(*original_args, **original_kwargs):
        try:
            return es_save_func(*original_args, **original_kwargs)
        except ConnectionError as exc:
            raise ESAdapterException(exc)
        except TransportError as exc:
            raise ESAdapterException(exc)
    return wrapper


class ESAdapterException(Exception):
    """
    This class implement config errors and timeouts
    """
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(ESAdapterException, self).__init__(message)


class ESAdapter:
    """
    This class is the ES base class, allowing objects to be fetched and saved in ES
    """
    PORT = 80

    def __init__(self, es_url):
        self.es_url = es_url
        self.logger = getLogger(LoggerInfo.name)

        # Elastic search instance
        try:
            self.es = Elasticsearch([self.es_url],
                                    port=self.PORT)
        except ConnectionError as exc:
            self.logger.error("Connection error while connection to ES %s" % self.es_url)
            raise ESAdapterException(exc)

        # Used for object updates
        self.obj_index_name = ""
        self.obj_doc_type_name = ""
        # Used for index mapping creation
        self._mapping = {}

    @staticmethod
    def _to_JSON(obj):
        """
        The method return a serialized AP object
        :param Object obj: Object to serialize
        :return string: JSON
        """
        return jsonpickle.encode(obj)

    @staticmethod
    def _from_JSON(json_obj):
        """
        The method return a serialized AP object
        :param JSON json_obj: Object to deserialize
        :return:
        """
        return jsonpickle.decode(json_obj)

    def _ES_JSON_to_object(self, es_doc):
        # TODO - implement a JSON verification method to make sure only valid documents are deserialized

        # Get the source of the document containing the data
        try:
            json_obj = json.dumps(es_doc["_source"])
        except KeyError as exc:
            raise ESAdapterException(exc)

        # Convert the JSON to an object
        try:
            return self._from_JSON(json_obj)
        except (ValueError, TypeError) as exc:
            raise ESAdapterException("Couldn't parse message JSON because %s" % exc)

    def create_object_list_from_es_query(self, es_response, *obj_types):
        """
        Create an object list from an ES query
        :param dictionary es_response: The response from Elasticsearch
        :param obj_types: Type of object we create
        :return list queried_obj_list: A list of objects
        """
        queried_obj_list = []
        # Create an object list out of the Document
        for doc in es_response["hits"]["hits"]:
            obj = self._ES_JSON_to_object(doc)
            # Make sure we get the type of object we want back from ES
            for obj_type in obj_types:
                if isinstance(obj, obj_type):
                    queried_obj_list.append(obj)
                    break
        return queried_obj_list

    @es_get_wrapper
    def get_objects_by_query(self, es_query, index_name, obj_type):
        """
        This method is used to fetch multiple APs by a specific query to ES.
        The method returns a list of AP objects

        :param dictionary es_query: A dictionary describing the query we do
        :param str index_name: The name of the index
        :param Object obj_type: The type of the object
        :return list AccessPointModel(): A list of AP objects
        """

        # Run the requested query
        es_response = self.es.search(index=index_name,
                                     body=es_query)
        return self.create_object_list_from_es_query(es_response, obj_type)

    def update_obj_value_in_es(self, doc_id, query, index="", id_lower_case=True):
        """
        This is a base method used to send a specific query to ES updating data in a specific AP

        :param string doc_id: The ID of the document to update
        :param ESQuery query: The query to send
        :param str index: Optional index field
        :param bool id_lower_case: Set the ID to lower case

        :return bool: True on a successful operation
        :raises ESAdapterException: On a failing operation
        """
        if not index:
            index = self.obj_index_name

        if id_lower_case:
            doc_id = doc_id.lower()

        # Make sure we have valid index names
        if not index or not self.obj_doc_type_name:
            raise ESAdapterException("Missing indexes for obj update")

        return self.update_es_doc(index=index,
                                  doc_type=self.obj_doc_type_name,
                                  doc_id=doc_id,
                                  query=query.get_query())

    def verify_returned_list_size(self, expected_list, actual_list):
        """
        This method verifies that a returned list from ES is the same size as the expected one
        :param list expected_list:
        :param list actual_list:
        """
        # Enter a log entry in case the list size is different
        if type(expected_list) == list and type(actual_list) == list:
            if len(expected_list) != len(actual_list):
                self.logger.warning("Got wrong list size from ES in %s, trying to get %s" % (class_name(self),
                                                                                             expected_list))
        else:
            self.logger.warning("Got wrong list param type in %s, with params %s, %s" % (class_name(self),
                                                                                         expected_list,
                                                                                         actual_list))

    @staticmethod
    def parse_delete_response(es_response):
        """
        Parsing the ES response when deleting items
        :param dictionary es_response:
        :return bool: Operation successful
        """
        if es_response:
            try:
                indexes_dict = es_response["_indices"]
                for index_name, status_dict in indexes_dict.items():
                    status = status_dict["_shards"]
                    # Return true when the operation was successful
                    if status["successful"] >= 1:
                        return True
            except KeyError:
                pass
        return False

    @staticmethod
    def parse_update_response(es_response):
        """
        This function retrieves and update request parsing
        :param dictionary es_response:
        :return bool: Operation successful
        """
        if es_response:
            try:
                # {u'_type': u'AP', u'_id': u'rzb81e4027711', u'_version': 399, u'_index': u'accesspoint'}
                if "type" and "_id" and "_version" and "_index" in es_response.keys():
                    return True
            except KeyError:
                pass
        return False

    @staticmethod
    def parse_save_response(es_response):
        """
        Parsing the ES response when deleting items
        :param dictionary es_response:
        :return bool: Operation successful
        """
        if es_response:
            try:
                status = es_response["created"]
                # Return true when the operation was successful
                if status:
                    return True
            except KeyError:
                pass
        return False

    def parse_bulk_response(self, es_response, item_list):
        """
        Parsing the response from the bulk operation, making sure it went alright
        :param tuple es_response: (success count, fail_list)
        :param list item_list: A list of the items to be originally saved
        :return bool:
        """
        success_num, fail_list = es_response
        # Check if we got a confirmation for a different number of successes
        if len(item_list) != success_num:
            self.logger.error("Bulk operation wasn't successful: %s, %s" % (es_response, item_list))

        if success_num > 0:
            return True
        return False

    def parse_es_aggregation_list(self, es_response, agg_name):
        """
        This method parses an ES aggregation into a list of values
        :param dictionary es_response: The response from ES
        :param string agg_name: The name of the aggregation to make a list
        :return list :
        """
        try:
            item_list_doc = extract_value(es_response, 'aggregations', agg_name, "buckets")
            item_list = []
            for items in item_list_doc:
                item_list.append(items['key'])

            return item_list
        except KeyError as exc:
            raise ESAdapterException("Error while trying to create a list in %s: %s" % (class_name(self), exc))

    @staticmethod
    def parse_es_put_operation_response(es_response):
        """
        This method parses the response received when creating an ES index
        :param dictionary es_response:
        :return bool:
        """
        if extract_value(es_response, "acknowledged"):
            return True
        else:
            return False

    @es_save_wrapper
    def create_new_index(self, index_name):
        """
        This method creates a new index with custom name and mapping in ES
        :param index_name:
        :return bool:
        """
        body_req = {"mappings": self._mapping}

        es_response = self.es.indices.create(index=index_name,
                                             body=body_req)

        return self.parse_es_put_operation_response(es_response)

    @es_save_wrapper
    def verify_existing_index(self, index_name):
        """
        This method checks if an index is existing, and in a different case create a new index with mapping
        :param string index_name:
        :return bool: Operation status
        """
        if not self.es.indices.exists(index_name):
            self.create_new_index(index_name)

        return True

    @es_save_wrapper
    def bulk_save_es_data(self, doc_list):
        """
        Save a list of documents in ES
        :param list doc_list: List of documents to be saved
        :return bool: Operation status
        """
        es_response = helpers.bulk(self.es, doc_list)
        return self.parse_bulk_response(es_response, doc_list)

    @retry_updates_to_es
    def update_es_doc(self, index, doc_type, doc_id, query):
        """
        This is a base method used to send a specific query to ES updating data in a specific AP

        :param string index: The index of the document
        :param string doc_type: The document type
        :param string doc_id: The document ID
        :param dictionary query: The query to send

        :return bool: True on a successful operation
        :raises ESAdapterException: On a failing operation
        """
        # Set the doc ID as the APs serial number
        es_response = self.es.update(index=index,
                                     doc_type=doc_type,
                                     id=doc_id,
                                     body=query)
        return self.parse_update_response(es_response)

    @staticmethod
    def create_es_doc(index, doc_type, source, timestamp="", doc_id=""):
        """
        This method create an ES doc for bulk operation
        :param str index: Index name
        :param str doc_type: Document type
        :param dict source: The documents body
        :param str timestamp: Optional timestamp for the document
        :param str doc_id: Optional ID for the document
        :return dict es_dict:
        """
        es_dict = {
                "_index": index,
                "_type": doc_type,
                "_source": source
                 }
        if timestamp:
            es_dict["_source"]["@timestamp"] = timestamp
        if doc_id:
            es_dict["_id"] = doc_id

        return es_dict

    @es_save_wrapper
    def save_multiple_serializable_objects(self, obj_list, id_name):
        """
        This method saves a single AP object in ES
        :param list obj_list: A list of OptHistoryAction() Objects to save in ES
        :param str id_name: A string describing the attributes used to get the object id: "actionId", "generalInfo.apId"
        :return bool: Returns True on a successful operation
        """
        bulk_data = []

        for obj in obj_list:
            # Add timestamp if it exists
            if hasattr(obj, "timestamp"):
                obj.timestamp = current_utc_time()
            try:
                doc_id = multi_getattr(obj, id_name)
            except AttributeError as exc:
                raise ESAdapterException("Couldn't find object id for object %s, %s, %s" %
                                         (class_name(obj), id_name, exc))
            obj_dict = {
                    "_index": self.index_name_to_save_obj(obj),
                    "_type": self.doc_type_name_to_save_obj(obj),
                    "_id": doc_id,
                    "_source": self._to_JSON(obj)
                     }
            bulk_data.append(obj_dict)

        # Bulk save the data in ES
        es_response = helpers.bulk(self.es, bulk_data)
        return self.parse_bulk_response(es_response, obj_list)

    def index_name_to_save_obj(self, obj):
        """
        :param obj: Empty input param just as a stub
        This method is used to get the index name, which is normally overrun in case
        we have multiple indexes to save objects to
        """
        return self.obj_index_name

    def index_name_to_get_obj(self):
        """
        This method is used to get the index name, which is normally overrun in case
        we have multiple indexes to save objects to
        """
        return self.obj_index_name

    def doc_type_name_to_save_obj(self, obj):
        """
        :param obj: Empty input param just as a stub
        This method is used to get the index name, which is normally overrun in case
        we have multiple indexes to save objects to
        """
        return self.obj_doc_type_name

    def doc_type_name_to_get_obj(self):
        """
        This method is used to get the index name, which is normally overrun in case
        we have multiple indexes to save objects to
        """
        return self.obj_doc_type_name

    @es_get_wrapper
    def get_multiple_serializable_objects(self, id_list, *obj_types):
        """
        This method gets a list of serial numbers and returns a list of AP objects
        :param list id_list: A list of serial numbers to fetch
        :param obj_types: A list of valid objects to be returns from the query in ES: (ClassA, ClassB)
        :return list AccessPointModel(): A list of APs
        :raises ESAdapterException: On a connection and transport error with ES
        """
        obj_list = []
        # Make sure id_list got a list of ids
        if id_list:
            es_response = self.es.search(index=self.index_name_to_get_obj(),
                                         doc_type=self.obj_doc_type_name,
                                         body=query_get_multiple_documents_from_list(id_list))
            obj_list = self.create_object_list_from_es_query(es_response, *obj_types)

        # Make sure we got the right size
        self.verify_returned_list_size(id_list, obj_list)
        return obj_list

    def get_single_serializable_object(self, obj_id, *obj_types):
        """
        This method gets a single serializable object from ES
        :param str obj_id: The object ID to fetch
        :param obj_types: A list of valid objects to be returns from the query in ES: (ClassA, ClassB)
        :return: The returned object
        """
        # Use the multiple api to get a single action
        obj_list = self.get_multiple_serializable_objects([obj_id], *obj_types)
        if obj_list:
            return obj_list[0]
        else:
            return None

    @es_get_wrapper
    def delete_multiple_serializable_objects(self, id_list, index=""):
        """
        This method gets a list of serial numbers and returns a list of AP objects
        :param list id_list: A list of serial numbers to fetch
        :param str index: Optional index for the function, if not received we take from the class
        :return list Object: A list of APs
        :raises ESAdapterException: On a connection and transport error with ES
        """
        status = False

        if not index:
            index = self.index_name_to_get_obj()
        # Make sure id_list got a list of ids
        if id_list:
            es_response = self.es.delete_by_query(index=index,
                                                  doc_type=self.obj_doc_type_name,
                                                  body=delete_multiple_documents_from_list(id_list))
            # Make sure we got the right size
            status = self.parse_delete_response(es_response)

        return status

    @es_get_wrapper
    def delete_index(self, index):
        """
        This method deletes a complete index in ES
        :param str index:
        :return bool: Operation status
        """
        es_response = self.es.indices.delete(index=index)
        return self.parse_es_put_operation_response(es_response)

    def parse_aggregation_response_to_dict(self, es_response):
        """
        Parses an ES response coming from a query returning a list of aggregated values
        The response is parse to {NAME: VALUE} dictionary
        :param dict es_response: Response from ES
        :return dict object_dict: {Name: Value}
        """
        object_dict = {}
        agg_dict = extract_value(es_response, "aggregations")
        if not agg_dict:
            self.logger.error("Error receiving aggregation dictionary from es query in %s, %s" % (class_name(self),
                                                                                                  es_response))
            return object_dict

        out_dict = {}
        self.aggregation_parser(out_dict, agg_dict)
        return out_dict

    @staticmethod
    def aggregation_parser(out_dict, agg_dict):
        """
        Parses a part of the aggregation tree recursively
        :param out_dict:
        :param agg_dict:
        """
        # Go over the items in the es_response
        for key, value_dict in agg_dict.items():
            if type(value_dict) == dict:
                # whenever we have some more aggregations of term
                if "buckets" in value_dict.keys():
                    agg_list = extract_value(value_dict, "buckets")
                    if agg_list:
                        # Go over the entire list
                        for i in range(len(agg_list)):
                            agg_dict = agg_list[i]
                            value = extract_value(agg_dict, "key")
                            if not value:
                                continue
                            # Check if we are at the last aggregation
                            # Recursion stops when we reach the last aggregation
                            if len(agg_dict.keys()) <= 2:
                                # If we have more to go
                                if len(agg_list) > 1:
                                    ESAdapter._add_to_dict(out_dict, key, value, value_as_list=True)
                                else:
                                    ESAdapter._add_to_dict(out_dict, key, value)
                            else:
                                ESAdapter._add_to_dict(out_dict, key, value, value_as_dict=True)
                                # Continue the recursion
                                ESAdapter.aggregation_parser(out_dict[key][value], agg_dict)

                # Parse value aggregations
                else:
                    value = extract_value(value_dict, "value")
                    ESAdapter._add_to_dict(out_dict, key, value)
        return out_dict

    @staticmethod
    def _add_to_dict(in_dict, key, value, value_as_dict=False, value_as_list=False):
        """
        Add a key to a dictionary if it doesnt exist
        :param dict in_dict:
        :param str key:
        :param value:
        """
        if key not in in_dict.keys():
            if value_as_list:
                in_dict[key] = []
            else:
                in_dict[key] = {}
        if not value:
            value = 0

        if value_as_dict:
            in_dict[key].update({value: {}})
        elif value_as_list:
            in_dict[key].append(value)
        else:
            in_dict[key] = value

    @es_get_wrapper
    def get_param_value_from_object(self, doc_id, param_list):
        """
        Get a list of field names and returns a dictionary of {param: [values]}
        :param str doc_id: The ID of the document
        :param list param_list:
        :return dict:
        """
        if type(param_list) is not list:
            raise ESAdapterException("get_param_value_from_object got wrong input list type %s in %s"
                                     % (param_list, class_name(self)))
        # Get a list of all the action Serial Numbers for the timestamp
        es_response = self.es.search(index=self.index_name_to_get_obj(),
                                     body=query_params_from_object(doc_id, param_list))
        param_dict = {}
        for param in param_list:
            value = self.parse_es_aggregation_list(es_response, param)
            if value:
                param_dict[param] = value

        return param_dict

    def get_single_param_value_from_object(self, serial_number, param_name):
        """
        Returns the profile name for a given AP
        :param str serial_number:
        :param str param_name: The name of the parameter to take from the list
        :return str: The value of the parameter
        """
        param_list = [param_name]
        params_dict = self.get_param_value_from_object(serial_number, param_list)
        name_list = extract_value(params_dict, param_list[0])

        # The returned value is a list of values
        if name_list and type(name_list) is list:
            return name_list[0]
        else:
            return ""

    @es_save_wrapper
    def save_template_list_in_es(self, template_list):
        """
        Save a list of elasticsearch templates in elasticsearch
        :param list template_list:
        :return bool:
        """
        status = False
        for template in template_list:
            es_response = self.es.indices.put_template(name=template["template"],
                                                       body=template)
            status = self.parse_es_put_operation_response(es_response)
        return status

    @staticmethod
    def parse_reindex_response(es_response):
        """
        Reindexing response is a tuple (1, 0)
        :param tuple es_response:
        :return bool:
        """
        success, failure = es_response
        if success > 0:
            return True
        return False

    @staticmethod
    def create_daily_index_list(index_pattern, min_timestamp, max_timestamp):
        """
        Create a list of indexes to search when using daily indexes
        :param str index_pattern:
        :param str min_timestamp:
        :param str max_timestamp:
        :return list index_list:
        """
        index_list = []
        min_day, min_month, min_year = extract_day_from_timestamp_string(min_timestamp)
        max_day, max_month, max_year = extract_day_from_timestamp_string(max_timestamp)
        d1 = date(min_year, min_month, min_day)
        d2 = date(max_year, max_month, max_day)

        delta = d2 - d1
        for i in range(delta.days + 1):
            index = "-".join((index_pattern, str(d1 + timedelta(days=i))))
            index_list.append(index)

        return index_list

    @es_get_wrapper
    def search_in_daily_index(self, index_pattern, min_timestamp, max_timestamp, query):
        """
        Create a list of indexes to search when using daily indexes
        :param str index_pattern:
        :param str min_timestamp:
        :param str max_timestamp:
        :param dict query:
        :return list index_list:
        """
        # index_list = self.create_daily_index_list(index_pattern, min_timestamp, max_timestamp)
        # patching for too ling indices
        # if len(index_list) > 30:

        index_list = index_pattern + "-*"

        es_response = self.es.search(index=index_list,
                                     body=query,
                                     request_timeout=120)
        values_dict = self.parse_aggregation_response_to_dict(es_response)

        return values_dict
