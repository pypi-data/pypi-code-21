# coding=utf-8
import logging

from umfpayservice import error, regex_check
from umfpayservice.util import logger
import datetime
import os

class Config(object):

    def __init__(self):
        # # log文件输出路径
        # self.log_path = "./logs"
        # 私钥对
        self.mer_private_keys = {}
        # 联动公钥
        self.umf_public_key = '-----BEGIN PUBLIC KEY-----\n' \
                              'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDGWAu4p6aK1SiQqNKT1nTgYwA8\n' \
                              'cz0Rde9fRtmLJAx1QxLqrerAUVl/uuXV7NQFSkTipouo3cwEEpae89267AeLJBzK\n' \
                              'PbKnUID6JYGbwnq7CiRR4E244zcgqE8jo8DnkbH3KkiWonoUMD1uHy6TUFv5W7zr\n' \
                              'haz/E59MVmbzrp1TwwIDAQAB\n' \
                              '-----END PUBLIC KEY-----'
        # 接口版本
        self.api_version = '4.0'
        self.auth_version = '1.0'
        # 默认签名加密方式
        self.sign_type = 'RSA'
        # 默认编码方式
        self.charset = 'UTF-8'
        # 默认响应格式
        self.res_format = 'HTML'

        self.is_log = True
        self.log_path = './logs'
        self.log_level = logging.INFO

        # 子商户入网配置
        self.submer_token = 'e7de0583b811b898c043346564a6f1855f26fa64b3b80b3797043045e5aa038f'


    def add_private_keys(self, key_list=None):
        '''
        动态添加商户号和私钥路径对
        :param key_list:
        :return:
        '''
        if key_list is None:
            return

        if isinstance(key_list, list):
            for mer_id, private_key_path in key_list:
                if regex_check.check("mer_id", mer_id):
                    self.mer_private_keys[mer_id] = private_key_path
                else:
                    raise error.ConfigError("[配置错误] mer_id格式不匹配。(mer_id: %s)"
                                            "匹配规则为：%s" % (mer_id, regex_check.get_regexs()["mer_id"]))

    def set_log_path(self, log_path, level=logging.INFO):
        '''设置log路径'''
        self.is_log = True
        self.log_path = log_path
        self.log_level = level
        self.set_logger()

    def set_log(self, is_log):
        self.is_log = is_log
        self.set_logger()

    def set_logger(self):
        if self.is_log and logger.disabled is 0:
            if os.path.isdir(self.log_path):
                pass
            else:
                os.mkdir(self.log_path)
            log_file = "%s/umfservice_log_%s.log" % (self.log_path, datetime.datetime.now().strftime("%Y%m%d"))

            fh = logging.FileHandler(log_file)
            fh.setLevel(logging.DEBUG)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [UMF SDK]%(message)s')
            fh.setFormatter(formatter)
            logger.setLevel(self.log_level)
            logger.addHandler(fh)
        elif not self.is_log:
            logger.disabled = True


# 需要加密的敏感字段
encrypt_fields = ["card_id", "valid_date", "cvv2", "pass_wd", "identity_code",
                  "card_holder", "recv_account", "recv_user_name", "identity_holder",
                  "identityCode", "cardHolder", "mer_cust_name", "account_name", "bank_account", "endDate",

                  "contActsName", "merName", "lawyer", "cardNo", "bankName", "bankAccount", ]

# 联动提供的service列表
service_keys = ["pay_req", "pay_req_ivr_call", "pay_req_ivr_tcall", "query_order", "mer_cancel",
                    "mer_refund", "download_settle_file", "pay_req_split_front", "pay_req_split_back",
                    "pay_req_split_direct", "split_refund_req", "pay_result_notify", "split_req_result",
                    "split_refund_result", "credit_direct_pay", "debit_direct_pay", "pre_auth_direct_req",
                    "pre_auth_direct_pay", "pre_auth_direct_cancel", "pre_auth_direct_query",
                    "pre_auth_direct_refund", "pre_auth_direct_settle", "pay_transfer_register",
                    "pay_transfer_req", "pay_transfer_order_query", "pay_transfer_mer_refund", "card_auth",
                    "req_sms_verifycode", "pay_confirm", "pay_req_shortcut_front", "pay_req_shortcut",
                    "agreement_pay_confirm_shortcut", "query_mer_bank_shortcut", "unbind_mercust_protocol_shortcut",
                    "split_req",  "query_split_order",  "transfer_direct_req",  "transfer_query",
                    "mer_order_info_query",  "mer_refund_query",  "active_scancode_order", "passive_scancode_pay",
                    "query_account_balance", "comm_auth", "apply_pay_shortcut", "sms_req_shortcut",
                    "confirm_pay_shortcut", "get_mer_bank_shortcut", "unbind_mercust_protocol_shortcut",
                    "refund_info_replenish", "req_bind_verify_shortcut","req_bind_confirm_shortcut",
                    "bind_agreement_notify_shortcut","bind_req_shortcut_front", "req_front_page_pay", "pay_req_h5_frontpage",
                    "publicnumber_and_verticalcode"]

# service对应的日志描述，log用
logger_decs = {
    # service: (接口名字/..)
    "pay_req": ("APP支付下单"),
    "pay_req_ivr_call": (""),
    "pay_req_ivr_tcall": (""),
    "query_order": ("订单查询---查询当天订单"),
    "mer_cancel": ("撤销"),
    "mer_refund": ("退款---普通退款"),
    "download_settle_file": ("对账---对账文件下载"),
    "pay_req_split_front": (""),
    "pay_req_split_back": (""),
    "pay_req_split_direct": (""),
    "split_refund_req": ("退款---批量转账退费"),
    "pay_result_notify": (""),
    "split_req_result": (""),
    "split_refund_result": (""),
    "credit_direct_pay": (""),
    "debit_direct_pay": (""),
    "pre_auth_direct_req": (""),
    "pre_auth_direct_pay": (""),
    "pre_auth_direct_cancel": (""),
    "pre_auth_direct_query": (""),
    "pre_auth_direct_refund": (""),
    "pre_auth_direct_settle": (""),
    "pay_transfer_register": (""),
    "pay_transfer_req": (""),
    "pay_transfer_order_query": (""),
    "pay_transfer_mer_refund": (""),
    "card_auth": (""),
    "req_sms_verifycode": (""),
    "pay_confirm": (""),
    "pay_req_shortcut_front": (""),
    "pay_req_shortcut": (""),
    "agreement_pay_confirm_shortcut": (""),
    "query_mer_bank_shortcut": ("收款---快捷支付获取银行卡列表"),
    "unbind_mercust_protocol_shortcut": ("收款---快捷支付解约."),
    "split_req": (""),
    "query_split_order": (""),
    "transfer_direct_req": ("付款---下单"),
    "transfer_query": ("付款---付款状态查询"),
    "mer_order_info_query": ("订单查询---查询历史订单"),
    "mer_refund_query": ("退款---退款状态查询方法"),
    "active_scancode_order": ("收款---扫码支付（主扫）下单方法"),
    "passive_scancode_pay": ("收款---扫码支付（被扫）下单."),
    "query_account_balance": ("付款---余额查询"),
    "comm_auth": ("鉴权"),
    "apply_pay_shortcut": ("收款---快捷支付下单."),
    "sms_req_shortcut": ("收款---快捷支付向平台获取短信验证码."),
    "confirm_pay_shortcut": ("收款---快捷支付确认支付"),
    "get_mer_bank_shortcut": (""),
    "refund_info_replenish": ("退款---退费信息补录"),
    "req_bind_verify_shortcut": (""),
    "req_bind_confirm_shortcut": (""),
    "bind_agreement_notify_shortcut": (""),
    "bind_req_shortcut_front": (""),
    "req_front_page_pay": ("Web收银台---生成get后的请求参数"),
    "pay_req_h5_frontpage": ("H5收银台---生成get后的请求参数"),
    "publicnumber_and_verticalcode": ("公众号支付--生成get后的请求参数"),
}

