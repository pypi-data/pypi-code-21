from http import HTTPStatus
from flask import Blueprint, request
import logging

from magen_rest_apis.rest_server_apis import RestServerApis
from ks.ks_api.key_service_api import key_service_api
from magen_logger.logger_config import LogDefaults

__author__ = "paulq@cisco.com"
__maintainer__ = "Alena Lifar"
__email__ = "alifar@cisco.com"
__copyright__ = "Copyright(c) 2017, Cisco Systems, Inc."
__version__ = "0.4.1"
__status__ = "alpha"

# Global default to local keyserver
ks_type = 'local'

key_service_bp = Blueprint("key_service_bp", __name__)
key_service_bp_v3 = Blueprint("key_service_bp_v3", __name__)

default_key_format = 'json'


@key_service_bp_v3.route('/', methods=['GET'])
@key_service_bp.route('/', methods=['GET'])
def ks_welcome():
    """Simple GET that indetifies key service"""
    return "Welcome to Magen Key Service"


@key_service_bp_v3.route('/check/', methods=["GET"])
@key_service_bp.route('/check/', methods=["GET"])
def health_check():
    """health check used by SLB"""
    return "Check success"


# V3 APIS


# Generate multiple new keys
# {
#   "assets": [
#     {
#       "asset": {
#         "asset_id": ID (String)
#       }
#     },
#     {
#       "asset": {
#         "asset_id": ID (String)
#       }
#     }
#   ],
#   "format" : "json"|"jwt"
#   "ks_type" : "awskms" | "local"
# }


@key_service_bp_v3.route('/asset_keys/assets/', methods=['POST'])
def generate_new_keys_v3():
    """ 
    Create new multiple keys 

    :return: http response with created key info 
    :rtype: json 
    """
    logger = logging.getLogger(LogDefaults.default_log_name)

    success, created_keys = key_service_api.generate_new_asset_keys(request.json)

    logger.debug('key info is %s', created_keys)

    http_response = RestServerApis.respond(HTTPStatus.OK, "create new keys", created_keys) if success \
        else RestServerApis.respond(HTTPStatus.BAD_REQUEST, "create new keys", created_keys)

    http_response.headers['location'] = '/magen/ks/v3/asset_keys/assets/'
    return http_response


# Generate new key
# {
#       "asset": {
#         "asset_id": ID
#       },
#       "format" : "jwt" | "json"
#       "ks_type" : "local" | "awskms"
# }

@key_service_bp_v3.route('/asset_keys/assets/asset/', methods=['POST'])
def generate_new_key_v3():
    """ 
    Create new single key 

    :return: http response with created key info 
    :rtype: json 
    """
    logger = logging.getLogger(LogDefaults.default_log_name)

    success, created_key = key_service_api.generate_new_asset_key(request.json)
    logger.debug("key info is %s", created_key)

    http_response = RestServerApis.respond(HTTPStatus.OK, "create new key", created_key) if success \
        else RestServerApis.respond(HTTPStatus.BAD_REQUEST, "create new key", created_key)

    http_response.headers['location'] = '/magen/ks/v3/asset_keys/assets/asset/'
    return http_response


@key_service_bp_v3.route('/asset_keys/assets/', methods=['GET'])
def get_asset_keys_v3():
    """ 
    Retrieve existing keys via asset ID 
    url: http://localhost:5010/magen/ks/v3/asset_keys/assets/?asset_id=<ID>&asset_id=<ID>/ 

    :return: http response with keys info 
    :rtype: json 
    """
    logger = logging.getLogger(LogDefaults.default_log_name)

    asset_id_list = list()

    for asset_id in request.args.getlist('asset_id'):
        asset_id_list.append(dict(asset_id=asset_id))
    asset_id_dict = dict(assets=asset_id_list)

    asset_id_dict['format'] = request.args.get('format', default_key_format)

    logger.debug('list of asset ids %s', asset_id_dict)

    success, retrieved_keys = key_service_api.retrieve_asset_keys(asset_id_dict)

    http_response = RestServerApis.respond(HTTPStatus.OK, "requested keying material", retrieved_keys) if success \
        else RestServerApis.respond(HTTPStatus.BAD_REQUEST, "requested keying material", retrieved_keys)

    http_response.headers['location'] = '/magen/ks/v3/asset_keys/assets/'
    return http_response


@key_service_bp_v3.route('/asset_keys/assets/asset/<asset_id>/', methods=['GET'])
def get_asset_key_v3(asset_id):
    """ 
    Retrieve single key via asset ID 
    url - http://localhost:5010/magen/ks/v3/asset_keys/assets/asset/<asset_id>/ 

    :param asset_id: asset id 
    :type asset_id: uuid str 

    :return: http response with key info 
    :rtype: json 
    """

    asset_id_dict = dict(
        asset_id=asset_id,
        format=request.args.get('format', default_key_format)
    )
    success, retrieved_key = key_service_api.retrieve_asset_key(asset_id_dict)

    http_response = RestServerApis.respond(HTTPStatus.OK, "key details", retrieved_key) if success \
        else RestServerApis.respond(HTTPStatus.BAD_REQUEST, "key details", retrieved_key)
    http_response.headers['location'] = '/magen/ks/v3/asset_keys/assets/asset/<asset_id>/'
    return http_response


@key_service_bp_v3.route('/asset_keys/keys/', methods=['DELETE'])
def delete_asset_keys_v3():
    """
    Delete multiple keys via key ID

    :return: http response with keys info
    :rtype: json
    """
    logger = logging.getLogger(LogDefaults.default_log_name)
    key_id_list = []

    for kid in request.args.getlist('key_id'):
        key_id_list.append(dict(key=dict(
            key_id=kid
        )))

    keys_del_dict = dict(
        keys=key_id_list,
        format=request.args.get('format', default_key_format)
    )

    success, deleted_keys = key_service_api.delete_asset_keys(keys_del_dict)

    logger.debug("key info is %s", deleted_keys)

    http_response = RestServerApis.respond(HTTPStatus.OK, "delete keys", deleted_keys) if success \
        else RestServerApis.respond(HTTPStatus.BAD_REQUEST, "delete keys", deleted_keys)
    http_response.headers['location'] = '/magen/ks/v3/asset_keys/keys/'
    return http_response


@key_service_bp_v3.route('/asset_keys/keys/key/<key_id>/', methods=['DELETE'])
def delete_asset_key_v3(key_id):
    """
    Delete single key

    :param key_id: id of a key to delete
    :type key_id: uuid str

    :return: http response with key info
    :rtype: json
    """

    logger = logging.getLogger(LogDefaults.default_log_name)
    key_to_del = dict(
        key=dict(key_id=key_id),
        format=request.args.get('format', default_key_format)
    )
    success, deleted_key = key_service_api.delete_asset_key(key_to_del)

    http_response = RestServerApis.respond(HTTPStatus.OK, "delete key", deleted_key) if success \
        else RestServerApis.respond(HTTPStatus.BAD_REQUEST, "delete key", deleted_key)
    http_response.headers['location'] = '/magen/ks/v3/asset_keys/keys/key/'
    return http_response


@key_service_bp_v3.route('/asset_keys/keys/', methods=['PUT'])
def change_state_keys_v3():
    """
    Change state for multiple keys

    :return: http response with keys info
    :rtype: json
    """
    logger = logging.getLogger(LogDefaults.default_log_name)

    success, updated_keys = key_service_api.update_asset_keys(request.json)
    logger.debug("key info is %s", updated_keys)

    http_response = RestServerApis.respond(HTTPStatus.OK, "updated keys", updated_keys) if success \
        else RestServerApis.respond(HTTPStatus.BAD_REQUEST, "updated keys", updated_keys)
    http_response.headers['location'] = '/magen/ks/v3/asset_keys/keys/'
    return http_response


@key_service_bp_v3.route('/asset_keys/keys/key/', methods=['PUT'])
def change_state_key_v3():
    """
    Change state for a single key

    :return: http response with key info
    :rtype: json
    """
    success, updated_key = key_service_api.update_asset_key(request.json)

    http_response = RestServerApis.respond(HTTPStatus.OK, "updated key", updated_key) if success \
        else RestServerApis.respond(HTTPStatus.BAD_REQUEST, "updated key", updated_key)
    http_response.headers['location'] = '/magen/ks/v3/asset_keys/keys/key/'
    return http_response


@key_service_bp_v3.route('/asset_keys/keys/', methods=['GET'])
def return_keys_details_v3():
    """
    GET information about keys, by key_id

    :return: http response with keys info
    :rtype: json
    """
    logger = logging.getLogger(LogDefaults.default_log_name)
    key_id_list = []

    for kid in request.args.getlist('key_id'):
        key_id_list.append(dict(key_id=kid))
    key_id_dict = dict(
        keys=key_id_list,
        format=request.args.get('format', default_key_format)
    )
    logger.debug("list of asset ids %s", key_id_dict)

    success, keys_info = key_service_api.get_asset_keys_info(key_id_dict)

    http_response = RestServerApis.respond(HTTPStatus.OK, "key details", keys_info) if success \
        else RestServerApis.respond(HTTPStatus.BAD_REQUEST, "key details", keys_info)
    http_response.headers['location'] = '/magen/ks/v3/asset_keys/keys/key/'
    return http_response


@key_service_bp_v3.route('/asset_keys/keys/key/<key_id>/', methods=['GET'])
def retrun_key_details_v3(key_id):
    """
    Get detail about a single key

    :param key_id: id of a single key
    :type key_id: uuid str

    :return: http response with keys info
    :rtype: json
    """
    logger = logging.getLogger(LogDefaults.default_log_name)
    key_id_dict = dict(
        key=dict(key_id=key_id),
        format=request.args.get('format', default_key_format)
    )
    success, key_info = key_service_api.get_asset_key_info(key_id_dict)
    logger.debug("Returning single key")

    http_response = RestServerApis.respond(HTTPStatus.OK, "key details", key_info) if success \
        else RestServerApis.respond(HTTPStatus.BAD_REQUEST, "key details", str(key_info))
    http_response.headers['location'] = '/magen/ks/v3/asset_keys/keys/key/'
    return http_response


# ALL OLDER URIs deprecated
@key_service_bp_v3.route('/ks/reset/', methods=['GET'])
@key_service_bp.route('/ks/reset/', methods=['GET'])
def reset_ks():
    """
    USED FOR TEST ONLY: clean up all records and start again

    :rtype: str
    """
    result = key_service_api.reset()
    return result


@key_service_bp_v3.route('/logging_level/<level>/', methods=["POST", "PUT"])
@key_service_bp.route('/logging_level/<level>/', methods=["POST", "PUT"])
def set_logging_level(level):
    """
    Set logging level

    :param level: level of a logger
    :type level: str

    :return: http response
    :rtype: json
    """
    try:
        do_set_logging_level(level)

        return RestServerApis.respond(
            HTTPStatus.OK,
            "set_logging_level",
            dict(
                success=True,
                cause='level set to {}'.format(level)
            )
        )
    
    except ValueError as e:
        return RestServerApis.respond(
            HTTPStatus.INTERNAL_SERVER_ERROR, "set_logging_level", {
                "success": False, "cause": e.args[0]})

def do_set_logging_level(level):
    logger = logging.getLogger(LogDefaults.default_log_name)
    level = str(level).upper()

    logger.setLevel(level=level)
    requests_logger = logging.getLogger("requests")
    requests_logger.setLevel(level=level)
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.setLevel(level=level)
    return True
