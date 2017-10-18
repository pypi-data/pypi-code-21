
CODE_0_SUCCESS = 0
CODE_1_ERROR = 1
CODE_2_LOGIN_REQUIRED = 2
CODE_3_ERROR_SECURE_TOKEN = 3
CODE_4_ERROR_USERNAME_OR_PASSWORD = 4
CODE_5_INVALID_PASSWORD = 5
CODE_6_USER_CREATION_FAILED = 6
CODE_7_SEND_SMS_FAILED = 7
CODE_8_CAPTCHA_VALIDATION_ERROR = 8
CODE_9_INVALID_PHONE_NUMBER = 9
CODE_10_INVALID_EMAIL_ADDRESS = 10
CODE_11_INVALID_USERNAME = 11
CODE_12_INVALID_CHINESE_NAME = 12
CODE_13_VCODE_VALIDATION_ERROR = 13
CODE_14_PHONE_ALREADY_EXISTS_ERROR = 14
CODE_15_USERNAME_ALREADY_EXISTS_ERROR = 15
CODE_16_EMAIL_ALREADY_EXISTS_ERROR = 16
CODE_17_SALESMAN_ROLE_REQUIRED = 17
CODE_18_ADVERTISER_REQUIRED = 18
CODE_19_MISSING_REQUIRED_PARAMS = 19
CODE_20_PERMISSION_DENIED = 20
CODE_21_INVALID_PARAMETER = 21
CODE_22_SHOPKEEPER_REQUIRED = 22
CODE_23_OBJECT_ALREADY_EXISTS = 23


class APIException(Exception):

    code = CODE_1_ERROR
    default_detail = 'A server error occurred.'
    default_detail_zh = '服务器发生了一个错误'

    def __init__(self, detail=None, chinese_detail=True):
        if detail is not None:
            self.detail = detail
        else:
            self.detail = self.default_detail
            if chinese_detail:
                self.detail = self.default_detail_zh

    def __str__(self):
        return self.detail


class LoginRequired(APIException):
    code = CODE_2_LOGIN_REQUIRED
    default_detail = 'Login required.'

    default_detail_zh = '请登陆后再进行此操作'


class SecureTokenError(APIException):

    code = CODE_3_ERROR_SECURE_TOKEN
    default_detail = 'Error secure token.'


class UsernameOrPasswordError(APIException):

    code = CODE_4_ERROR_USERNAME_OR_PASSWORD
    default_detail = 'Error username or password.'

    default_detail_zh = '错误的用户名或密码'


class InvalidPassword(APIException):

    code = CODE_5_INVALID_PASSWORD
    default_detail = 'Invalid password'

    default_detail_zh = '密码不符合要求'


class UserCreationError(APIException):

    code = CODE_6_USER_CREATION_FAILED
    default_detail = 'UserCreationError.'

    default_detail_zh = '创建用户失败'


class SMSSendFailed(APIException):

    code = CODE_7_SEND_SMS_FAILED
    default_detail = 'Send SMS failed'

    default_detail_zh = '短信发送失败'


class CaptchaValidationError(APIException):

    code = CODE_8_CAPTCHA_VALIDATION_ERROR
    default_detail = 'Captcha validation error'

    default_detail_zh = '验证码不匹配'


class InvalidPhoneNumber(APIException):

    code = CODE_9_INVALID_PHONE_NUMBER
    default_detail = 'Invalid phone number'

    default_detail_zh = '不正确的手机号码'


class InvalidEmailAddress(APIException):

    code = CODE_10_INVALID_EMAIL_ADDRESS
    default_detail = 'Invalid email address'

    default_detail_zh = '不正确的邮件地址'


class InvalidUsername(APIException):

    code = CODE_11_INVALID_USERNAME
    default_detail = 'Invalid username'

    default_detail_zh = '不合法的用户名'


class InvalidChineseName(APIException):

    code = CODE_12_INVALID_CHINESE_NAME
    default_detail = 'Invalid Chinese name'

    default_detail_zh = '不正确的中文姓名'


class VcodeValidationError(APIException):

    code = CODE_13_VCODE_VALIDATION_ERROR
    default_detail = 'Vcode validation error'

    default_detail_zh = '验证码不正确或已经失效'


class PhoneAlreadyExistsError(APIException):

    code = CODE_14_PHONE_ALREADY_EXISTS_ERROR
    default_detail = 'Phone already exists'

    default_detail_zh = '手机号已经被注册'


class UsernameAlreadyExistsError(APIException):

    code = CODE_15_USERNAME_ALREADY_EXISTS_ERROR
    default_detail = 'Username already exists'

    default_detail_zh = '用户名已存在'


class EmailAlreadyExistsError(APIException):

    code = CODE_16_EMAIL_ALREADY_EXISTS_ERROR
    default_detail = 'Email already exists'

    default_detail_zh = '邮箱地址已经被注册'


class SalesmanRequired(APIException):

    code = CODE_17_SALESMAN_ROLE_REQUIRED
    default_detail = 'A salesman account is required'

    default_detail_zh = '需要以地推人员账号登录'


class AdvertiserRequired(APIException):

    code = CODE_18_ADVERTISER_REQUIRED
    default_detail = 'An advertiser account is required'

    default_detail_zh = '需要以广告主账号登录'


class MissingRequiredParams(APIException):

    code = CODE_19_MISSING_REQUIRED_PARAMS
    default_detail = 'Required params is missing'

    default_detail_zh = '缺少必要参数'


class PermissionDenied(APIException):

    code = CODE_20_PERMISSION_DENIED
    default_detail = 'Permission denied'

    default_detail_zh = '没有权限查看此内容'


class InvalidParameterValue(APIException):

    code = CODE_21_INVALID_PARAMETER
    default_detail = 'Invalid parameter value'

    default_detail_zh = '不正确的参数值'


class ShopkeeperRequired(APIException):

    code = CODE_22_SHOPKEEPER_REQUIRED
    default_detail = 'An shopkeeper account is required'

    default_detail_zh = '需要以店主账号登录'


class ObjectAlreadyExists(APIException):

    code = CODE_23_OBJECT_ALREADY_EXISTS
    default_detail = 'Object already exists'

    default_detail_zh = '此项已经存在'
