from pprint import pprint

from es_wrapper.tools.infra import ESQuery, ESInterval
from es_wrapper.configuration.parameters import BAND_24GHz, BAND_5GHz, AP_DATA_ALTERNATE_INTERFACE_DOC_TYPE,\
    ACTION_TYPE_DONT_OPTIMIZE, AP_DATA_SITE_SURVEY_DOC_TYPE, AP_DATA_STA_INFO_DOC_TYPE, AP_DATA_INTERFACE_DOC_TYPE, \
    AP_DATA_TOTAL_STA_INFO_DOC_TYPE, AP_DATA_USAGE_DOC_TYPE, AP_DATA_PING_INFO_DOC_TYPE, AP_DATA_INFO_DOC_TYPE


def query_saturation_for_ap_object(serial_number, min_timestamp, max_timestamp):
    """
    Querying by this order:
    1. Average SiteSurvey.Saturation for all SiteSurvey.Channel

    :param string serial_number:
    :param string min_timestamp:
    :param string max_timestamp:
    :return dictionary query: The query for elastic search
    """
    serial_number = str(serial_number).lower()

    # Make sure serial number is lower case
    query = ESQuery()
    query.must_match_single_value("apId", serial_number)
    query.must_match_single_value("_type", AP_DATA_SITE_SURVEY_DOC_TYPE)
    query.must_match_timestamp("@timestamp", gte=min_timestamp, lte=max_timestamp)

    query.add_aggregation(agg_name="band",
                          field="FrequencyBand",
                          agg_type=ESQuery.TERMS,
                          size=2
                          )

    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="channel",
                              field="SiteSurvey.Channel",
                              agg_type=ESQuery.TERMS
                              )

    query.add_sub_aggregation(top_agg_name=["band", "channel"],
                              sub_agg_name="saturation",
                              field="SiteSurvey.Saturation",
                              agg_type=ESQuery.AVERAGE
                              )

    return query.get_query()


def query_params_for_ap_object(serial_number, min_timestamp, max_timestamp):
    """
    Querying by this order:
    1. APInterface.RF.Noise
    2. APInterface.RF.TransmitPower
    3. APInterface.RF.TransmitPowerPercent
    4. APInterface.RF.DownlinkErrors
    5. APInterface.RF.UplinkErrors
    6. APInterface.RF.Channel
    7. APInterface.RF.PossibleDataTransmitRates
    8. APInterface.RF.BSSID
    9. APInterface.RF.SSID
    :param string serial_number:
    :param string min_timestamp:
    :param string max_timestamp:
    :return dictionary query: The query for elastic search
    """
    serial_number = str(serial_number).lower()

    # Make sure serial number is lower case
    query = ESQuery()
    query.must_match_single_value("apId", serial_number)
    query.must_match_timestamp("@timestamp", gte=min_timestamp, lte=max_timestamp)

    query.add_aggregation(agg_name="band",
                          field="APInterface.RF.FrequencyBand",
                          agg_type=ESQuery.TERMS,
                          size=2
                          )

    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="noise",
                              field="APInterface.RF.Noise",
                              agg_type=ESQuery.AVERAGE,
                              )
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="transmitPower",
                              field="APInterface.RF.TransmitPower",
                              agg_type=ESQuery.AVERAGE,
                              )
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="transmitPowerPercent",
                              field="APInterface.RF.TransmitPowerPercent",
                              agg_type=ESQuery.AVERAGE,
                              )
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="downlinkErrors",
                              field="APInterface.RF.DownlinkErrors",
                              agg_type=ESQuery.AVERAGE,
                              )
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="uplinkErrors",
                              field="APInterface.RF.UplinkErrors",
                              agg_type=ESQuery.AVERAGE,
                              )
    # Terms
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="channel",
                              field="APInterface.RF.Channel",
                              agg_type=ESQuery.TERMS,
                              )
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="possibleDataTransmitRates",
                              field="APInterface.RF.PossibleDataTransmitRates",
                              agg_type=ESQuery.TERMS,
                              size=1
                              )
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="bssid",
                              field="APInterface.RF.BSSID",
                              agg_type=ESQuery.TERMS,
                              )
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="ssid",
                              field="APInterface.RF.SSID",
                              agg_type=ESQuery.TERMS,
                              size=4
                              )
    return query.get_query()


def query_general_info_for_object(serial_number, min_timestamp, max_timestamp):
    """
    Querying by this order:
    1. APInfo.WANDevice.ExternalIPAddress
    1. APInfo.WANDevice.MacAddress

    :param string serial_number:
    :param string min_timestamp:
    :param string max_timestamp:
    :return dictionary query: The query for elastic search
    """
    serial_number = str(serial_number).lower()

    # Make sure serial number is lower case
    query = ESQuery()
    query.must_match_single_value("apId", serial_number)
    query.must_match_timestamp("@timestamp", gte=min_timestamp, lte=max_timestamp)

    query.add_aggregation(agg_name="externalIPAddress",
                          field="APInfo.WANDevice.ExternalIPAddress",
                          agg_type=ESQuery.TERMS,
                          )
    query.add_aggregation(agg_name="macAddress",
                          field="APInfo.WANDevice.MacAddress",
                          agg_type=ESQuery.TERMS,
                          )
    query.add_aggregation(agg_name="connectionRequestURL",
                          field="APInfo.ConnectionRequestURL",
                          agg_type=ESQuery.TERMS,
                          )
    return query.get_query()


def query_get_serial_number_by_bssid(bssid):
    """
    Querying by this order:
    1. interfaces.BAND.BSSID

    :param string bssid:
    :return dictionary query: The query for elastic search
    """
    query_24 = ".".join(("interfaces", BAND_24GHz, "bssid"))
    query_5 = ".".join(("interfaces", BAND_5GHz, "bssid"))

    # Make sure serial number is lower case
    query = ESQuery()

    query.should_match_single_value(query_24, bssid)
    query.should_match_single_value(query_5, bssid)

    return query.get_query()


def query_get_multiple_serial_numbers_by_multiple_bssids(band, bssid_list):
    """
    This query returns an documents of APs by bssids
    :param band: Band enum
    :param list bssid_list: A list of BSSIDs to query
    :return dictionary query:
    """

    # Make sure serial number is lower case
    query = ESQuery()

    query_str = ".".join(("interfaces", band, "BSSID"))

    query.must_match_multiple_values(field=query_str, value_list=bssid_list)

    return query.get_query()


def query_bssids_and_serial_numbers(band, bssid_list):
    """
    This query returns an aggregations of multiple bssids and their respective serial numbers
    :param band: Band enum
    :param list bssid_list: A list of BSSIDs to query
    :return dictionary query:
    """
    # Query for the necessary interfaces
    bssid_field = ".".join(("interfaces", band, "bssid"))
    alternate_bssid_field = ".".join(("alternateInterfaces", band, "bssid"))

    # Make sure serial number is lower case
    query = ESQuery()
    query.should_match_multiple_values(field=bssid_field, value_list=bssid_list)
    query.should_match_multiple_values(field=alternate_bssid_field, value_list=bssid_list)

    query.add_aggregation(agg_name="apId",
                          field="generalInfo.apId",
                          agg_type=ESQuery.TERMS,
                          )

    query.add_sub_aggregation(top_agg_name="apId",
                              sub_agg_name="BSSID",
                              field=bssid_field,
                              agg_type=ESQuery.TERMS
                              )
    query.add_sub_aggregation(top_agg_name="apId",
                              sub_agg_name="alternateBSSID",
                              field=alternate_bssid_field,
                              agg_type=ESQuery.TERMS
                              )

    return query.get_query()


def query_neighbor_list(min_timestamp, max_timestamp, serial_number=None, bssid_list=None):
    """
    This query returns the neighbor list with average values for a specific serial number
    :param string serial_number: Serial Number for the specific AP
    :param string min_timestamp: minimal timestamp to query
    :param string max_timestamp: maximal timestamp to query
    :param list bssid_list: A list of bssids to query
    :return dictionary query:
    """

    query = ESQuery()
    query.must_match_timestamp("@timestamp", gte=min_timestamp, lte=max_timestamp)

    if serial_number:
        # Make sure serial number is lower case
        serial_number = str(serial_number).lower()
        query.must_match_single_value("apId", serial_number)

    if bssid_list is not None:
        query.must_match_multiple_values("Neighbors.BSSID", bssid_list)

    query.add_aggregation(agg_name="band",
                          field="FrequencyBand",
                          agg_type=ESQuery.TERMS,
                          size=10)

    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="BSSIDs",
                              field="Neighbors.BSSID",
                              agg_type=ESQuery.TERMS,
                              size=10
                              )

    query.add_sub_aggregation(top_agg_name=["band", "BSSIDs"],
                              sub_agg_name="rssi",
                              field="Neighbors.RSSI",
                              agg_type=ESQuery.AVERAGE
                              )
    query.add_sub_aggregation(top_agg_name=["band", "BSSIDs"],
                              sub_agg_name="noise",
                              field="Neighbors.Noise",
                              agg_type=ESQuery.AVERAGE
                              )
    query.add_sub_aggregation(top_agg_name=["band", "BSSIDs"],
                              sub_agg_name="snr",
                              field="Neighbors.SNR",
                              agg_type=ESQuery.AVERAGE
                              )
    query.add_sub_aggregation(top_agg_name=["band", "BSSIDs"],
                              sub_agg_name="channel",
                              field="Neighbors.Channel",
                              agg_type=ESQuery.TERMS
                              )
    query.add_sub_aggregation(top_agg_name=["band", "BSSIDs"],
                              sub_agg_name="ssid",
                              field="Neighbors.SSID",
                              agg_type=ESQuery.TERMS
                              )
    query.add_sub_aggregation(top_agg_name=["band", "BSSIDs"],
                              sub_agg_name="capability",
                              field="Neighbors.Capability",
                              agg_type=ESQuery.TERMS,
                              size=5
                              )
    query.add_sub_aggregation(top_agg_name=["band", "BSSIDs"],
                              sub_agg_name="supportedRates",
                              field="Neighbors.SupportedRates",
                              agg_type=ESQuery.TERMS,
                              size=5
                              )
    return query.get_query()


def get_all_serial_numbers(min_timestamp, max_timestamp):
    """
    This query returns an aggregation of all active serial numbers in ES
    :param string min_timestamp: minimal timestamp to query
    :param string max_timestamp: maximal timestamp to query
    :return dictionary query:
    """
    query = ESQuery()
    query.must_match_timestamp("@timestamp", gte=min_timestamp, lte=max_timestamp)

    query.add_aggregation(agg_name="apIds",
                          field="apId",
                          agg_type=ESQuery.TERMS)

    query.add_filter_query(filter_query="_type: APInterface AND APInterface.RF.SSID: *")

    return query.get_query()


def query_all_outlier_aps(band, min_timestamp):
    """
    This query returns the AP documents of all the APs which are considered outliers
    -   isLocked = False
    -   isOutlier = True
    :param string band: BANDs enum
    :param string min_timestamp: The minimum update timestamp to look for
    :return dictionary query:
    """

    # Create the query string
    is_locked = ".".join(("interfaces", band, "isLocked"))
    is_outlier = ".".join(("interfaces", band, "isOutlier"))

    query = ESQuery()
    query.must_match_single_value(is_locked, False)
    query.must_match_single_value(is_outlier, True)
    query.must_match_timestamp("timestamp", gte=min_timestamp)

    query.must_not_match_single_value("actionType", ACTION_TYPE_DONT_OPTIMIZE)

    query.add_aggregation(agg_name="apIds",
                          field="generalInfo.apId",
                          agg_type=ESQuery.TERMS)

    return query.get_query()


def query_get_multiple_documents_from_list(id_list):
    """
    This query gets a list of documents by their IDs
    :param list id_list:
    :return dictionary query:
    """
    query = ESQuery()
    query.should_match_multiple_values("_id", id_list)

    return query.get_query()


def delete_multiple_documents_from_list(id_list):
    """
    This query deletes a list of APs in ES
    :param list id_list:
    :return dictionary query:
    """
    query = ESQuery()
    query.must_match_multiple_values("_id", id_list)

    return query.get_query(include_size=False)


def query_params_from_object(serial_number, param_list):
    """
    This query returns the values of fields in the object
    :param serial_number:
    :param param_list:
    :return:
    """
    serial_number = str(serial_number).lower()

    query = ESQuery()
    query.must_match_single_value("generalInfo.apId", serial_number)

    for param in param_list:
        query.add_aggregation(agg_name=param,
                              field=param,
                              agg_type=ESQuery.TERMS,
                              size=5)

    return query.get_query()


def query_hosts_rssi_for_ap(serial_number, min_timestamp, max_timestamp):
    """
    Querying by this order:
    1. StaInfo.SignalStrength
    2. StaInfo.StaMacAddress

    :param string serial_number:
    :param string min_timestamp:
    :param string max_timestamp:
    :return dictionary query: The query for elastic search
    """
    serial_number = str(serial_number).lower()

    query = ESQuery()
    query.must_match_single_value("apId", serial_number)
    query.must_match_timestamp("@timestamp", gte=min_timestamp, lte=max_timestamp)

    query.should_match_single_value("_type", AP_DATA_STA_INFO_DOC_TYPE)
    query.should_match_single_value("_type", AP_DATA_TOTAL_STA_INFO_DOC_TYPE)
    query.should_match_single_value("_type", AP_DATA_USAGE_DOC_TYPE)

    query.add_aggregation(agg_name="band",
                          field="FrequencyBand",
                          agg_type=ESQuery.TERMS,
                          size=10,
                          )
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="commonRateSet",
                              field="StaInfo.CommonRateSet",
                              agg_type=ESQuery.TERMS,
                              size=20,
                              )
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="ssid",
                              field="NetworkUsage.SSID",
                              agg_type=ESQuery.TERMS,
                              size=20,
                              )
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="signalStrength",
                              field="StaInfo.SignalStrength",
                              agg_type=ESQuery.TERMS,
                              size=10,
                              )
    query.add_sub_aggregation(top_agg_name=["band", "signalStrength"],
                              sub_agg_name="macAddress",
                              field="StaInfo.StaMacAddress",
                              agg_type=ESQuery.CARDINALITY
                              )
    return query.get_query()


def query_cost_metric_params_for_ap(serial_number, min_timestamp, max_timestamp):
    """
    Querying by this order:
    1. StaInfo.TotalTxFailuresDiff
    2. StaInfo.TotalRxDecryptFailuresDiff
    3. APInterface.RF.CountersInfo.TxRetransDiff
    3. APInterface.RF.CountersInfo.TxRetransDiff
    3. APInterface.RF.CountersInfo.TxRetransDiff

    :param string serial_number:
    :param string min_timestamp:
    :param string max_timestamp:
    :return dictionary query: The query for elastic search
    """
    # Make sure serial number is not in capital letters
    serial_number = str(serial_number).lower()

    query = ESQuery()
    query.must_match_single_value("apId", serial_number)
    query.must_match_timestamp("@timestamp", gte=min_timestamp, lte=max_timestamp)

    query.should_match_single_value("_type", AP_DATA_STA_INFO_DOC_TYPE)
    query.should_match_single_value("_type", AP_DATA_INTERFACE_DOC_TYPE)

    query.add_aggregation(agg_name="band",
                          field="FrequencyBand",
                          agg_type=ESQuery.TERMS,
                          size=10,
                          )
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="txErrors",
                              field="StaInfo.TotalTxFailuresDiff",
                              agg_type=ESQuery.SUM
                              )
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="rxErrors",
                              field="StaInfo.TotalRxDecryptFailuresDiff",
                              agg_type=ESQuery.SUM
                              )
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="countersTxErrors",
                              field="APInterface.RF.CountersInfo.TxErrorDiff",
                              agg_type=ESQuery.SUM
                              )
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="countersRxErrors",
                              field="APInterface.RF.CountersInfo.RxErrorDiff",
                              agg_type=ESQuery.SUM
                              )
    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="countersTxRetrans",
                              field="APInterface.RF.CountersInfo.TxRetransDiff",
                              agg_type=ESQuery.SUM
                              )

    return query.get_query()


def query_alternate_interfaces(serial_number, min_timestamp, max_timestamp):
    """
    This query returns an aggregation of all active serial numbers in ES
    :param string serial_number: The serial number of the unit
    :param string min_timestamp: minimal timestamp to query
    :param string max_timestamp: maximal timestamp to query
    :return dictionary query:
    """
    serial_number = str(serial_number).lower()

    query = ESQuery()
    query.must_match_single_value("_type", AP_DATA_ALTERNATE_INTERFACE_DOC_TYPE)
    query.must_match_single_value("apId", serial_number)
    query.must_match_timestamp("@timestamp", gte=min_timestamp, lte=max_timestamp)

    query.add_aggregation(agg_name="band",
                          field="frequencyBand",
                          agg_type=ESQuery.TERMS)

    query.add_sub_aggregation(top_agg_name="band",
                              sub_agg_name="bssid",
                              field="AlternateInterface.BSSID",
                              agg_type=ESQuery.TERMS)

    query.add_sub_aggregation(top_agg_name=["band", "bssid"],
                              sub_agg_name="ssid",
                              field="AlternateInterface.SSID",
                              agg_type=ESQuery.TERMS)

    return query.get_query()


def query_get_all_aps_for_profile_name(profile_name, sp_id):

    query = ESQuery()
    query.must_match_single_value("profileName", profile_name)
    query.must_match_single_value("spId", sp_id)

    query.add_aggregation(agg_name="apId",
                          field="generalInfo.apId",
                          agg_type=ESQuery.TERMS,
                          )

    return query.get_query(agg_size=0)


def query_get_all_aps_aggr_by_profile_name(ap_list=None):

    query = ESQuery()

    if ap_list:
        ap_list = [ap.lower() for ap in ap_list]
        query.must_match_multiple_values("generalInfo.apId", ap_list)

    query.add_aggregation(agg_name="spId",
                          field="spId",
                          agg_type=ESQuery.TERMS,
                          )
    query.add_sub_aggregation(top_agg_name="spId",
                              sub_agg_name="profileName",
                              field="profileName",
                              agg_type=ESQuery.TERMS)

    query.add_sub_aggregation(top_agg_name=["spId", "profileName"],
                              sub_agg_name="apId",
                              field="generalInfo.apId",
                              agg_type=ESQuery.TERMS)

    return query.get_query()


def query_get_all_bssids_by_ap_id_list(band, min_timestamp, max_timestamp, ap_list=None, bssid_list=None):

    query = ESQuery()
    query.must_match_timestamp("@timestamp", gte=min_timestamp, lte=max_timestamp)
    query.must_match_single_value("FrequencyBand", band)

    if ap_list:
        ap_list = [ap.lower() for ap in ap_list]
        query.should_match_multiple_values("apId", ap_list)

    if bssid_list:
        query.should_match_multiple_values("AlternateInterface.BSSID", bssid_list)
        query.should_match_multiple_values("APInterface.RF.BSSID", bssid_list)

    query.add_aggregation(agg_name="apId",
                          field="apId",
                          agg_type=ESQuery.TERMS,
                          )

    query.add_sub_aggregation(top_agg_name="apId",
                              sub_agg_name="alternateBSSID",
                              field="AlternateInterface.BSSID",
                              agg_type=ESQuery.TERMS)

    query.add_sub_aggregation(top_agg_name="apId",
                              sub_agg_name="bssid",
                              field="APInterface.RF.BSSID",
                              agg_type=ESQuery.TERMS,
                              )
    return query.get_query()


def query_managed_neighbors_histogram(min_timestamp, max_timestamp, interval, ap_list=None, bssid_list=None):

    query = ESQuery()
    query.must_match_single_value("_type", "Neighbors")
    query.must_match_timestamp("@timestamp", gte=min_timestamp, lte=max_timestamp)

    if ap_list:
        ap_list = [ap.lower() for ap in ap_list]
        query.must_match_multiple_values("apId", ap_list)
    if bssid_list:
        query.must_match_multiple_values("Neighbors.BSSID", bssid_list)

    query.add_histogram(hist_name="timestamp",
                        field="@timestamp",
                        interval=ESInterval(interval, ESInterval.MINUTES).get()
                        )

    query.add_sub_aggregation(top_agg_name="timestamp",
                              sub_agg_name="apId",
                              field="apId",
                              agg_type=ESQuery.TERMS)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId"],
                              sub_agg_name="frequency",
                              field="FrequencyBand",
                              agg_type=ESQuery.TERMS)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId", "frequency"],
                              sub_agg_name="bssid",
                              field="Neighbors.BSSID",
                              agg_type=ESQuery.TERMS)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId", "frequency", "bssid"],
                              sub_agg_name="rssi",
                              field="Neighbors.RSSI",
                              agg_type=ESQuery.AVERAGE)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId", "frequency", "bssid"],
                              sub_agg_name="noise",
                              field="Neighbors.Noise",
                              agg_type=ESQuery.AVERAGE)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId", "frequency", "bssid"],
                              sub_agg_name="SNR",
                              field="Neighbors.SNR",
                              agg_type=ESQuery.AVERAGE)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId", "frequency", "bssid"],
                              sub_agg_name="channel",
                              field="Neighbors.Channel",
                              agg_type=ESQuery.TERMS)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId", "frequency", "bssid"],
                              sub_agg_name="SSID",
                              field="Neighbors.SSID",
                              agg_type=ESQuery.TERMS)

    return query.get_query()


def query_ping_info_histogram(serial_number_list, min_timestamp, max_timestamp, interval):
    """

    :param list serial_number_list:
    :param string min_timestamp:
    :param string max_timestamp:
    :param int interval:
    :return dictionary query: The query for elastic search
    """
    # Make sure serial number is not in capital letters
    serial_number_list = [str(serial_number).lower() for serial_number in serial_number_list]

    query = ESQuery()
    query.must_match_multiple_values("apId", serial_number_list)
    query.must_match_timestamp("@timestamp", gte=min_timestamp, lte=max_timestamp)

    query.add_histogram(hist_name="timestamp",
                        field="@timestamp",
                        interval=ESInterval(interval, ESInterval.MINUTES).get()
                        )

    query.add_sub_aggregation(top_agg_name="timestamp",
                              sub_agg_name="apId",
                              field="apId",
                              agg_type=ESQuery.TERMS
                              )

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId"],
                              sub_agg_name="Band",
                              field="FrequencyBand",
                              agg_type=ESQuery.TERMS)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId", "Band"],
                              sub_agg_name="AvgRoundTripTime",
                              field="PingInfo.AvgRoundTripTime",
                              agg_type=ESQuery.AVERAGE)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId", "Band"],
                              sub_agg_name="MaxPacketLossPercent",
                              field="PingInfo.PacketLossPercent",
                              agg_type=ESQuery.MAX)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId", "Band"],
                              sub_agg_name="AvgJitter",
                              field="PingInfo.AvgJitter",
                              agg_type=ESQuery.AVERAGE)

    return query.get_query()


def query_mos_average_histogram(serial_number_list, min_timestamp, max_timestamp, interval):
    """
    :param list serial_number_list:
    :param string min_timestamp:
    :param string max_timestamp:
    :param int interval:
    :return dictionary query: The query for elastic search
    """
    # Make sure serial number is not in capital letters
    serial_number_list = [str(serial_number).lower() for serial_number in serial_number_list]

    query = ESQuery()
    query.must_match_multiple_values("apId", serial_number_list)
    query.must_match_timestamp("@timestamp", gte=min_timestamp, lte=max_timestamp)
    query.must_match_single_value("_type", AP_DATA_PING_INFO_DOC_TYPE)

    query.add_histogram(hist_name="timestamp",
                        field="@timestamp",
                        interval=ESInterval(interval, ESInterval.MINUTES).get()
                        )

    query.add_sub_aggregation(top_agg_name="timestamp",
                              sub_agg_name="apId",
                              field="apId",
                              agg_type=ESQuery.TERMS)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId"],
                              sub_agg_name="Band",
                              field="FrequencyBand",
                              agg_type=ESQuery.TERMS)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId", "Band"],
                              sub_agg_name="voiceReadiness",
                              field="PingInfo.MOS",
                              agg_type=ESQuery.AVERAGE
                              )
    return query.get_query()

# def query_get_multiple_aps_by_lock_status(id_list, band, is_locked):
#     """
#     This query gets a list of documents by their IDs
#     :param list id_list:
#     :return dictionary query:
#     """
#     query = ESQuery()
#     query.should_match_multiple_values("_id", id_list)
#     query.must_match_single_value("")
#
#     return query.get_query()


def query_throughput_histogram(serial_number_list, min_timestamp, max_timestamp, interval):
    """
    :param list serial_number_list:
    :param string min_timestamp:
    :param string max_timestamp:
    :param int interval:
    :return dictionary query: The query for elastic search
    """
    # Make sure serial number is not in capital letters
    serial_number_list = [str(serial_number).lower() for serial_number in serial_number_list]

    query = ESQuery()
    query.must_match_multiple_values("apId", serial_number_list)
    query.must_match_timestamp("@timestamp", gte=min_timestamp, lte=max_timestamp)
    query.must_match_single_value("_type", AP_DATA_INFO_DOC_TYPE)

    query.add_histogram(hist_name="timestamp",
                        field="@timestamp",
                        interval=ESInterval(interval, ESInterval.MINUTES).get()
                        )

    query.add_sub_aggregation(top_agg_name="timestamp",
                              sub_agg_name="apId",
                              field="apId",
                              agg_type=ESQuery.TERMS)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId"],
                              sub_agg_name="UplinkTotalBytes",
                              field="APInfo.WANDevice.UplinkTotalBytes",
                              agg_type=ESQuery.SUM
                              )

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId"],
                              sub_agg_name="DownlinkTotalBytes",
                              field="APInfo.WANDevice.DownlinkTotalBytes",
                              agg_type=ESQuery.SUM
                              )

    return query.get_query()


def query_ap_interface_histogram(serial_number_list, min_timestamp, max_timestamp, interval):
    """
    :param list serial_number_list:
    :param string min_timestamp:
    :param string max_timestamp:
    :param int interval:
    :return dictionary query: The query for elastic search
    """
    # Make sure serial number is not in capital letters
    serial_number_list = [str(serial_number).lower() for serial_number in serial_number_list]

    query = ESQuery()
    query.must_match_multiple_values("apId", serial_number_list)
    query.must_match_timestamp("@timestamp", gte=min_timestamp, lte=max_timestamp)
    query.must_match_single_value("_type", AP_DATA_INTERFACE_DOC_TYPE)

    query.add_histogram(hist_name="timestamp",
                        field="@timestamp",
                        interval=ESInterval(interval, ESInterval.MINUTES).get()
                        )

    query.add_sub_aggregation(top_agg_name="timestamp",
                              sub_agg_name="apId",
                              field="apId",
                              agg_type=ESQuery.TERMS)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId"],
                              sub_agg_name="Band",
                              field="FrequencyBand",
                              agg_type=ESQuery.TERMS)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId", "Band"],
                              sub_agg_name="RF.Noise",
                              field="APInterface.RF.Noise",
                              agg_type=ESQuery.AVERAGE
                              )

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId", "Band"],
                              sub_agg_name="RF.UplinkErrors",
                              field="APInterface.RF.UplinkErrors",
                              agg_type=ESQuery.SUM
                              )

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId", "Band"],
                              sub_agg_name="RF.DownlinkErrors",
                              field="APInterface.RF.DownlinkErrors",
                              agg_type=ESQuery.SUM
                              )
    return query.get_query()


def query_ap_health_histogram(serial_number_list, min_timestamp, max_timestamp, interval):
    """
    :param list serial_number_list:
    :param string min_timestamp:
    :param string max_timestamp:
    :param int interval:
    :return dictionary query: The query for elastic search
    """
    # Make sure serial number is not in capital letters
    serial_number_list = [str(serial_number).lower() for serial_number in serial_number_list]

    query = ESQuery()
    query.must_match_multiple_values("apId", serial_number_list)
    query.must_match_timestamp("@timestamp", gte=min_timestamp, lte=max_timestamp)
    #query.must_match_single_value("_type", AP_DATA_INFO_DOC_TYPE)
    #query.must_match_single_value("APInfo.UpTime", "*")
    query.add_filter_query(filter_query="_type: %s AND APInfo.UpTime: * " % AP_DATA_INFO_DOC_TYPE)

    query.add_histogram(hist_name="timestamp",
                        field="@timestamp",
                        interval=ESInterval(interval, ESInterval.MINUTES).get()
                        )

    query.add_sub_aggregation(top_agg_name="timestamp",
                              sub_agg_name="apId",
                              field="apId",
                              agg_type=ESQuery.TERMS)

    query.add_sub_aggregation(top_agg_name=["timestamp", "apId"],
                              sub_agg_name="isAlive",
                              field="@timestamp",
                              agg_type=ESQuery.CARDINALITY)

    return query.get_query()


