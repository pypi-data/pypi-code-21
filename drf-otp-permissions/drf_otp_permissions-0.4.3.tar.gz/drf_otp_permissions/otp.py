from __future__ import unicode_literals

import json
from datetime import datetime, timedelta
import time
import logging

from .encryptions import decrypt_message_with_file
from .encryptions import encrypt_message_with_file

logger = logging.getLogger(__name__)


def _str_dict(data):
    output_dict = {}
    for key, value in list(data.items()):
        if type(value) is unicode:
            string_value = value
        else:
            string_value = str(value)
        output_dict[str(key)] = string_value
    return output_dict


def _validate_due(datetime_object):
    logger.info(datetime_object)
    if datetime.utcnow() < datetime_object:
        return True
    return False


def create_otp(data, key_location):
    """
    Given data and key location, return OTP header for HTTP request
    :param data: dict. Data passed with the HTTP request
    :param key_location: str. Path to encryption key
    :return: str. Encryption of `data` and current time
    """
    datetime_object = datetime.utcnow()
    delta = timedelta(seconds=60)
    due = datetime_object + delta
    unix_time = time.mktime(due.timetuple())

    message_dict = {
        "data": json.loads(json.dumps(data)),
        "due": unix_time,
        "expiredBy" : due.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    message_json_str = json.dumps(message_dict)

    return encrypt_message_with_file(message_json_str, key_location)


def validate_otp(otp, data, key_location):
    """
    Given otp, data, and key location, validate if OTP is correct
    :param otp: str. Encryption of `data` and created time
    :param data: dict. Data passed with HTTP request
    :return: bool. True, if OTP is valid. Else, returns False.
    """
    if not otp:
        logger.info(type(otp))
        logger.info("empty otp was provided: %s" % str(otp))
        return False

    try:
        decrypted_string = decrypt_message_with_file(otp, key_location)
    except Exception as e:
        logger.error(str(e))
        logger.info("failed to decrypt %s" % otp)
        return False

    try:
        decrypted_message_dict = json.loads(decrypted_string)
    except Exception as e:
        logger.error(str(e))
        logger.info("failed to parse json from %s" % decrypted_string)
        return False

    decrypted_data = decrypted_message_dict.get("data", {})
    decrypted_data = _str_dict(decrypted_data)

    str_data = _str_dict(data)

    if decrypted_data != str_data:
        logger.info("decrypted_data does not equal to data")
        logger.info("decrypted_data = %s" % str(decrypted_data))
        logger.info("data = %s" % str(data))
        return False

    expired_by = decrypted_message_dict.get('expiredBy')
    logger.info(expired_by)

    if expired_by:
        datetime_object = datetime.strptime(expired_by, "%Y-%m-%dT%H:%M:%SZ")
        return _validate_due(datetime_object)

    decrypted_due = decrypted_message_dict.get('due')
    logger.info(decrypted_due)

    if decrypted_due:
        datetime_object = datetime.fromtimestamp(decrypted_due)
        return _validate_due(datetime_object)
    return False