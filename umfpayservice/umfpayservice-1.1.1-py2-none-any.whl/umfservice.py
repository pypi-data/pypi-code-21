# coding=utf-8

import datetime
import urllib

import umfpayservice
from umfpayservice import util, error, sign
from umfpayservice.resource import APIResource, UmfPayObject, DownLoadAPIResource, ParamsGetAPIResource

class MobileOrder(APIResource):
    '''APP支付下单'''
    def __init__(self):
        super(MobileOrder, self).__init__('pay_req')

    @classmethod
    def get_required_keys(cls):
        return ["service" ,"charset", "mer_id", "sign_type", "version", "order_id", "mer_date", "amount", "amt_type"]

class ActiveScanPayment(APIResource):
    '''收款---扫码支付（主扫）下单方法'''
    def __init__(self):
        super(ActiveScanPayment, self).__init__('active_scancode_order')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "notify_url", "version", "goods_inf", "order_id", "mer_date", "amount", "amt_type", "scancode_type"]

class PassiveScanPayment(APIResource):
    '''收款---扫码支付（被扫）下单.'''
    def __init__(self):
        super(PassiveScanPayment, self).__init__('passive_scancode_pay')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "notify_url", "version", "goods_inf", "order_id", "mer_date", "amount", "amt_type", "auth_code", "use_desc", "scancode_type"]

class QuickPayOrder(APIResource):
    '''收款---快捷支付下单.'''
    def __init__(self):
        super(QuickPayOrder, self).__init__('apply_pay_shortcut')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "version", "order_id", "notify_url", "order_id", "mer_date", "amount", "amt_type", "pay_type", "gate_id"]

class QuickGetMessage(APIResource):
    '''收款---快捷支付向平台获取短信验证码.'''
    def __init__(self):
        super(QuickGetMessage, self).__init__('sms_req_shortcut')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "version", "trade_no", "media_id", "media_type"]

class QuickPayConfirm(APIResource):
    '''收款---快捷支付确认支付'''
    def __init__(self):
        super(QuickPayConfirm, self).__init__('confirm_pay_shortcut')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "version", "trade_no", "trade_no", "verify_code", "media_type", "media_id"]

class QuickQuerybankSupport(APIResource):
    '''收款---快捷支付获取银行卡列表'''
    def __init__(self):
        super(QuickQuerybankSupport, self).__init__('query_mer_bank_shortcut')

    @classmethod
    def get_required_keys(cls):
        return ["service", "sign_type", "charset", "mer_id", "version", "pay_type"]

class QuickCancelSurrender(APIResource):
    '''收款---快捷支付解约.'''
    def __init__(self):
        super(QuickCancelSurrender, self).__init__('unbind_mercust_protocol_shortcut')

    @classmethod
    def get_required_keys(cls):
        return ["service", "sign_type", "charset", "mer_id", "version"]

class QueryhistoryOrder(APIResource):
    '''订单查询---查询历史订单'''
    def __init__(self):
        super(QueryhistoryOrder, self).__init__('mer_order_info_query')

    @classmethod
    def get_required_keys(cls):
        return ["service", "sign_type", "charset", "mer_id", "version", "order_id", "mer_date"]

class QueryTodayOrder(APIResource):
    '''订单查询---查询当天订单'''
    def __init__(self):
        super(QueryTodayOrder, self).__init__('query_order')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "sign_type", "mer_id", "version", "order_id", "mer_date"]

class CancelTrade(APIResource):
    '''撤销'''
    def __init__(self):
        super(CancelTrade, self).__init__('mer_cancel')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "sign_type", "mer_id", "version", "order_id", "mer_date", "amount"]


class GeneralRefund(APIResource):
    '''退款---普通退款'''
    def __init__(self):
        super(GeneralRefund, self).__init__('mer_refund')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "sign_type", "mer_id", "version", "refund_no", "order_id", "mer_date", "org_amount"]

class MassTransferRefund(APIResource):
    '''退款---批量转账退费'''
    def __init__(self):
        super(MassTransferRefund, self).__init__('split_refund_req')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "version", "refund_no", "order_id", "mer_date", "refund_amount", "org_amount", "sub_mer_id", "sub_order_id"]

class QueryRefundState(APIResource):
    '''退款---退款状态查询方法'''
    def __init__(self):
        super(QueryRefundState, self).__init__('mer_refund_query')

    @classmethod
    def get_required_keys(cls):
        return ["service", "sign_type", "charset", "mer_id", "version", "refund_no"]

class RemedyRefundInformation(APIResource):
    '''退款---退费信息补录'''
    def __init__(self):
        super(RemedyRefundInformation, self).__init__('refund_info_replenish')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "version", "refund_no", "card_holder", "card_id"]

#------------------------------------------------------------
# 付款
#------------------------------------------------------------
class PaymentOrder(APIResource):
    '''付款---下单'''
    def __init__(self):
        super(PaymentOrder, self).__init__('transfer_direct_req')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "version", "sign_type", "order_id", "mer_date", "amount", "recv_account_type", "recv_bank_acc_pro", "recv_account", "recv_user_name", "recv_gate_id", "purpose", "prov_name", "city_name", "bank_brhname"]

class QueryPaymentStatus(APIResource):
    '''付款---付款状态查询'''
    def __init__(self):
        super(QueryPaymentStatus, self).__init__('transfer_query')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "version", "sign_type", "order_id", "mer_date"]

class QueryAccountBalance(APIResource):
    '''付款---余额查询'''
    def __init__(self):
        super(QueryAccountBalance, self).__init__('query_account_balance')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "version", "sign_type"]

# ------------------------------------------------------------
# 鉴权
#------------------------------------------------------------
class DebitCardAuthentication(APIResource):
    '''鉴权---借记卡实名认证'''
    def __init__(self):
        super(DebitCardAuthentication, self).__init__('comm_auth')

    def add_common_params(self, params):
        common_params = {
            'service': self.service.strip(),
            'sign_type': umfpayservice.umf_config.sign_type.strip(),
            'charset': umfpayservice.umf_config.charset.strip(),
            'res_format': umfpayservice.umf_config.res_format.strip(),
            'version': umfpayservice.umf_config.auth_version.strip()
        }
        return dict(common_params, **params)

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "version", "auth_type", "order_id"]

class CreditCardAuthentication(APIResource):
    '''鉴权---贷记卡实名认证'''
    def __init__(self):
        super(CreditCardAuthentication, self).__init__('comm_auth')

    def add_common_params(self, params):
        common_params = {
            'service': self.service.strip(),
            'sign_type': umfpayservice.umf_config.sign_type.strip(),
            'charset': umfpayservice.umf_config.charset.strip(),
            'res_format': umfpayservice.umf_config.res_format.strip(),
            'version': umfpayservice.umf_config.auth_version.strip()
        }
        return dict(common_params, **params)

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "version", "auth_type", "order_id"]

class IdentityAuthentication(APIResource):
    '''鉴权---身份认证'''
    def __init__(self):
        super(IdentityAuthentication, self).__init__('comm_auth')

    def add_common_params(self, params):
        common_params = {
            'service': self.service.strip(),
            'sign_type': umfpayservice.umf_config.sign_type.strip(),
            'charset': umfpayservice.umf_config.charset.strip(),
            'res_format': umfpayservice.umf_config.res_format.strip(),
            'version': umfpayservice.umf_config.auth_version.strip()
        }
        return dict(common_params, **params)


    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "version", "auth_type", "order_id"]

# ---------------------------------------------------------------
# 对账
# ---------------------------------------------------------------
class ReconciliationDownload(DownLoadAPIResource):
    '''对账---对账文件下载'''
    def __init__(self):
        super(ReconciliationDownload, self).__init__('download_settle_file')

    @classmethod
    def get_required_keys(cls):
        return ["service", "sign_type", "mer_id", "version", "settle_date"]

    def get_save_path(self, params):
        if 'settle_path' in params:
            file_path = params['settle_path']
            del params['settle_path']

            file_name = "settle_file_%s_%s.txt" % (params['mer_id'], datetime.datetime.now().strftime("%Y%m%d"))
            return file_path, file_name
        else:
            raise error.ParamsError("[请求参数校验] "
                                    "settle_path: 该字段不能为空。")

    def do_response(self, rbody):
        return rbody

# ------------------------------------------------------------
# 异步通知
# ------------------------------------------------------------

class AsynNotification(UmfPayObject):
    '''
    异步通知
    '''
    def __init__(self):
        super(AsynNotification, self).__init__()

    def notify_data_parser(self, notify_params_str):
        '''
        解析异步通知数据
        :param notify_params_str:
        :return:
        '''
        try:
            notify_params = {key: urllib.unquote(value) for key, value in
                            (split_param.split('=', 1) for split_param in notify_params_str.split('&'))}
            plain = sign.get_sorted_plain(notify_params)
            verify = sign.verify(plain, notify_params['sign'])
        except:
            raise error.SignatureError('异步通知验证签名异常')

        if verify:
            util.logger.info("平台通知数据验签成功")
            if 'sign' in notify_params: del notify_params['sign']
            if 'sign_type' in notify_params: del notify_params['sign_type']
            if 'version' in notify_params: del notify_params['version']

            return notify_params
        else:
            util.logger.info("平台通知数据验证签名发生异常")

    def response_umf_map(self, notify_params):
        '''
        拼接响应给平台的数据
        :param notify_params:
        :return:
        '''
        response_dict = {
            'mer_date': notify_params['mer_date'],
            'mer_id': notify_params['mer_id'],
            'order_id': notify_params['order_id'],
            'ret_code': '0000',
            'ret_msg': 'success',
            'version': '4.0',
            'sign_type': 'RSA'
        }

        mer_plain = sign.get_sorted_plain(response_dict)
        mer_sign = sign.sign(mer_plain, notify_params['mer_id'])
        response_dict['sign'] = mer_sign

        return util.convert_url_not_encode(response_dict)

class WebFrontPagePay(ParamsGetAPIResource):
    '''Web收银台---生成get后的请求参数，商户只需要拼接URL进行get请求即可'''
    def __init__(self):
        super(WebFrontPagePay, self).__init__('req_front_page_pay')

    def params_to_get(self, params):
        return urllib.urlencode(params)

    @classmethod
    def get_required_keys(cls):
        return ["mer_id", "order_id", "mer_date", "amount", "amt_type", "interface_ty"]

class H5FrontPage(ParamsGetAPIResource):
    '''H5收银台---生成get后的请求参数，商户只需要拼接URL进行get请求即可'''
    def __init__(self):
        super(H5FrontPage, self).__init__('pay_req_h5_frontpage')

    def params_to_get(self, params):
        return urllib.urlencode(params)

    @classmethod
    def get_required_keys(cls):
        return ["mer_id", "order_id", "mer_date", "notify_url", "ret_url", "amount", "amt_type"]

class PublicPayment(ParamsGetAPIResource):
    '''公众号支付--生成get后的请求参数，商户只需要拼接URL进行get请求即可'''
    def __init__(self):
        super(PublicPayment, self).__init__('publicnumber_and_verticalcode')

    def params_to_get(self, params):
        return urllib.urlencode(params)

    @classmethod
    def get_required_keys(cls):
        return ["mer_id", "order_id", "notify_url", "mer_date", "goods_inf", "amount", "amt_type", "is_public_number"]

class UmfServiceUtils(UmfPayObject):
    '''
    其他工具
    '''
    def __init__(self):
        super(UmfServiceUtils, self).__init__()

    @classmethod
    def generate_sign(cls, **params):
        '''SDK生成签名方法，传入请求字典，生成sign字段'''
        plain = sign.get_sorted_plain(params)
        return sign.sign(plain, params['mer_id'])

    @classmethod
    def mobile_generate_sign(cls, **params):
        '''APP---聚合支付SDK后台生成签名为移动端使用聚合支付SDK签名使用'''
        params = params or {}

        requiredKeys = ['merId', 'orderId', 'orderDate', 'amount']
        for requiredKey in requiredKeys:
            if requiredKey not in params or params[requiredKey] is None or params[requiredKey] == '':
                raise error.ParamsError('签名参数%s为空,请传入%s' % (requiredKey, requiredKey))

        plain = "%s%s%s%s" % (params['merId'], params['orderId'], params['amount'], params['orderDate'])
        sign_str = sign.app_sign(plain, params['merId'])
        util.logger.info("[generate_sign]签名后密文串:%s" % sign_str)
        return sign_str

    @classmethod
    def verify_sign(cls, plain, sign_str):
        '''SDK验签方法传入参数分别为联动返回明文和密文sign字段，明文在前'''
        return sign.verify(plain, sign_str)