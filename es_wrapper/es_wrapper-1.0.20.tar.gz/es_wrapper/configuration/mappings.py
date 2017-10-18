from es_wrapper.general.datatypes import build_nested_mapping_dictionary, merge_dicts, extract_value
from es_wrapper.configuration.parameters import AP_DATA_NEIGHBOR_DOC_TYPE, ES_LOGGER_DOC_TYPE, ES_WLC_AP_DOC_TYPE, \
    ES_WLC_ROGUE_DOC_TYPE, ES_ACTIONS_DOC_TYPE, ES_SUMMARIZED_DOC_TYPE, WLAN_BANDS,\
    ES_EVAL_PERIOD_SUMMARIZED_DOC_TYPE, ES_PROFILE_DOC_TYPE, ES_AP_OBJ_DOC_TYPE, AP_DATA_TOTAL_STA_INFO_DOC_TYPE, \
    AP_DATA_STA_INFO_DOC_TYPE, AP_DATA_PING_INFO_DOC_TYPE, AP_DATA_INFO_DOC_TYPE, AP_DATA_USAGE_DOC_TYPE, \
    AP_DATA_ALTERNATE_INTERFACE_DOC_TYPE, AP_DATA_SITE_SURVEY_DOC_TYPE, AP_DATA_INTERFACE_DOC_TYPE, \
    ES_WLC_CONFIG_DOC_TYPE


class ESMapping:

    BOOLEAN = "boolean"
    STRING = "string"
    INTEGER = "integer"
    LONG = "long"
    DOUBLE = "double"
    GEOPOINT = "geopoint"
    TIME = "time"
    EPOCH = "epoch_millis"
    NESTED = "object"

    def __init__(self):
        self.mapping = {}

        self.function_mapper = {self.BOOLEAN: self.set_boolean_field,
                                self.STRING: self.set_string_field,
                                self.LONG: self.set_long_field,
                                self.INTEGER: self.set_integer_field,
                                self.DOUBLE: self.set_double_field,
                                self.GEOPOINT: self.set_geo_point_field,
                                self.TIME: self.set_time_field,
                                self.EPOCH: self.set_epoch_field,
                                self.NESTED: self.set_nested_field,
                                }

    @staticmethod
    def get_analyzed_string(is_analyzed):
        """
        return the needed string for the analyzed statues
        :param bool is_analyzed: Analyzed status
        return str: String representing and analyzed status ("analyzed"/"not_analyzed")
        """
        if is_analyzed:
            return "analyzed"
        else:
            return "not_analyzed"

    @staticmethod
    def set_string_field(is_analyzed=True):
        """
        sets string mapping values
        :param bool is_analyzed: Analyzed status
        :return dictionary:
        """
        return {"type": "string",
                # "fielddata": "true",
                "index": ESMapping.get_analyzed_string(is_analyzed)}

    @staticmethod
    def set_nested_field():
        return {"type": "nested"}

    @staticmethod
    def set_boolean_field():
        """
        set integer mapping values
        :return dictionary:
        """
        return {"type": "boolean"}

    @staticmethod
    def set_integer_field():
        """
        set integer mapping values
        :return dictionary:
        """
        return {"type": "integer"}

    @staticmethod
    def set_long_field():
        """
        sets long mapping values
        :return dictionary:
        """
        return {"type": "long"}

    @staticmethod
    def set_double_field():
        """
        sets double mapping values
        :return dictionary:
        """
        return {"type": "double"}

    @staticmethod
    def set_geo_point_field():
        """
        sets geo_point data type
        :return dictionary:
        """
        # return {"type": "geo_point",
        #         "geohash_prefix": "true",
        #         "lat_lon": "true",
        #         "geohash_precision": 11}
        return {"type": "geo_point"}

    @staticmethod
    def set_time_field():
        """
        sets number mapping values
        :return dictionary:
        """
        return {"type": "date",
                "format": "dateOptionalTime"}

    @staticmethod
    def set_epoch_field():
        """
        sets number mapping values
        :return dictionary:
        """
        return {"type": "date",
                "format": "epoch_millis"}

    def get_field_func(self, field_type):
        """
        Return the parsing function
        :param field_type:
        :return func:
        :raise ValueError: When received a wrong field_type
        """
        field_func = extract_value(self.function_mapper[field_type])
        # When we got an invalid field_type
        if not field_func:
            raise ValueError("Wrong field type received %s" % field_type)

        return field_func

    def add_field(self, doc_type, field_name, field_type, **kwargs):
        """
        This method add a new field to the document mapping
        :param str doc_type: Name of the document
        :param str field_name: Name of the field
        :param str field_type:
        :param kwargs:
        """
        # Get the field function by the field type
        field_func = self.get_field_func(field_type)
        self.mapping[doc_type]["properties"][field_name] = field_func(**kwargs)

    def add_nested_field(self, father_doc, doc_type, field_name, field_type, **kwargs):
        """
        Add a nested key value
        :param father_doc:
        :param doc_type:
        :param field_name:
        :param field_type:
        :param kwargs:
        :return:
        """
        # Get the field function by the field type
        field_func = self.get_field_func(field_type)
        self.mapping[father_doc]["properties"][doc_type]["properties"][field_name] = field_func(**kwargs)

    def create_new_doc(self, *args):
        """
        Build mapping for a new document, to support nested document keys
        :param args: Arguments for new document mapping creation
        :return dict index_dict: A dictionary containing the right structure for a new mapping
        """
        # Create a key list of the arguments
        key_list = [arg for arg in args]
        temp_d = {}
        temp_d = build_nested_mapping_dictionary(temp_d, [key_list])
        # Add the new doc's mapping to the original dictionary
        self.mapping = merge_dicts(self.mapping, temp_d)

    def get_mapping(self):
        """
        Returns the mapping dictionary
        :return dict:
        """
        return self.mapping


# logger-* - Index containing log messages from all modules
log_mapper = ESMapping()
log_mapper.create_new_doc(ES_LOGGER_DOC_TYPE)
log_mapper.add_field(ES_LOGGER_DOC_TYPE, "msg", ESMapping.STRING, is_analyzed=False)
log_mapper.add_field(ES_LOGGER_DOC_TYPE, "source_host", ESMapping.STRING, is_analyzed=False)

LOGGER_INDEX_MAPPING = log_mapper.get_mapping()

# ap-* - Index containing stream data from the AP
ap_mapper = ESMapping()

ap_mapper.create_new_doc(AP_DATA_NEIGHBOR_DOC_TYPE)
ap_mapper.add_field(AP_DATA_NEIGHBOR_DOC_TYPE, "IF_Chan", ESMapping.STRING)
ap_mapper.add_field(AP_DATA_NEIGHBOR_DOC_TYPE, "InterfaceMacAddress", ESMapping.STRING)
ap_mapper.add_field(AP_DATA_NEIGHBOR_DOC_TYPE, "apId", ESMapping.STRING)
ap_mapper.add_field(AP_DATA_NEIGHBOR_DOC_TYPE, "FrequencyBand", ESMapping.STRING)

ap_mapper.create_new_doc(AP_DATA_NEIGHBOR_DOC_TYPE, "Neighbors")
# Adding fields to a nested document
ap_mapper.add_nested_field(AP_DATA_NEIGHBOR_DOC_TYPE, "Neighbors", "SupportedRates", ESMapping.STRING, is_analyzed=False)
ap_mapper.add_nested_field(AP_DATA_NEIGHBOR_DOC_TYPE, "Neighbors", "Capability", ESMapping.STRING, is_analyzed=False)
ap_mapper.add_nested_field(AP_DATA_NEIGHBOR_DOC_TYPE, "Neighbors", "Channel", ESMapping.STRING, is_analyzed=False)
ap_mapper.add_nested_field(AP_DATA_NEIGHBOR_DOC_TYPE, "Neighbors", "Noise", ESMapping.LONG)
ap_mapper.add_nested_field(AP_DATA_NEIGHBOR_DOC_TYPE, "Neighbors", "RSSI", ESMapping.LONG)
ap_mapper.add_nested_field(AP_DATA_NEIGHBOR_DOC_TYPE, "Neighbors", "SNR", ESMapping.DOUBLE)
ap_mapper.add_nested_field(AP_DATA_NEIGHBOR_DOC_TYPE, "Neighbors", "SSID", ESMapping.STRING, is_analyzed=False)
ap_mapper.add_nested_field(AP_DATA_NEIGHBOR_DOC_TYPE, "Neighbors", "BSSID", ESMapping.STRING)
ap_mapper.add_nested_field(AP_DATA_NEIGHBOR_DOC_TYPE, "Neighbors", "FrequencyBand", ESMapping.STRING)


ap_mapper.create_new_doc(AP_DATA_TOTAL_STA_INFO_DOC_TYPE)
ap_mapper.add_field(AP_DATA_TOTAL_STA_INFO_DOC_TYPE, "FrequencyBand", ESMapping.STRING)
ap_mapper.create_new_doc(AP_DATA_TOTAL_STA_INFO_DOC_TYPE, "StaInfo")
ap_mapper.add_nested_field(AP_DATA_TOTAL_STA_INFO_DOC_TYPE, "StaInfo", "CommonRateSet", ESMapping.STRING, is_analyzed=False)

ap_mapper.create_new_doc(AP_DATA_STA_INFO_DOC_TYPE)
ap_mapper.create_new_doc(AP_DATA_STA_INFO_DOC_TYPE, "StaInfo")
ap_mapper.add_field(AP_DATA_STA_INFO_DOC_TYPE, "FrequencyBand", ESMapping.STRING)
ap_mapper.add_nested_field(AP_DATA_STA_INFO_DOC_TYPE, "StaInfo", "RateSet", ESMapping.STRING, is_analyzed=False)


ap_mapper.create_new_doc(AP_DATA_STA_INFO_DOC_TYPE)
ap_mapper.create_new_doc(AP_DATA_TOTAL_STA_INFO_DOC_TYPE, "TotalStaInfo")
ap_mapper.add_field(AP_DATA_STA_INFO_DOC_TYPE, "FrequencyBand", ESMapping.STRING)

ap_mapper.create_new_doc(AP_DATA_PING_INFO_DOC_TYPE)
ap_mapper.create_new_doc(AP_DATA_PING_INFO_DOC_TYPE, "PingInfo")
ap_mapper.add_field(AP_DATA_PING_INFO_DOC_TYPE, "FrequencyBand", ESMapping.STRING)
ap_mapper.add_nested_field(AP_DATA_PING_INFO_DOC_TYPE, "PingInfo", "PingTimestamp", ESMapping.TIME)


ap_mapper.create_new_doc(AP_DATA_INTERFACE_DOC_TYPE)
ap_mapper.create_new_doc(AP_DATA_INTERFACE_DOC_TYPE, "APInterface")
ap_mapper.add_field(AP_DATA_INTERFACE_DOC_TYPE, "FrequencyBand", ESMapping.STRING)


ap_mapper.create_new_doc(AP_DATA_INFO_DOC_TYPE)
ap_mapper.create_new_doc(AP_DATA_INFO_DOC_TYPE, "APInfo")
ap_mapper.add_field(AP_DATA_INFO_DOC_TYPE, "FrequencyBand", ESMapping.STRING)
ap_mapper.add_nested_field(AP_DATA_INFO_DOC_TYPE, "APInfo", "connectionRequestURL", ESMapping.STRING, is_analyzed=False)

ap_mapper.create_new_doc(AP_DATA_USAGE_DOC_TYPE)
ap_mapper.create_new_doc(AP_DATA_USAGE_DOC_TYPE, "NetworkUsage")
ap_mapper.add_field(AP_DATA_USAGE_DOC_TYPE, "FrequencyBand", ESMapping.STRING)
ap_mapper.add_nested_field(AP_DATA_USAGE_DOC_TYPE, "NetworkUsage", "FrequencyBand", ESMapping.STRING)

ap_mapper.create_new_doc(AP_DATA_ALTERNATE_INTERFACE_DOC_TYPE)
ap_mapper.add_field(AP_DATA_ALTERNATE_INTERFACE_DOC_TYPE, "FrequencyBand", ESMapping.STRING)

ap_mapper.create_new_doc(AP_DATA_SITE_SURVEY_DOC_TYPE)
ap_mapper.add_field(AP_DATA_SITE_SURVEY_DOC_TYPE, "FrequencyBand", ESMapping.STRING)


AP_DATA_INDEX_MAPPING = ap_mapper.get_mapping()

# wlc-* - Index containing data scraped from the WLC
wlc_mapper = ESMapping()
wlc_mapper.create_new_doc(ES_WLC_AP_DOC_TYPE)

# ES_WLC_AP_DOC_TYPE
wlc_mapper.add_field(ES_WLC_AP_DOC_TYPE, "apMac", ESMapping.STRING)
wlc_mapper.add_field(ES_WLC_AP_DOC_TYPE, "name", ESMapping.STRING)
wlc_mapper.add_field(ES_WLC_AP_DOC_TYPE, "radioType", ESMapping.STRING)
wlc_mapper.add_field(ES_WLC_AP_DOC_TYPE, "ssid", ESMapping.STRING)
wlc_mapper.add_field(ES_WLC_AP_DOC_TYPE, "timestamp", ESMapping.TIME)
wlc_mapper.add_field(ES_WLC_AP_DOC_TYPE, "channel", ESMapping.STRING)

# ES_WLC_ROGUE_DOC_TYPE
wlc_mapper.create_new_doc(ES_WLC_ROGUE_DOC_TYPE)
wlc_mapper.add_field(ES_WLC_ROGUE_DOC_TYPE, "apMac", ESMapping.STRING)
wlc_mapper.add_field(ES_WLC_ROGUE_DOC_TYPE, "channel", ESMapping.STRING)
wlc_mapper.add_field(ES_WLC_ROGUE_DOC_TYPE, "lastReported", ESMapping.TIME)
wlc_mapper.add_field(ES_WLC_ROGUE_DOC_TYPE, "bssid", ESMapping.STRING)
wlc_mapper.add_field(ES_WLC_ROGUE_DOC_TYPE, "rssi", ESMapping.LONG)
wlc_mapper.add_field(ES_WLC_ROGUE_DOC_TYPE, "snr", ESMapping.LONG)
wlc_mapper.add_field(ES_WLC_ROGUE_DOC_TYPE, "ssid", ESMapping.STRING)
wlc_mapper.add_field(ES_WLC_ROGUE_DOC_TYPE, "wlcIP", ESMapping.STRING)
wlc_mapper.add_field(ES_WLC_ROGUE_DOC_TYPE, "timestamp", ESMapping.TIME)

WLC_INDEX_MAPPING = wlc_mapper.get_mapping()


# opthistory - Index with OptActionHistory objects containing actions
action_mapper = ESMapping()
action_mapper.create_new_doc(ES_ACTIONS_DOC_TYPE)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "actionId", ESMapping.STRING)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "actionTimePeriod", ESMapping.LONG)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "apId", ESMapping.STRING)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "applyRetriesCounter", ESMapping.LONG)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "costMetricType", ESMapping.STRING)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "evalTimePeriod", ESMapping.LONG)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "failureReason", ESMapping.STRING)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "frequencyBand", ESMapping.STRING)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "newValue", ESMapping.LONG)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "oldValue", ESMapping.LONG)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "failureReason", ESMapping.STRING)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "frequencyBand", ESMapping.STRING)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "optAlgo", ESMapping.STRING)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "optCompleteTimestamp", ESMapping.TIME)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "optParam", ESMapping.STRING)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "optTimePeriod", ESMapping.LONG)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "postOptCostMetric", ESMapping.DOUBLE)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "preOptCostMetric", ESMapping.DOUBLE)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "rfClusterId", ESMapping.STRING)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "rgCommitTimestamp", ESMapping.TIME)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "rgSentTimestamp", ESMapping.TIME)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "rgEvalEndTimestamp", ESMapping.TIME)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "scheduledTimestamp", ESMapping.TIME)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "previewTimeout", ESMapping.TIME)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "status", ESMapping.STRING)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "timestamp", ESMapping.TIME)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "actionType", ESMapping.STRING)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "rejectReason", ESMapping.STRING, is_analyzed=False)
action_mapper.add_field(ES_ACTIONS_DOC_TYPE, "value", ESMapping.STRING)

OPT_ACTION_INDEX_MAPPING = action_mapper.get_mapping()

# summarizedap-* - Index with cost metric values
cost_metric_mapper = ESMapping()
# Create two documents, currently their are identical
cost_metric_mapper.create_new_doc(ES_SUMMARIZED_DOC_TYPE)
cost_metric_mapper.create_new_doc(ES_EVAL_PERIOD_SUMMARIZED_DOC_TYPE)

for doc_name in [ES_SUMMARIZED_DOC_TYPE, ES_EVAL_PERIOD_SUMMARIZED_DOC_TYPE]:
    # Create the documents fields
    cost_metric_mapper.add_field(doc_name, "@timestamp", ESMapping.TIME)
    cost_metric_mapper.add_field(doc_name, "apId", ESMapping.STRING)
    for band in WLAN_BANDS:
        cost_metric_mapper.create_new_doc(doc_name, band)
        cost_metric_mapper.add_nested_field(doc_name, band, "costMetric", ESMapping.DOUBLE)
        cost_metric_mapper.add_nested_field(doc_name, band, "hostsSignalStrengthCost", ESMapping.LONG)
        cost_metric_mapper.add_nested_field(doc_name, band, "isLocked", ESMapping.BOOLEAN)
        cost_metric_mapper.add_nested_field(doc_name, band, "isOutlier", ESMapping.BOOLEAN)

COST_METRIC_INDEX_MAPPING = cost_metric_mapper.get_mapping()


# profile - Index with Profiles
profile_mapper = ESMapping()
profile_mapper.create_new_doc(ES_PROFILE_DOC_TYPE)
profile_mapper.add_field(ES_PROFILE_DOC_TYPE, "profileName", ESMapping.STRING, is_analyzed=False)
profile_mapper.add_field(ES_PROFILE_DOC_TYPE, "profileDescription", ESMapping.STRING, is_analyzed=False)

PROFILE_INDEX_MAPPING = profile_mapper.get_mapping()


# accesspoint - Index with Access Point objects
access_point_mapper = ESMapping()
access_point_mapper.create_new_doc(ES_AP_OBJ_DOC_TYPE)
access_point_mapper.create_new_doc(ES_AP_OBJ_DOC_TYPE, "generalInfo")
access_point_mapper.add_nested_field(ES_AP_OBJ_DOC_TYPE,
                                     "generalInfo",
                                     "connectionRequestURL",
                                     ESMapping.STRING,
                                     is_analyzed=False)

access_point_mapper.create_new_doc(ES_AP_OBJ_DOC_TYPE,
                                   "profileInfo")
access_point_mapper.add_nested_field(ES_AP_OBJ_DOC_TYPE,
                                     "profileInfo",
                                     "profileName",
                                     ESMapping.STRING,
                                     is_analyzed=False)

ACCESS_POINT_INDEX_MAPPING = access_point_mapper.get_mapping()


# WLC Credentials - Index with Profiles
credentials_mapper = ESMapping()
credentials_mapper.create_new_doc(ES_WLC_CONFIG_DOC_TYPE)
credentials_mapper.add_field(ES_WLC_CONFIG_DOC_TYPE, "configId", ESMapping.STRING, is_analyzed=False)
credentials_mapper.add_field(ES_WLC_CONFIG_DOC_TYPE, "user", ESMapping.STRING, is_analyzed=False)
credentials_mapper.add_field(ES_WLC_CONFIG_DOC_TYPE, "password", ESMapping.STRING, is_analyzed=False)
credentials_mapper.add_field(ES_WLC_CONFIG_DOC_TYPE, "ip", ESMapping.STRING, is_analyzed=False)

WLC_CONFIG_INDEX_MAPPING = credentials_mapper.get_mapping()

