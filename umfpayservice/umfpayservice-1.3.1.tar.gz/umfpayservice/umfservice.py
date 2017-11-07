# coding=utf-8

import datetime
from bs4 import BeautifulSoup

import umfpayservice
from umfpayservice import util, error, sign
from umfpayservice.resource import UmfPayObject, ServiceAPIResource, DownLoadServiceAPIResource, ParamsGetServiceAPIResource, SubMerAPIResource

class MobileOrder(ServiceAPIResource):
    '''APP支付下单'''
    def __init__(self):
        super(MobileOrder, self).__init__('pay_req')

    @classmethod
    def get_required_keys(cls):
        return ["service" ,"charset", "mer_id", "sign_type", "version", "order_id", "mer_date", "amount", "amt_type"]

class ActiveScanPayment(ServiceAPIResource):
    '''收款---扫码支付（主扫）下单方法'''
    def __init__(self):
        super(ActiveScanPayment, self).__init__('active_scancode_order')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "notify_url", "version", "goods_inf", "order_id", "mer_date", "amount", "amt_type", "scancode_type"]

class PassiveScanPayment(ServiceAPIResource):
    '''收款---扫码支付（被扫）下单.'''
    def __init__(self):
        super(PassiveScanPayment, self).__init__('passive_scancode_pay')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "notify_url", "version", "goods_inf", "order_id", "mer_date", "amount", "amt_type", "auth_code", "use_desc", "scancode_type"]

class QuickPayOrder(ServiceAPIResource):
    '''收款---快捷支付下单.'''
    def __init__(self):
        super(QuickPayOrder, self).__init__('apply_pay_shortcut')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "version", "order_id", "notify_url", "order_id", "mer_date", "amount", "amt_type", "pay_type", "gate_id"]

class QuickGetMessage(ServiceAPIResource):
    '''收款---快捷支付向平台获取短信验证码.'''
    def __init__(self):
        super(QuickGetMessage, self).__init__('sms_req_shortcut')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "version", "trade_no", "media_id", "media_type"]

class QuickPayConfirm(ServiceAPIResource):
    '''收款---快捷支付确认支付'''
    def __init__(self):
        super(QuickPayConfirm, self).__init__('confirm_pay_shortcut')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "version", "trade_no", "trade_no", "verify_code", "media_type", "media_id"]

class QuickQuerybankSupport(ServiceAPIResource):
    '''收款---快捷支付获取银行卡列表'''
    def __init__(self):
        super(QuickQuerybankSupport, self).__init__('query_mer_bank_shortcut')

    @classmethod
    def get_required_keys(cls):
        return ["service", "sign_type", "charset", "mer_id", "version", "pay_type"]

class QuickCancelSurrender(ServiceAPIResource):
    '''收款---快捷支付解约.'''
    def __init__(self):
        super(QuickCancelSurrender, self).__init__('unbind_mercust_protocol_shortcut')

    @classmethod
    def get_required_keys(cls):
        return ["service", "sign_type", "charset", "mer_id", "version"]

class QueryhistoryOrder(ServiceAPIResource):
    '''订单查询---查询历史订单'''
    def __init__(self):
        super(QueryhistoryOrder, self).__init__('mer_order_info_query')

    def check_params(self, params):
        '''校验参数'''

        # 必传字段校验
        required_keys = self.get_required_keys()
        util.logger.info("该接口的必传参数列表为：%r" % required_keys)
        for required_key in required_keys:
            if required_key not in params:
                raise error.ParamsError("[请求参数校验]"
                                        "该接口缺少必传字段。必传字段列表为：%s" % required_keys)

        if not ("trade_no" in params or "order_id" in params):
            raise error.ParamsError("[请求参数校验]"
                                    "trade_no和order_id至少有一个不为空")

        # 正则校验
        if (self.regex_check.check(key, value) for key, value in params.items()):
            util.logger.info("参数校验通过！")
            return True
        return False

    @classmethod
    def get_required_keys(cls):
        return ["service", "sign_type", "charset", "mer_id", "version", "mer_date"]

class QueryTodayOrder(ServiceAPIResource):
    '''订单查询---查询当天订单'''
    def __init__(self):
        super(QueryTodayOrder, self).__init__('query_order')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "sign_type", "mer_id", "version", "order_id", "mer_date"]

class CancelTrade(ServiceAPIResource):
    '''撤销'''
    def __init__(self):
        super(CancelTrade, self).__init__('mer_cancel')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "sign_type", "mer_id", "version", "order_id", "mer_date", "amount"]


class GeneralRefund(ServiceAPIResource):
    '''退款---普通退款'''
    def __init__(self):
        super(GeneralRefund, self).__init__('mer_refund')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "sign_type", "mer_id", "version", "refund_no", "order_id", "mer_date", "org_amount"]

class MassTransferRefund(ServiceAPIResource):
    '''退款---批量转账退费'''
    def __init__(self):
        super(MassTransferRefund, self).__init__('split_refund_req')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "version", "refund_no", "order_id", "mer_date", "refund_amount", "org_amount", "sub_mer_id", "sub_order_id"]

class QueryRefundState(ServiceAPIResource):
    '''退款---退款状态查询方法'''
    def __init__(self):
        super(QueryRefundState, self).__init__('mer_refund_query')

    @classmethod
    def get_required_keys(cls):
        return ["service", "sign_type", "charset", "mer_id", "version", "refund_no"]

class RemedyRefundInformation(ServiceAPIResource):
    '''退款---退费信息补录'''
    def __init__(self):
        super(RemedyRefundInformation, self).__init__('refund_info_replenish')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "version", "refund_no", "card_holder", "card_id"]

#------------------------------------------------------------
# 付款
#------------------------------------------------------------
class PaymentOrder(ServiceAPIResource):
    '''付款---下单'''
    def __init__(self):
        super(PaymentOrder, self).__init__('transfer_direct_req')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "version", "sign_type", "order_id", "mer_date", "amount", "recv_account_type", "recv_bank_acc_pro", "recv_account", "recv_user_name"]

class QueryPaymentStatus(ServiceAPIResource):
    '''付款---付款状态查询'''
    def __init__(self):
        super(QueryPaymentStatus, self).__init__('transfer_query')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "version", "sign_type", "order_id", "mer_date"]

class QueryAccountBalance(ServiceAPIResource):
    '''付款---余额查询'''
    def __init__(self):
        super(QueryAccountBalance, self).__init__('query_account_balance')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "version", "sign_type"]

# ------------------------------------------------------------
# 鉴权
#------------------------------------------------------------
class DebitCardAuthentication(ServiceAPIResource):
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

class CreditCardAuthentication(ServiceAPIResource):
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

class IdentityAuthentication(ServiceAPIResource):
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
class ReconciliationDownload(DownLoadServiceAPIResource):
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

    @classmethod
    def notify_data_parser(self, notify_params_str):
        '''
        解析异步通知数据
        :param notify_params_str:
        :return:
        '''
        try:
            notify_params = {key: util.urllib_parser.unquote(value) for key, value in
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

    @classmethod
    def response_umf_map(self, notify_params):
        '''拼接响应给平台的数据'''
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

    @classmethod
    def response_child_notify_map(cls, notify_params):
        '''子商户入网响应给平台的数据'''
        response_dict = {
            'merId': notify_params['merId'],
            'licenseNo': notify_params['licenseNo'],
            'ret_code': notify_params['ret_code']
        }

        mer_plain = sign.get_sorted_plain(response_dict)
        mer_sign = sign.sign(mer_plain, notify_params['merId'])
        response_dict['sign'] = mer_sign

        return util.convert_url_not_encode(response_dict)

    @classmethod
    def convert_to_html(self, meta_content):
        html_str = "<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01 Transitional//EN'>"\
                    "<HTML>"\
                    " <HEAD><META NAME='MobilePayPlatform' CONTENT='%s' /></HEAD>"\
                    " <BODY>"\
                    " </BODY>"\
                     "</HTML>" % meta_content
        return html_str

class WebFrontPagePay(ParamsGetServiceAPIResource):
    '''Web收银台---生成get后的请求参数，商户只需要拼接URL进行get请求即可'''
    def __init__(self):
        super(WebFrontPagePay, self).__init__('req_front_page_pay')

    def params_to_get(self, params):
        return params

    @classmethod
    def get_required_keys(cls):
        return ["mer_id", "order_id", "mer_date", "amount", "amt_type", "interface_type"]

class H5FrontPage(ParamsGetServiceAPIResource):
    '''H5收银台---生成get后的请求参数，商户只需要拼接URL进行get请求即可'''
    def __init__(self):
        super(H5FrontPage, self).__init__('pay_req_h5_frontpage')

    def params_to_get(self, params):
        return params

    @classmethod
    def get_required_keys(cls):
        return ["mer_id", "order_id", "mer_date", "notify_url", "ret_url", "amount", "amt_type"]

class PublicPayment(ParamsGetServiceAPIResource):
    '''公众号支付--生成get后的请求参数，商户只需要拼接URL进行get请求即可'''
    def __init__(self):
        super(PublicPayment, self).__init__('publicnumber_and_verticalcode')

    def params_to_get(self, params):
        return params

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

class SubMerGetToken(SubMerAPIResource):
    '''获取token'''
    def __init__(self):
        super(SubMerGetToken, self).__init__('post', 'spay_restPay/oauth/authorize')

    def get_token(self, **params):
        resp = super(SubMerGetToken, self).create(**params)

        token = resp['access_token']
        if token:
            # 保存token
            umfpayservice.umf_config.submer_token = util.decode(token)
        else:
            raise error.APIError(
                "接口返回的响应错误: %s" % (resp),
                resp)
        return token

    def check_do_response(self, response):
        '''解析response'''
        try:
            # 获取token不需要验证签名
            resp = util.json.loads(response)
            return resp
        except Exception:
            raise error.APIError(
                "接口返回的响应错误: %s" % (response),
                response)
        return resp

class AddSubMerInfo(SubMerAPIResource):
    def __init__(self):
        super(AddSubMerInfo, self).__init__('post', 'spay_restPay/addChildMerInfo')

    def add_submer(self, **params):
        self.mer_id = params['merId']

        resp = super(AddSubMerInfo, self).create(**params)
        return resp

    def get_headers(self, post_data):
        try:
            sign_str = sign.submer_sign(post_data, self.mer_id)
        except:
            raise error.SignatureError("使用商户私钥生成签名失败。")

        return {
            "Content-type": "application/json;charset=utf-8",
            "Signature": sign_str,
            "Authorization": "Bearer%s" % umfpayservice.umf_config.submer_token
        }


class ChangeChildRebut(AddSubMerInfo):
    def __init__(self):
        super(AddSubMerInfo, self).__init__('post', 'spay_restPay/changeChildRebut')

    def change_child_rebut(self, **params):
        resp = super(ChangeChildRebut, self).add_submer(**params)
        return resp


class UploadMerFiles(SubMerAPIResource):
    def __init__(self):
        super(UploadMerFiles, self).__init__('post', 'spay_restPay/uploadChildFile')

    def upload_mer_files(self, files, **params):
        self.mer_id = params['merId']

        json_params = util.json.dumps(params, sort_keys=True)
        self.url = "%s?data=%s" % (self.url, util.urllib_parser.quote(json_params))

        resp = super(UploadMerFiles, self).upload(files, **params)
        return resp

    def get_headers(self, post_data):
        try:
            sign_str = sign.submer_sign(post_data, self.mer_id)
        except:
            raise error.SignatureError("使用商户私钥生成签名失败。")

        return {
            # "Content-type": "application/json;charset=utf-8",
            "Signature": sign_str,
            "Authorization": "Bearer%s" % umfpayservice.umf_config.submer_token
        }

class QueryChildState(SubMerAPIResource):
    def __init__(self):
        super(QueryChildState, self).__init__('get', 'spay_restPay/selectChildMerState')

    def query(self, **params):
        self.mer_id = params['merId']

        resp = super(QueryChildState, self).create(**params)
        return resp

    def get_headers(self, post_data):
        return {
            "Content-type": "application/json;charset=utf-8",
            "Authorization": "Bearer%s" % umfpayservice.umf_config.submer_token
        }

class SplitFileDownload(DownLoadServiceAPIResource):
    '''分账文件下载'''
    def __init__(self):
        super(SplitFileDownload, self).__init__('download_settle_file')

    @classmethod
    def get_required_keys(cls):
        return ["service", "sign_type", "mer_id", "settle_date", "settle_type"]

    def get_save_path(self, params):
        if 'settle_path' in params:
            file_path = params['settle_path']
            del params['settle_path']

            file_name = "%s_%s.split.txt" % (params['mer_id'], datetime.datetime.now().strftime("%Y%m%d"))
            return file_path, file_name
        else:
            raise error.ParamsError("[请求参数校验] "
                                    "settle_path: 该字段不能为空。")

    def do_response(self, rbody):
        return rbody

class SplitState(ServiceAPIResource):
    '''分账---分账状态查询'''
    def __init__(self):
        super(SplitState, self).__init__('query_split_order')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "version","mer_id","mer_date","order_id"]

class SplitRefund(GeneralRefund):
    '''分账---分账退费'''

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "sign_type", "mer_id", "version", "refund_no", "order_id", "mer_date"]

class SplitReq(ServiceAPIResource):
    '''分账---分账请求针对标准分账的延时分账'''
    def __init__(self):
        super(SplitReq, self).__init__('split_req')

    @classmethod
    def get_required_keys(cls):
        return ["service", "charset", "mer_id", "sign_type", "version", "order_id", "mer_date"]

class PayBankDirect(ParamsGetServiceAPIResource):
    '''Web收银台---生成get后的请求参数，商户只需要拼接URL进行get请求即可'''
    def __init__(self):
        super(PayBankDirect, self).__init__('pay_req_split_direct')

    def get_h5_url(self, **params):
        response = self.create(**params)
        return "https://pay.soopay.net/spay/pay/payservice.do?%s" % response

    def params_to_get(self, params):
        return params

    @classmethod
    def get_required_keys(cls):
        return ["service","charset","mer_id","sign_type","version","order_id","mer_date","amount","amt_type"]

class DebitDirect(ServiceAPIResource):
    '''收款---借记卡直连.'''
    def __init__(self):
        super(DebitDirect, self).__init__('debit_direct_pay')

    @classmethod
    def get_required_keys(cls):
        return ["service","charset","mer_id","sign_type","version","order_id","mer_date","amount","amt_type","pay_type", "card_id"]

class CreditDirect(ServiceAPIResource):
    '''收款---信用卡直连.'''
    def __init__(self):
        super(CreditDirect, self).__init__('credit_direct_pay')

    @classmethod
    def get_required_keys(cls):
        return ["service","charset","mer_id","sign_type","version","order_id","mer_date","amount","amt_type","pay_type","card_id","valid_date", "cvv2"]