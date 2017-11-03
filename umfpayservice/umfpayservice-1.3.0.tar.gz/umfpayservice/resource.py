# -*- coding: utf-8 -*-

import os
from bs4 import BeautifulSoup

import umfpayservice
from umfpayservice import api_requestor, util, error, regex_check, sign, common

class UmfPayObject(dict):

    def __init__(self):
        super(UmfPayObject, self).__init__()

class APIResource(UmfPayObject):

    def __init__(self, method, url):
        super(APIResource, self).__init__()

        self.method = method
        self.url = '%s/%s' % (self.get_base_url(), url)
        self.request_params = {}
        self.resp = {}

    def get_base_url(self):
        return 'https://pay.soopay.net'

    def get_headers(self, post_data):
        return {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    def request(self, post_data):
        self.request_params = post_data

        requestor = api_requestor.APIRequestor()
        response = requestor.request(self.method, self.url, post_data, self.get_headers(post_data))

        return response

    def create(self, **params):
        '''执行接口入口'''
        if self.method == 'get':
            self.url = "%s?%s" % (self.url, util.url_encode(params))
            post_data = None
        elif self.method == 'post':
            post_data = self.check_do_params(params)
            if post_data is None:
                raise error.ParamsError("处理post请求参数时出错")
        else:
            raise error.RequestError("umfpayservice包不支持该请求类型method：%s" % self.method)

        response = self.request(post_data)
        prepared_response = self.check_do_response(response)
        return prepared_response

    def upload(self, files, **params):
        post_data = self.check_do_params(params)
        files = self.check_do_files(files)

        if post_data is not None and files is not None and len(files) > 0:
            self.request_params = post_data
            requestor = api_requestor.APIRequestor()
            response = requestor.upload(self.url, files, self.get_headers(post_data))
            prepared_response = self.check_do_response(response)
            return prepared_response
        return None

    def check_do_params(self, params):
        return params

    def check_do_files(self, files):
        return files

    def check_do_response(self, response):
        return response

class ServiceAPIResource(APIResource):

    def __init__(self, service=None):
        super(ServiceAPIResource, self).__init__(method='post', url='spay/pay/payservice.do')

        if service in common.service_keys:
            self.service = service
        else:
            raise error.ParamsError("[请求参数校验] "
                                            "service: 为空或该接口本SDK不支持，请联系联动运营人员！")
        self.request_params = {}
        self.resp = {}

    def get_headers(self, post_data):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Encoding': umfpayservice.umf_config.charset
        }

    def create(self, **params):
        '''执行接口入口'''
        util.logger.info("\n\n开始执行===[%s]接口,service=%s ==========================="
                         % (common.logger_decs[self.service], self.service))

        response = super(ServiceAPIResource, self).create(**params)

        util.logger.info("处理后结果：%s" % str(response))
        util.logger.info("执行结束===[%s]接口,service=%s ==========================="
                        % (common.logger_decs[self.service], self.service))
        return response

    def check_do_params(self, params):
        '''校验和处理参数'''
        # util.logger.info("传入的参数列表为：\n%s" % util.JSON.str(params))

        params = self.add_common_params(params)
        params = {key: value.strip() for key, value in params.items()}

        if self.check_params(params):
            self.process_params(params)
            return util.urllib_parser.urlencode(params)
        return None

    def check_do_response(self, response):
        '''解析response'''
        try:
            rbody_dict = self._interpret_meta(response.strip())
            if sign.verify(rbody_dict['plain'], rbody_dict['sign']):
                if 'sign' in rbody_dict:
                    del rbody_dict['sign']
                if 'sign_type' in rbody_dict:
                    del rbody_dict['sign_type']
                if 'version' in rbody_dict:
                    del rbody_dict['version']
                if 'plain' in rbody_dict:
                    del rbody_dict['plain']
                resp = rbody_dict

                util.logger.info("解析响应数据获得：\n%s" % str(resp))
                return resp
            else:
                raise error.SignatureError("平台数据验签失败")
        except Exception as e:
            raise error.APIError(
                "接口返回的响应错误: %s" % (response),
                response)
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
            return params
        except:
            raise error.SignatureError("使用商户私钥生成签名失败。")

    @classmethod
    def encrypt_fields(cls, params):
        for key, value in params.items():
            if (value is not None or '') and key in common.encrypt_fields:
                try:
                    # value = util.deutf8('utf-8').encode('gbk')
                    value = util.gbk_encode(value)
                    params[key] = sign.encrypt_data(value)
                    util.logger.info("需要加密敏感字段：%s"
                                     "\n加密后为%s: %s" % (key, key, params[key]))
                except:
                    raise error.SignatureError("%s: 敏感字段加密失败。(%s: %s)" % (key, key, value))

    def _interpret_meta(self, rbody):
        '''
        解析meta
        :param rbody:
        :return:
        '''
        try:
            soup = BeautifulSoup(rbody, "html.parser")
            content = soup.head.meta['content']
            content = util.to_string(content)

            resp = {param_key: param_value for param_key, param_value in
                    (split_param.split('=', 1) for split_param in content.split('&'))}
            plain = sign.get_sorted_plain(resp)
            resp['plain'] = plain
        except:
            raise error.RequestError('解析服务器响应失败。body = %s' % rbody)
        return resp

    @classmethod
    def get_required_keys(cls):
        raise TypeError('APIResource 是一个虚拟类，你需要在它的子类中实现get_required_keys方法')

class DownLoadServiceAPIResource(ServiceAPIResource):

    def __init__(self, service=None):
        super(DownLoadServiceAPIResource, self).__init__(service)

    def get_headers(self, post_data):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Encoding': umfpayservice.umf_config.charset
        }

    def download(self, **params):
        file_path, file_name = self.get_save_path(params)
        util.logger.info("传入的保存文件路径为：\n%s\n文件名为：\n%s" % (file_path, file_name))

        post_data = self.check_do_params(params)
        if post_data is not None:
            rbody = api_requestor.APIRequestor().download('post', self.url, post_data, self.get_headers(post_data))

            self.write_file(file_path, file_name, self.do_response(rbody))
            return "下载对账文件成功，保存地址为：%s/%s" % (file_path, file_name)

    @classmethod
    def write_file(self, file_path, file_name, content):
        if not os.path.isdir(file_path):
            os.mkdir(file_path)

        try:
            content = util.decode(content, 'gbk')
            with open("%s/%s" % (file_path, file_name), 'w') as f:
                f.write(content)
            util.logger.info("文件下载成功，文件路径为：%s/%s" % (file_path, file_name))
        except IOError as e:
            raise IOError("本地写文件失败，path= %s/%s" % (file_path, file_name))

    def get_save_path(self, params):
        raise TypeError('DownLoadAPIResource 是一个虚拟类，你需要在它的子类中实现get_save_path方法')

    def do_response(self, rbody):
        raise TypeError('DownLoadAPIResource 是一个虚拟类，你需要在它的子类中实现do_response方法')

class ParamsGetServiceAPIResource(ServiceAPIResource):

    def __init__(self, service=None):
        super(ParamsGetServiceAPIResource, self).__init__(service)

    def create(self, **params):
        prepared_params = self.check_do_params(params)

        if prepared_params is not None:
            return self.params_to_get(prepared_params)
        return None

    def params_to_get(self, params):
        raise TypeError('ParamsGetAPIResource 是一个虚拟类，你需要在它的子类中实现params_to_get方法')

class SubMerAPIResource(APIResource):
    def __init__(self, method, url):
        super(SubMerAPIResource, self).__init__(method, url)

    def create(self, **params):
        '''执行接口入口'''
        util.logger.info("\n\n开始执行===接口地址url:%s ==========================="
                         % self.url)

        response = super(SubMerAPIResource, self).create(**params)

        util.logger.info("处理后结果：%s" % str(response))
        util.logger.info("执行结束===接口地址url:%s ==========================="
                         % self.url)
        return response

    def upload(self, files, **params):
        '''上传文件接口入口'''
        util.logger.info("\n\n开始执行===接口地址url:%s ==========================="
                         % self.url)
        response = super(SubMerAPIResource, self).upload(files, **params)

        util.logger.info("处理后结果：%s" % str(response))
        util.logger.info("执行结束===接口地址url:%s ==========================="
                         % self.url)
        return response
        pass

    def check_do_files(self, files):
        prepared_files = []
        for value in files:
            if os.path.isfile(value):

                prepared_files.append(('file', open(value, "rb"), ))
                # prepared_files["file%s" % files.index(value)] = ("file", open(value, "rb"))
            else:
                raise error.ParamsError("上传文件不存在file_path: %s" % value)

        return prepared_files

    def get_headers(self, post_data):
        return {
            "Content-type": "application/json;charset=utf-8",
        }

    def check_do_params(self, params):
        params = self.process_params(params)
        return util.json.dumps(params, sort_keys=True)

    def check_do_response(self, response):
        '''解析response'''
        try:
            rbody, sign_str = util.to_string(response).split('&', 1)
            if sign.submer_verify(rbody, sign_str):
                resp = util.json.loads(rbody)

                for meta_key, meta_value in resp['meta'].items():
                    resp[meta_key] = meta_value
                del resp['meta']

                return resp
            else:
                raise error.SignatureError("平台数据验签失败")

        except Exception:
            raise error.APIError(
                "接口返回的响应错误: %s" % (response),
                response)
        return resp

    @classmethod
    def process_params(cls, params):
        # 参数trim
        params = {key: value.strip() for key, value in params.items()}

        # 空参数过滤
        for key in list(params.keys()):
            if params[key] is None or (params[key] == ''):
                del params[key]

        # 敏感字段加密
        cls.encrypt_fields(params)
        return params

    @classmethod
    def encrypt_fields(cls, params):
        for key, value in params.items():
            if (value is not None or '') and key in common.encrypt_fields:
                try:
                    value = util.encode(value)
                    params[key] = sign.encrypt_data(value)
                    util.logger.info("需要加密敏感字段：%s"
                                     "\n加密后为%s: %s" % (key, key, params[key]))
                except:
                    raise error.SignatureError("%s: 敏感字段加密失败。(%s: %s)" % (key, key, value))