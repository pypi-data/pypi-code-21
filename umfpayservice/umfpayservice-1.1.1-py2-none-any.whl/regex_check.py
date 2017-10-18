# coding=utf-8

from umfpayservice import error
import re

def check(key, value):
    '''
    校验键值
    '''
    regexs = get_regexs()
    if key in regexs:
        # 提取正则校验规则
        regex_str = regexs[key]
        regex_match = re.compile(regex_str).match(value)
        if regex_match is None:
            raise error.ParamsError("[请求参数校验] "
                                    "%s: 该字段正则校验不通过。regex_str: %s (%s: %s)"
                                    % (key, regex_str, key, value))
        return True
    #
    # else:
    #     raise error.ParamsError("[请求参数校验] "
    #                             "%s: 改字段不在校验字段列表中，请确认该字段名是否有误。(%s: %s)" % (key, key, value))


def get_regexs():
    return {
        # "service": "^[a-zA-Z0-9_]{1,32}$",
        # "charset": "^(UTF-8|GBK|GB2312|GB18030)$",
        "mer_id": "^[0-9]{1,8}$",
        # "sign_type": "^RSA$",
        # "version": "^(4.0|1.0)$",
        "media_type": "^(MOBILE|EMAIL|MERUSERID)$",
        "order_id": "^\S{1,32}$",
        "mer_date": "^[1-2][0-9]{7}$",
        "amount": "^[1-9][0-9]*$",
        "amt_type": "^RMB$",
        "expire_time": "^[0-9]{1,32}$",
        "ret_code": "^[0-9]+$",
        "trade_no": "^[0-9]{1,16}$",
        "pay_date": "^[1-2][0-9]{7}$",
        "settle_date": "^[1-2][0-9]{7}$",
        "error_code": "^[0-9]*$",
        "mer_check_date": "^[1-2][0-9]{7}$",
        "refund_amt": "^[1-9][0-9]*$",
        "refund_amount": "^[1-9][0-9]*$",
        "org_amount": "^[1-9][0-9]*$",
        "split_type": "^[1-2]{0,2}$",
        "is_success": "^(Y|N)$",
        "sub_mer_id": "^[0-9]*$",
        "req_date": "^[1-2][0-9]{7}$",
        "req_time": "^[0-9]{6}$",
        "birthday": "^[1-2][0-9]{7}$",
        "sex": "^(M|F)$",
        "contact_mobile": "^[0-9]{11}$",
        "fee_amount": "^(0|[1-9][0-9]*)$",
        "recv_account_type": "^[0-1]{2}$",
        "recv_bank_acc_pro": "^[0-1]{1}$",
        "recv_type": "^[0-1]$",
        "debit_pay_type": "^(1|2)$",
        "pay_category": "^01$",
        "split_category": "^(1|2|3)$",
        "push_type": "^(0|1|2|3)$",
        "order_type": "^(1|2)$",
        "sign": "^\S+$",
        # "res_format": "^\S+$",
        "goods_inf": "^\S+$",
        "token": "^\S+$",
        "trade_state": "^\S{1,32}$",
        "refund_no": "^\S{1,16}$",
        "refund_state": "^\S+$",
        "sub_order_id": "^\S{1,32}$",
        "refund_desc": "^\S{1,128}$",
        "valid_date": "^\S{1,256}$",
        "cvv2": "^\S{1,256}$",
        "mail_addr": "^\S{1,64}$",
        "contact_phone": "^\S+$",
        "finance_vou_no": "^\S{1,32}$",
        "purpose": "^\S+$",
        "prov_name": "^\S+$",
        "city_name": "^\S+$",
        "bank_brhname": "^\S+$",
        # "ret_url": "^\S*$",
        # "notify_url": "^\S*$",
        # "goods_id": "^\S*$",
        "media_id": "^\S+$",
        "mobile_id": "^\S{0,11}$",
        # "pay_type": "^\S*$",
        # "gate_id": "^\S*$",
        # "mer_priv": "^\S*$",
        # "user_ip": "^\S*$",
        # "expand": "^\S*$",
        # "ret_msg": "^\S*$",
        # "pay_seq": "^\S*$",
        # "bank_check_state": "^\S*$",
        # "product_id": "^\S*$",
        # "mer_trace": "^\S*$",
        # "split_data": "^\S*$",
        "card_id": "^\S{0,256}$",
        "pass_wd": "^\S{0,256}$",
        "identity_type": "^\S{0,256}$",
        "identity_code": "^\S{0,256}$",
        "card_holder": "^\S{0,256}$",
        "cust_name": "^\S{0,32}$",
        # "recv_account": "^\S*$",
        # "recv_user_name": "^\S*$",
        # "recv_gate_id": "^\S*$",
        "verify_code": "^\S{0,8}$",
        "mer_cust_id": "^\S{0,32}$",
        "usr_busi_agreement_id": "^\S{0,64}$",
        "usr_pay_agreement_id": "^\S{0,64}$",
        "identity_holder": "^\S{0,256}$",
        # "split_refund_list": "^\S*$",
        # "split_cmd": "^\S*$",
        # "settle_type": "^\S*$",
    }
