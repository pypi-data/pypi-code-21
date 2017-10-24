import hashlib
import json
import logging

import pydash as _
import requests
from django.conf import settings
from django.core.validators import RegexValidator

validate_mobile = RegexValidator(r'1[34578][0-9]{9}', '无效的手机号码，应该为1开头的11位数字')  # todo 是否抽出为专门的validator文件


def _sign(params, sms_user, sms_key):
    params.pop('smsKey', None)
    params.pop('signature', None)
    params['smsUser'] = sms_user

    pairs = sorted(list(params.items()))
    param_str = '&'.join("{}={}".format(*pair) for pair in pairs)

    sign_str = sms_key + '&' + param_str + '&' + sms_key
    signature = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    params['signature'] = signature

    params['smsUser'] = sms_user
    return params


# send(phone, template_id, var_name_in_template_a=1, var_name_in_template_a=2)
def send(phone, template_id, msg_type=0, **kwargs):
    params = {
        'templateId': template_id,
        'msgType': msg_type,
        'phone': phone,
        'vars': json.dumps(kwargs),
    }
    logging.info("sendcloud_send_sms: %s %s", phone, params)
    params = _sign(params, _.get(settings, 'SENDCLOUD.sms.sms_user'), _.get(settings, 'SENDCLOUD.sms.sms_key'))

    try:
        validate_mobile(phone)
        if _.get(settings, 'SENDCLOUD.sms.muted'):
            ret = {"statusCode": 200}
        else:
            resp = requests.post('http://www.sendcloud.net/smsapi/send', data=params)
            ret = resp.json()
    except Exception:
        ret = {'statusCode': -1}

    if ret.get('statusCode') != 200:
        logging.warning("sendcloud_send_sms error: params=%s ret=%s", params, ret)
    return ret
