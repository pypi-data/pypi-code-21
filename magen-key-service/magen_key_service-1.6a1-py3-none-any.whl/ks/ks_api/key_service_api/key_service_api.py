from ks.ks_api.kms_apis import keywrapper
from ks.ks_api.kms_apis.ks_local import KsLocal
from ks.ks_api.kms_apis.ks_super import KeyServerBase

from ks.ks_api.kms_apis.ks_aws import KsAws
from ks.settings import mongo_settings

import logging

from magen_logger.logger_config import LogDefaults

__author__ = "paulq@cisco.com"
__maintainer__ = "Alena Lifar"
__email__ = "alifar@cisco.com"
__copyright__ = "Copyright(c) 2017, Cisco Systems, Inc."
__version__ = "0.4.1"
__status__ = "alpha"

local_instance = KsLocal.get_instance()
jwt_format = 'jwt'


def reset():
    collection = mongo_settings.MongoSettings().collection
    collection.drop()
    return "ks reset\n"


def _check_key_type(key_id: str):
    """
    internal helper method to retrieve the type of key
    (ie what type of key server generated it)

    :param key_id: key id
    :type key_id: str

    :return: key server type that generated key
    :rtype: str
    """
    collection = mongo_settings.MongoSettings().collection
    found_key = collection.find_one({"key_id": key_id})
    if found_key:
        if found_key['key_server'] == 'awskms':
            return 'awskms'
        elif found_key['key_server'] == 'local':
            return 'local'
        return 'unknown key type for key id ' + key_id
    return "key " + str(key_id) + " not found"


def _create_new_key(ks_type: str, asset_id: str):
    """
    Performs calls for new key creation depending on ks_type

    :param ks_type: type of key service: aws or local
    :type ks_type: str

    :param asset_id: id of an asset
    :type asset_id: uuid str

    :return: status and key/error info
    :rtype: tuple
    """
    if ks_type == 'awskms':
        kms_instance = KsAws.get_instance()
        return kms_instance.generate_new_key(asset_id)
    elif ks_type == 'local':
        # kms_instance = KsLocal.get_instance()
        return local_instance.generate_new_key(asset_id)
    return False, "invalid key server type, or type not specified in POST"


def _validate_key_format(seed: str, actual_format: str):
    return seed if actual_format == seed else None


def generate_new_asset_keys(assets: dict):
    """
    create new keys for multiple provided asset ID

    :param assets: collection of asset ids
    :type assets: dict

    :return: status and keys collection
    :rtype: tuple
    """

    logger = logging.getLogger(LogDefaults.default_log_name)
    new_keys = dict(keys=list())

    success = False

    key_format = _validate_key_format(jwt_format, assets.get('format', ''))
    logger.debug("key format: %s",key_format)

    for asset in assets.get('assets', []):
        success, new_key = _create_new_key(assets.get('ks_type', ''), asset['asset']['asset_id'])
        new_keys['keys'].append(dict(key=new_key))

    return (success, keywrapper.jot_key(new_keys)) if key_format else (success, new_keys)


def generate_new_asset_key(asset: dict):
    """
    Create new key for an asset

    :param asset: asset info
    :type asset: dict

    :return: status and key info
    :rtype: tuple
    """
    key_format = _validate_key_format(jwt_format, asset.get('format', ''))

    success, new_key = _create_new_key(asset['ks_type'], asset['asset']['asset_id'])
    return (success, keywrapper.jot_key(new_key)) if key_format else (success, new_key)


def _construct_key(ks_type: str, asset_id: str):
    """
    Constructs key data depending on ks_type

    :param ks_type: key service type: aws or local
    :type ks_type: str

    :param asset_id: id of a given asset
    :type asset_id: str

    :return: status and key/error info
    :rtype: tuple
    """
    if ks_type == 'awskms':
        kms_instance = KsAws.get_instance()
        return kms_instance.construct_requested_key(asset_id)
    elif ks_type == 'local':
        kms_instance = KsLocal.get_instance()
        return local_instance.construct_requested_key(asset_id)
    return False, "invalid key server"


def retrieve_asset_keys(assets: dict):
    """
    Construct keys data for multiple assets

    :param assets: collection of assets
    :type assets: dict

    :return: status and keys collection
    :rtype: tuple
    """

    logger = logging.getLogger(LogDefaults.default_log_name)

    collection = mongo_settings.MongoSettings().collection

    multi_key_dict = dict(keys=list())
    success = False

    key_format = _validate_key_format(jwt_format, assets.get('format', ''))

    for asset in assets.get('assets', []):
        k = collection.find_one({"asset_id": asset['asset_id']})
        success, retrieved_key = _construct_key(k['key_server'], k)
        multi_key_dict['keys'].append(retrieved_key)
    if not multi_key_dict['keys']:
        msg = 'key not found for asset IDs: ' + str(assets)
        multi_key_dict = {'error': msg}
        success = False

    return (success, keywrapper.jot_key(multi_key_dict)) if key_format else (success, multi_key_dict)


def retrieve_asset_key(asset: dict):
    """
    Construct key data for a single asset

    :param asset: asset info
    :type asset: dict

    :return: status and key info
    :rtype: tuple
    """
    logger = logging.getLogger(LogDefaults.default_log_name)
    logger.debug("retrieving key for asset ID %s", asset['asset_id'])

    collection = mongo_settings.MongoSettings().collection
    key_format = _validate_key_format(jwt_format, asset.get('format', ''))

    k = collection.find_one({"asset_id": str(asset['asset_id'])})
    if not k:
        msg = 'key not found for asset ID: ' + str(asset['asset_id'])
        retrieved_key = {'error': msg}
        success = False
    else:
        success, retrieved_key = _construct_key(k['key_server'], k)
        logger.debug("success: %s retrieved_key: %s", success, retrieved_key)
        if not retrieved_key:
            msg = 'key not found for asset ID: ' + str(asset['asset_id'])
            retrieved_key = {'error': msg}
            success = False
    return (success, keywrapper.jot_key(retrieved_key)) if key_format else (success, retrieved_key)


def delete_asset_keys(keys_to_del: dict):
    """
    Delete multiple keys

    :param keys_to_del: collection of keys
    :type keys_to_del: dict

    :return: status and deletion info
    :rtype: tuple
    """

    logger = logging.getLogger(LogDefaults.default_log_name)

    deleted_keys = list()
    success = False

    key_format = _validate_key_format(jwt_format, keys_to_del.get('format', ''))

    for a in keys_to_del.get('keys', []):
        success, key_info = KeyServerBase.rm_key(a['key']['key_id'])
        deleted_keys.append(dict(key=key_info))
    if not deleted_keys:
        return success, "Invalid key data"
    return (success, keywrapper.jot_key(dict(keys=deleted_keys))) if key_format else (success, dict(keys=deleted_keys))


def delete_asset_key(key_to_del: dict):
    """
    Delete a single key

    :param key_to_del: key info
    :type key_to_del: dict

    :return: status and deletion info
    :rtype: tuple
    """
    logger = logging.getLogger(LogDefaults.default_log_name)
    logger.debug("Key to be deleted %s", key_to_del)

    key_format = _validate_key_format(jwt_format, key_to_del.get('format', ''))

    success, deleted_key = KeyServerBase.rm_key(key_to_del['key']['key_id'])

    return (success, keywrapper.jot_key(deleted_key)) if key_format else (success, deleted_key)


def update_asset_keys(keys_to_update: dict):
    """
    Update key state for given keys depending on information provided

    :param keys_to_update: collection of keys with new info
    :type keys_to_update: dict

    :return: status and updated key data
    :rtype: tuple
    """

    logger = logging.getLogger(LogDefaults.default_log_name)

    multi_key_dict = {'keys': []}
    key_format = _validate_key_format(jwt_format, keys_to_update.get('format', ''))
    success = False

    for k in keys_to_update.get('keys', []):
        success, updated_key = KeyServerBase.state_change(k['key']['key_id'], k['key']['active'])
        multi_key_dict['keys'].append(dict(key=updated_key))

    if not multi_key_dict['keys']:
        multi_key_dict['keys'] = "invalid key data"
    return (success, keywrapper.jot_key(multi_key_dict)) if key_format else (success, multi_key_dict)


def update_asset_key(key_to_update: dict):
    """
    Update key state for a given key depending on information provided

    :param key_to_update: key info
    :type key_to_update: dict

    :return: status and updated key info
    :rtype: tuple
    """

    logger = logging.getLogger(LogDefaults.default_log_name)

    key_format = _validate_key_format(jwt_format, key_to_update.get('format', ''))
    success, updated_key = KeyServerBase.state_change(key_to_update['key']['key_id'], key_to_update['key']['active'])

    logger.debug("updated key info: %s", str(updated_key))

    return (success, keywrapper.jot_key(updated_key)) if key_format else (success, updated_key)


def _get_key(ks_type: str, key_id: str):
    """
    Get key detailed info by id depending on ks_type

    :param ks_type: key service type: aws or local
    :type ks_type: str

    :param key_id: key id
    :type key_id: str

    :return: status and key/error info
    :rtype: tuple
    """
    if ks_type == 'awskms':
        kms_instance = KsAws.get_instance()
        return kms_instance.get_key_details(key_id)
    elif ks_type == 'local':
        # kms_instance = KsLocal.get_instance()
        return local_instance.get_key_details(key_id)
    return False, ks_type


def get_asset_keys_info(keys: dict):
    """
    Get detailed information for given keys

    :param keys: keys collection
    :type keys: dict

    :return: status and detailed information for given keys
    :rtype: tuple
    """

    logger = logging.getLogger(LogDefaults.default_log_name)

    keys_info = list()
    key_format = _validate_key_format(jwt_format, keys.get('format', ''))
    success = False

    for key in keys.get('keys', []):
        ks_type = _check_key_type(key['key_id'])
        success, key_details = _get_key(ks_type, key['key_id'])
        keys_info.append(key_details)

    return (success, keywrapper.jot_key(dict(keys=keys_info))) if key_format else (success, dict(keys=keys_info))


def get_asset_key_info(key: dict):
    """
    Get detailed information for a given key

    :param key: key info (must contain key id)
    :type key: dict

    :return: status and detailed key info
    :rtype: tuple
    """

    logger = logging.getLogger(LogDefaults.default_log_name)

    key_format = _validate_key_format(jwt_format, key.get('format', ''))
    ks_type = _check_key_type(key['key']['key_id'])
    success, key_details = _get_key(ks_type, key['key']['key_id'])

    logger.debug("Key details: %s", key_details)

    return (success, keywrapper.jot_key(key_details)) if key_format else (success, key_details)

