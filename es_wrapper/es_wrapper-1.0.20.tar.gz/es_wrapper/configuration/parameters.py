import os
from es_wrapper.general.datatypes import extract_value, parse_range, parse_range_list, str2bool


def get_env_var_value(env_var_name, default_value):
    """
    This method tries to get a value from the environment vars, and in
    case of failure returns a default value
    :param str env_var_name:
    :param default_value:
    """
    try:
        return os.environ[env_var_name]
    except KeyError:
        return default_value


def parse_kafka_partitions(partition_str):
    """
    Parsing two types of kafka partitions
    :param partition_str:
    :return list:
    """
    if not partition_str:
        return []
    if "-" in partition_str:
        return parse_range(partition_str)
    else:
        return parse_range_list(partition_str)


def parse_string_to_list(list_str):

    if list_str:
        try:
            # out_list = ast.literal_eval(list_str)
            out_list = list_str.split(",")
            # # print type(out_list)
            if type(out_list) != list:
                return [out_list]
            else:
                return out_list
        except TypeError as exc:
            pass
    return []

# Constants - run mode
SIMULATOR_MODE = "simulator"
PRODUCTION_MODE = "production"
# Getting the debug mode from the environment
SYS_DEBUG_MODE = str2bool(get_env_var_value("DEBUG_MODE", "False"))
DEV_MODE = str2bool(get_env_var_value("DEV_MODE", 'False'))

ACS_HTTP_PROXY = get_env_var_value("ACS_PROXY", "")

RG_RRM_LOGGER = "rg_rrm_package"
KAFKA_LOGGER = "kafka"

ID_LENGTH = 16

BAND_24GHz = "2.4ghz"
BAND_5GHz = "5ghz"
WLAN_BANDS = [BAND_24GHz, BAND_5GHz]

BAND_INTERFACE_ID_DICT = {BAND_24GHz: "1_5",
                          BAND_5GHz: "1_6"}

band_dict = {BAND_24GHz: "BAND_24GHz",
             BAND_5GHz: "BAND_5GHz"}
WLAN_CHANNELS = {BAND_24GHz: [x for x in range(1, 12)],
                 BAND_5GHz: [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 149, 153, 157, 161],
                 }


def convert_band_name(band):
    return value_from_dict(band_dict, band)

cost_func_dict = {"cost_metric_errors_only": "ERRORS_ONLY",
                  "cost_metric_errors_and_noise": "ERRORS_AND_NOISE"}
DEFAULT_COST_METRIC_FUNCTION = "cost_metric_errors_and_noise"
DEFAULT_COST_METRIC_THRESHOLD = 25


def convert_cost_function_to_enum(func_name):
    return value_from_dict(cost_func_dict, func_name)


def value_from_dict(dict_name, key):
    """
    Get a value from a dictionary, return "" if not existing
    :param dict_name:
    :param key:
    :return:
    """
    try:
        return dict_name[key]
    except KeyError:
        return ""

SIGNAL_STRENGTH_LIST = ["none", "poor", "fair", "good", "very_good", "excellent"]
STRENGTH_ENUM_DICT = {"none": 0,
                      "poor": 2,
                      "fair": 4,
                      "good": 6,
                      "very_good": 8,
                      "excellent": 10,
                      }

# ES Query Parameters
ES_MAX_QUERY_SIZE = 50000

PAYLOAD_ZLIB_ACTIVE = False

ES_AP_OBJ_INDEX = "accesspoint"
ES_AP_OBJ_DOC_TYPE = "AP"

ES_ACTIONS_DOC_TYPE = "OptHistory"

ES_ACTIONS_INDEX = "opthistory"
ES_ACTIONS_GET_INDEX = ES_ACTIONS_INDEX
ES_MANUAL_ACTIONS_INDEX = "opthistory-manual"
ES_SETTINGS_ACTIONS_INDEX = "opthistory-settings"
ES_MANUAL_AND_SETTINGS_ACTIONS_GET_INDEX = "opthistory-*"
ES_ALL_ACTIONS_GET_INDEX = "opthistory*"
ES_ACTIONS_TEMPLATE_NAME = "opthistory*"

ES_SUMMARIZED_GET_INDEX = "summarizedap"
ES_SUMMARIZED_SAVE_INDEX = "summarizedap"  # This needs to be called from generate_daily_index()
ES_SUMMARIZED_TEMPLATE_NAME = "-".join((ES_SUMMARIZED_GET_INDEX, "*"))

ES_SUMMARIZED_DOC_TYPE = "SummarizedAP"
ES_EVAL_PERIOD_SUMMARIZED_DOC_TYPE = "EvalPeriodSummarizedAP"

ES_AP_DATA_GET_INDEX = "ap"
ES_AP_DATA_SAVE_INDEX = "ap"  # This needs to be called from generate_daily_index()
ES_AP_DATA_TEMPLATE_NAME = "-".join((ES_AP_DATA_GET_INDEX, "*"))

AP_DATA_NEIGHBOR_DOC_TYPE = "Neighbors"
AP_DATA_USAGE_DOC_TYPE = "NetworkUsage"
AP_DATA_INFO_DOC_TYPE = "APInfo"
AP_DATA_SITE_SURVEY_DOC_TYPE = "SiteSurvey"
AP_DATA_INTERFACE_DOC_TYPE = "APInterface"
AP_DATA_ALTERNATE_INTERFACE_DOC_TYPE = "AlternateAPInterface"

AP_DATA_ERRORS_DOC_TYPE = "ClientErrors"
AP_DATA_STA_INFO_DOC_TYPE = "StaInfo"
AP_DATA_TOTAL_STA_INFO_DOC_TYPE = "TotalStaInfo"
AP_DATA_PING_INFO_DOC_TYPE = "PingInfo"

AP_TEST_INFO_DOC_TYPE = "TestMessage"


ES_CLUSTER_INDEX = "clusters"
ES_CLUSTER_DOC_TYPE = "Cluster"
ES_CLUSTER_TEMPLATE_NAME = "cluster*"

ES_LOGGER_GET_INDEX = "logger"
ES_LOGGER_SAVE_INDEX = "logger"  # This needs to be called from generate_daily_index()
ES_LOGGER_DOC_TYPE = "LogMessage"
ES_LOGGER_TEMPLATE_NAME = "-".join((ES_LOGGER_GET_INDEX, "*"))


ES_WLC_GET_INDEX = "wlc"
ES_WLC_SAVE_INDEX = "wlc"  # This needs to be called from generate_daily_index()
ES_WLC_TEMPLATE_NAME = "-".join((ES_WLC_SAVE_INDEX, "*"))

ES_WLC_DOC_TYPE = "Wlc"
ES_WLC_AP_DOC_TYPE = "WlcAP"
ES_WLC_ROGUE_DOC_TYPE = "Rogue"
ES_WLC_CHANNEL_COST_DOC_TYPE = "ChannelCost"

#  Profile doc
ES_PROFILE_INDEX = "profiles"
ES_PROFILE_DOC_TYPE = "profile"
ES_MASTER_PROFILE = "master_profile"
DAY_LIST = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
DAYS_OF_WEEK_DICT = {"Sun": 0, "Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6}
ES_PROFILE_TEMPLATE_NAME = "profile*"

ES_CREDENTIALS_INDEX = "credentials"
ES_CREDENTIALS_TEMPLATE_NAME = "credential*"

ES_WLC_CONFIG_DOC_TYPE = "WlcConfig"

# Sta data
ES_STA_CLIENT_INDEX = "staclient"
ES_STA_CLIENT_TYPE = "StaClient"


ES_TIMEOUT_TRIALS = 3
# ES_SERVER_URL = get_env_var_value("ES_SERVER_URL", "10.11.1.11")
# Kafka URLs
KAFKA_LISTEN_PORT = 8080
KAFKA_TOPICS_GROUP = "test-consumer-group"

partitions = get_env_var_value("KAFKA_TOPIC_PARTITION", "")
KAFKA_TOPIC_PARTITION = parse_kafka_partitions(partitions)

# Outliers Manager
CLUSTER_MAX_SIZE = 50
STRONG_RSSI_RELATION_VALUE = -85


KAFKA_OUTLIERS_CLUSTER_BAND_24GHZ = "outliers_cluster_band_24ghz"
KAFKA_OUTLIERS_CLUSTER_BAND_5GHZ = "outliers_cluster_band_5ghz"
BAND_TO_KAFKA_TOPIC_MAP = {BAND_24GHz: KAFKA_OUTLIERS_CLUSTER_BAND_24GHZ,
                           BAND_5GHz: KAFKA_OUTLIERS_CLUSTER_BAND_5GHZ}


KAFKA_OPT_ACTIONS_TOPIC = "opt_actions"

KAFKA_RG_GENERAL_INFO_TOPIC = "general_info"
KAFKA_RG_RADIO_INFO_TOPIC = "radio_info_topic"
KAFKA_RG_HOST_USAGE_INFO_TOPIC = "hosts_usage_info"
KAFKA_RG_ERROR_MESSAGE_TOPIC = "error_message"
KAFKA_LOG_MESSAGE_TOPIC = "log_message"
KAFKA_WLC_DATA_TOPIC = "wlc_data"
KAFKA_CLUSTER_REJECTED_TOPIC = "cluster_rejected_topic"
KAFKA_OPT_ACTIONS_STATUS_TOPIC = "opt_actions_status_topic"
KAFKA_PROFILE_UPDATED_TOPIC = "profile_updated_topic"
KAFKA_TEST_TOPIC = "test_topic"

HTTP = "http"
HTTPS = "https"


GENERAL_INFO_RW_API = 'general_info'
RADIO_INFO_RW_API = 'radio_info'
HOSTS_USAGE_INFO_RW_API = 'hosts_usage_info'
LOG_MESSAGE_RW_API = 'log_message'
RG_ACTION_RW_API = 'rg_action'
IS_ALIVE_RW_API = 'is_alive'
RG_SETTINGS_RW_API = "rg_settings"
STA_CLIENT_RW_API = "sta_client"
TEST_RW_API = "test"

KAFKA_TOPIC_TO_RW_API_MAPPER = {KAFKA_RG_GENERAL_INFO_TOPIC: GENERAL_INFO_RW_API,
                                KAFKA_RG_RADIO_INFO_TOPIC: RADIO_INFO_RW_API,
                                KAFKA_RG_HOST_USAGE_INFO_TOPIC: HOSTS_USAGE_INFO_RW_API,
                                KAFKA_LOG_MESSAGE_TOPIC: LOG_MESSAGE_RW_API,
                                IS_ALIVE_RW_API: IS_ALIVE_RW_API,
                                }


def convert_kafka_topic_to_rest_api(kafka_topic):
    return extract_value(KAFKA_TOPIC_TO_RW_API_MAPPER, kafka_topic)


# Time Intervals
MINUTE_SECONDS = 60
HOUR_SECONDS = 60 * MINUTE_SECONDS
DAY_SECONDS = 24 * HOUR_SECONDS
WEEK_SECONDS = 7 * DAY_SECONDS
MONTH_SECONDS = 4 * WEEK_SECONDS

OUTLIERS_ACTIVE_TIME = 1 * HOUR_SECONDS

# Action Status modes
ACTION_PENDING = "pending"
ACTION_SENT = "sent"
ACTION_COMMIT = "commit"
ACTION_COMPLETE = "complete"

ACTION_FAILED = "failed"
ACTION_FAILED_ACS_ERROR = "failed_acs"
ACTION_FAILED_TIMEOUT_ERROR = "failed_timeout"

ACTION_TYPE_COMMIT = "action_commit"
ACTION_TYPE_PREVIEW = "action_preview"
ACTION_TYPE_REJECTED = "action_rejected"
ACTION_TYPE_DONT_OPTIMIZE = "action_dont_optimize"
ACTION_TYPE_REVERT = "action_revert"

DEFAULT_PREVIEW_TIMEOUT = 4 * HOUR_SECONDS


def validate_action_type(action_type):
    """
    This method verifies that the inserted action type is valid
    :param str action_type: The checked action type
    """
    # Make sure its lower case
    action_type = str(action_type).lower()
    if action_type in ACTION_TYPE_LIST:
        return True

    return False

ACTION_TYPE_LIST = [ACTION_TYPE_COMMIT, ACTION_TYPE_PREVIEW, ACTION_TYPE_REJECTED, ACTION_TYPE_DONT_OPTIMIZE]
DEFAULT_ACTION_TYPE = ACTION_TYPE_COMMIT

# Params
ACTION_CHANNEL = "CHANNEL"
ACTION_MODULATION_RATE = "MODULATION_RATE"
ACTION_TXPOWER = "TXPOWER"
ACTION_UPDATE_APP_VERSION = "UPDATE_APP_VERSION"


ACTION_OPT_ALGO_LIST = [ACTION_CHANNEL, ACTION_MODULATION_RATE, ACTION_TXPOWER]
ACTION_TIMEOUT_VALUE = 4 * HOUR_SECONDS  # 24 * HOUR_SECONDS

# Max number for ACS command retires
ACTION_MAX_RETRIES = 3

# optParam -> APInterface.__members__
opt_param_to_members_dict = {ACTION_CHANNEL: "channel",
                             ACTION_TXPOWER: "transmitPower",
                             ACTION_MODULATION_RATE: "possibleFrequencyBands"}


def convert_action_param_to_member_name(param_name):
    return value_from_dict(opt_param_to_members_dict, param_name)


# Action Status modes
CLUSTER_INIT = "init"
CLUSTER_LOCKED = "locked"
CLUSTER_UNLOCKED = "unlocked"

# AP Summarizer
C_DEFAULT_SUMMARIZER_INTERVAL = 15 * MINUTE_SECONDS
DEFAULT_COST_METRIC_SAMPLES = DAY_SECONDS / C_DEFAULT_SUMMARIZER_INTERVAL  # sampling for a day


# FOR RW MODULE
DIRECT_RG_RW_MODE = 1
ACS_RW_MODE = 2

ACTIVE_RW_MODE = ACS_RW_MODE

# Clusters
CLUSTERS_BUILDER_TIME_INTERVAL = MINUTE_SECONDS * 15
PENDING_OPT_ACTIONS_TIME_INTERVAL = MINUTE_SECONDS * 15
UNLOCK_CLUSTERS_TIME_INTERVAL = MINUTE_SECONDS * 15

TR69_WLAN_CONFIG_PATH = {BAND_24GHz: "InternetGatewayDevice.LANDevice.1.WLANConfiguration.5.",
                         BAND_5GHz: "InternetGatewayDevice.LANDevice.1.WLANConfiguration.6."}

TR69_WLAN_PARAMETERS_DICT = {ACTION_CHANNEL: ["Channel"],
                             ACTION_MODULATION_RATE: ["BasicDataTransmitRates", "OperationalDataTransmitRates"],
                             ACTION_TXPOWER: ["TransmitPower"]}

# Logger
RG_RW_WEB_SERVER_PROCESS = "RwWebServer"
RG_DATA_SUMMARIZER_PROCESS = "DataSummarizer"
RG_MESSAGE_HANDLER_PROCESS = "MessageHandler"
RG_OUTLIERS_MANAGER = "OutliersManager"

# WLC
DEFAULT_WLC_COLLECTOR_INTERVAL = 12 * HOUR_SECONDS
# DEFAULT_WLC_COLLECTOR_INTERVAL = 60 * MINUTE_SECONDS

DEFAULT_NEIGHBOR_CAPABILITY = "ESS WEP RRM"
DEFAULT_NEIGHBOR_SUPPORTED_RATES = "[ 1(b) 2(b) 5.5(b) 6 9 11(b) 12 18 24 36 48 54 ]"
DEFAULT_ROGUE_SSID = "aaaabbbbccccdddd"

DEFAULT_PHY_RATE_VALUE = 1
DEFAULT_CHANNEL_COST_VALUE = 10

# Outlier Calc
# DEFAULT_EVAL_TIME = 4 * HOUR_SECONDS
DEFAULT_EVAL_TIME = 1 * HOUR_SECONDS
COST_METRIC_SAMPLES_PERCENTAGE = 70

# Profiles
DEFAULT_AP_PROFILE_NAME = "master_profile"
DEFAULT_SP_ID = "2368395399420206"
PROFILE_ACCESS_ADMIN = "rrm_admin"
PROFILE_ACCESS_DEV = "rrm_dev"

# Profile Params
COST_METRIC_THRESHOLD_PARAM_NAME = "costMetricThreshold"
COST_METRIC_FUNCTION_PARAM_NAME = "costMetricFunction"
COST_METRIC_TYPE_PARAM_NAME = "costMetricType"
COST_METRIC_SAMPLES_PERCENTAGE_PARAM_NAME = "costMetricSamplePct"
ERROR_METRIC_WEIGHT_PARAM_NAME = "errorMetricWeight"
OUTLIER_EVAL_TIME_PARAM_NAME = "outlierEvalTime"

RSSI_THRESHOLD_PARAM_NAME = "rssiThreshold"
SNR_METRIC_WEIGHT_PARAM_NAME = "snrMetricWeight"

ACS_URL_PARAM_NAME = "acsURL"
ACS_API_PARAM_NAME = "acsAPI"
ACS_IP_PARAM_NAME = "acsIP"
ACS_PROXY_PARAM_NAME = "acsProxy"
ACS_RW_MODE_PARAM_NAME = "acsRWMode"
DIRECT_RG_RW_MODE_PARAM_NAME = "directRGRWMode"

CLUSTER_MAX_SIZE_PARAM_NAME = "clusterMaxSize"
CLUSTER_STRONG_RSSI_RELATION_PARAM_NAME = "clusterStrongRSSIRelation"

ES_MAX_QUERY_SIZE_PARAM_NAME= "esMaxQuerySize"
ES_RETRIES_PARAM_NAME = "esRetries"
ES_SERVER_URL_PARAM_NAME = "esServerURL"

ACTION_TYPE_PARAM_NAME = "actionType"
ACTION_TIME_PERIOD_PARAM_NAME = "actionTimePeriod"
ACTION_EVAL_TIME_PERIOD_PARAM_NAME = "actionEvalTimePeriod"

PREVIEW_TIMEOUT_PARAM_NAME = "previewTimeout"
PREVIEW_TIMEOUT_REJECT_REASON = "Preview Action has timeout"
RG_RRM_CLIENT_VERSION_PARAM_NAME = "rgRrmClientVersion"
RG_RRM_CHECK_CLIENT_VERSION_PARAM_NAME = "rgRrmCheckClientVersion"

RG_RESPONSE_CACHE_SERVICE_URL = "http://localhost:8088/rg_response/{0}"

OPT_TIME_PERIOD_PARAM_NAME = "optTimePeriod"
OPT_EVAL_TIME_PERIOD_PARAM_NAME = "evalWindowMargin"

DEFAULT_TIME_FOR_BSSID_SEARCH = 12 * HOUR_SECONDS

RSSI_LOWER_LIMIT = -80

