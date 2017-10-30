# coding=utf-8
import umfpayservice
from umfpayservice import error, util

import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.Hash import SHA, SHA256

def encrypt_data(data):
    '''
    使用联动公钥加密数据
    '''
    key = get_public_key()
    rsakey = RSA.importKey(key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    text = cipher.encrypt(data)
    bash64_r = base64.b64encode(text)

    return util.to_string(bash64_r)

def sign(data, mer_id):
    '''
    使用商户私钥对数据签名
    '''
    gbk_data = util.gbk_encode(data)
    private_key = get_private_key(mer_id)
    key = RSA.importKey(private_key)
    h = SHA.new(gbk_data)
    signer = Signature_pkcs1_v1_5.new(key)
    signature = signer.sign(h)
    bash64_r = base64.b64encode(signature)

    return util.to_string(bash64_r)
    #
    # return base64.b64encode(signature)

def submer_sign(data, mer_id):
    utf8_data = util.encode(data)

    private_key = get_private_key(mer_id)
    key = RSA.importKey(private_key)
    h = SHA256.new(utf8_data)
    signer = Signature_pkcs1_v1_5.new(key)
    signature = signer.sign(h)
    bash64_r = base64.b64encode(signature)

    return util.to_string(bash64_r)
    # return base64.b64encode(signature)

def app_sign(data, mer_id):
    '''
    app的签名方法
    '''
    base64_sign = sign(data, mer_id)
    sign_str = base64.b64decode(base64_sign)
    return base64.b16encode(sign_str)

def verify(data, signature):
    '''
    使用联动公钥对数据验签
    '''
    gbk_data = util.gbk_encode(data)

    public_key = get_public_key()
    key = RSA.importKey(public_key)
    digest = SHA.new()
    digest.update(gbk_data)
    verifier = Signature_pkcs1_v1_5.new(key)

    sig = base64.b64decode(signature)
    if verifier.verify(digest, sig):
        return True
    return False

def submer_verify(data, signature):
    utf8_data = util.encode(data)

    public_key = get_public_key()
    key = RSA.importKey(public_key)
    digest = SHA256.new()
    digest.update(utf8_data)
    verifier = Signature_pkcs1_v1_5.new(key)

    sig = base64.b64decode(signature)
    if verifier.verify(digest, sig):
        return True
    return False

def get_private_key(mer_id):
    '''
    获取商户私钥
    '''
    try:
        private_key_path = umfpayservice.umf_config.mer_private_keys[mer_id]
    except KeyError:
        raise error.ConfigError("[配置错误] mer_id不在商户私钥配置列表中。(mer_id: %s)"
                                "商户私钥配置列表为：%s. " % (mer_id, umfpayservice.umf_config.mer_private_keys), "mer_id", mer_id)

    private_key = open(private_key_path, "r").read()
    return private_key.strip()

def get_public_key():
    '''获取联动公钥'''
    return umfpayservice.umf_config.umf_public_key

def get_sorted_plain(params):
    params_copy = params.copy()
    # 删除不参与签名的字段
    if 'sign_type' in params_copy:
        del params_copy['sign_type']
    if 'sign' in params_copy:
        del params_copy['sign']

    params_copy = sorted(list(params_copy.items()), key=lambda d: d[0])
    plain = util.convert_url_not_encode(params_copy)

    # util.logger.info("获取签名明文串：%s" % plain)
    return plain