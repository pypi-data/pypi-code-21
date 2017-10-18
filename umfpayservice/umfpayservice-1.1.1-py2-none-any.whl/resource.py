# -*- coding: utf-8 -*-

import os

import umfpayservice
from umfpayservice import api_requestor, util, error, regex_check, sign, common

class UmfPayObject(dict):
    def __init__(self, service=None):
        super(UmfPayObject, self).__init__()

        self.service = service

class APIResource(UmfPayObject):

    def __init__(self, service=None):
        super(APIResource, self).__init__(service)

        if service in common.service_keys:
            self.service = service
        else:
            raise error.ParamsError("[请求参数校验] "
                                            "service: 为空或该接口本SDK不支持，请联系联动运营人员！")
        self.request_params = {}
        self.resp = {}

    def request(self, params):
        self.request_params = params

        requestor = api_requestor.APIRequestor()
        response = requestor.request('post', params)
        self.resp = response
        return response

    def create(self, **params):
        '''执行接口入口'''
        util.logger.info("\n\n开始执行===[%s]接口,service=%s ==========================="
                         % (common.logger_decs[self.service], self.service))

        prepared_params = self.check_do_params(params)
        if prepared_params is not None:
            response = self.request(prepared_params)

            util.logger.info("执行结束===[%s]接口,service=%s ==========================="
                             % (common.logger_decs[self.service], self.service))
            return response
        return None

    def check_do_params(self, params):
        '''校验和处理参数'''
        # util.logger.info("传入的参数列表为：\n%s" % util.JSON.str(params))

        params = self.add_common_params(params)
        params = {key: value.strip() for key, value in params.items()}

        if self.check_params(params):
            self.process_params(params)
            return params
        return None

    def add_common_params(self, params):
        '''
        添加公共参数
        '''
        common_params = {
            'service': self.service,
            'sign_type': umfpayservice.umf_config.sign_type,
            'charset': umfpayservice.umf_config.charset,
            'res_format': umfpayservice.umf_config.res_format,
            'version': umfpayservice.umf_config.api_version
        }
        # util.logger.info("添加公共参数列表为：\n%s" % util.JSON.str(common_params))
        return dict(common_params, **params)

    def check_params(self, params):
        '''校验参数'''

        # 必传字段校验
        required_keys = self.get_required_keys()
        util.logger.info("该接口的必传参数列表为：%r" % required_keys)
        for required_key in required_keys:
            if required_key not in params:
                raise error.ParamsError("[请求参数校验]"
                                        "该接口缺少必传字段。必传字段列表为：%s" % required_keys)

        # 正则校验
        if (regex_check.check(key, value) for key, value in params.items()):
            util.logger.info("参数校验通过！")
            return True
        return False

    @classmethod
    def process_params(cls, params):
        # 空参数过滤
        for key in list(params.keys()):
            if params[key] is None or (params[key] == ''):
                del params[key]

        # 敏感字段加密
        cls.encrypt_fields(params)

        # 添加签名
        try:
            plain = sign.get_sorted_plain(params)
            sign_str = sign.sign(plain, params['mer_id'])
            util.logger.info("生成签名为 sign：\n%s" % sign_str)
            params['sign'] = sign_str

            util.logger.info("处理后的请求参数为：\n%s" % str(params))
        except:
            raise error.SignatureError("使用商户私钥生成签名失败。")

    @classmethod
    def encrypt_fields(cls, params):
        for key, value in params.items():
            if (value is not None or '') and key in common.encrypt_fields:
                try:
                    value = value.decode('utf-8').encode('gbk')
                    params[key] = sign.encrypt_data(value)
                    util.logger.info("需要加密敏感字段：%s"
                                     "\n加密后为%s: %s" % (key, key, params[key]))
                except:
                    raise error.SignatureError("%s: 敏感字段加密失败。(%s: %s)" % (key, key, value))

    @classmethod
    def get_required_keys(cls):
        raise TypeError('APIResource 是一个虚拟类，你需要在它的子类中实现get_required_keys方法')


class DownLoadAPIResource(APIResource):

    def __init__(self, service=None):
        super(DownLoadAPIResource, self).__init__(service)

    def download(self, **params):

        prepared_params = self.check_do_params(params)
        if prepared_params is not None:
            file_path, file_name = self.get_save_path(prepared_params)

            util.logger.info("传入的保存文件路径为：\n%s\n文件名为：\n%s" % (file_path, file_name))
            rbody, rcode = api_requestor.APIRequestor().download(file_path, file_name, 'post', prepared_params)

            if not (200 <= rcode < 300):
                raise error.APIError(
                    "接口返回的响应错误: %r (响应码为： %d)" % (rbody, rcode),
                    rbody, rcode)
            else:
                self.write_file(file_path, file_name, self.do_response(rbody))
                return "下载对账文件成功，保存地址为：%s/%s" % (file_path, file_name)

    @classmethod
    def write_file(self, file_path, file_name, content):
        if not os.path.isdir(file_path):
            os.mkdir(file_path)

        try:
            content = content.decode('gbk').encode('utf-8')
            with open("%s/%s" % (file_path, file_name), 'w') as f:
                f.write(content)
            util.logger.info("文件下载成功，文件路径为：%s/%s" % (file_path, file_name))
        except IOError as e:
            raise IOError("本地写文件失败，path= %s/%s" % (file_path, file_name))

    def get_save_path(self, params):
        raise TypeError('DownLoadAPIResource 是一个虚拟类，你需要在它的子类中实现get_save_path方法')

    def do_response(self, rbody):
        raise TypeError('DownLoadAPIResource 是一个虚拟类，你需要在它的子类中实现do_response方法')

class ParamsGetAPIResource(APIResource):

    def __init__(self, service=None):
        super(ParamsGetAPIResource, self).__init__(service)

    def create(self, **params):
        prepared_params = self.check_do_params(params)

        if prepared_params is not None:
            return self.params_to_get(prepared_params)
        return None

    def params_to_get(self, params):
        raise TypeError('ParamsGetAPIResource 是一个虚拟类，你需要在它的子类中实现params_to_get方法')




