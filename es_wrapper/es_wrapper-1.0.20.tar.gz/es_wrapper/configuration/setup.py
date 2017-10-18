from es_wrapper.tools.es_adapter import ESAdapter
# from es_wrapper.configuration.mappings import LOGGER_INDEX_MAPPING, AP_DATA_INDEX_MAPPING, WLC_INDEX_MAPPING, \
#     OPT_ACTION_INDEX_MAPPING
# from es_wrapper.configuration.parameters import ES_LOGGER_GET_INDEX, ES_WLC_GET_INDEX, ES_AP_DATA_GET_INDEX, ES_SERVER_URL, \
#     ES_ACTIONS_INDEX
from es_wrapper.tools.infra import create_index_template


# def create_project_templates():
#     """
#     This method creates the needed ES templates for elastic search
#     """
#     # Create all index templates
#     template_list = [create_index_template(ES_LOGGER_GET_INDEX, LOGGER_INDEX_MAPPING),
#                      create_index_template(ES_WLC_GET_INDEX, WLC_INDEX_MAPPING),
#                      create_index_template(ES_AP_DATA_GET_INDEX, AP_DATA_INDEX_MAPPING),
#                      create_index_template(ES_ACTIONS_INDEX, OPT_ACTION_INDEX_MAPPING)]
#
#     # Save mappings in ES
#     ESAdapter(ES_SERVER_URL).save_template_list_in_es(template_list)


def save_template_in_es(es_url, mapping_dict):
    """
    This method saves a mapping in ES
    :param str es_url: The URL of elastic search to save template in
    :param dict mapping_dict: {TEMPLATE_NAME, MAPPING}
    :return bool: Operation status
    :raises Exception: On false
    """
    template_list = []
    for template_name, mapping in mapping_dict.items():
        template_list.append(create_index_template(template_name, mapping))

    if not ESAdapter(es_url).save_template_list_in_es(template_list):
        raise Exception("Couldn't save templates for %s in %s" % (es_url, mapping_dict.keys()))

    return True
