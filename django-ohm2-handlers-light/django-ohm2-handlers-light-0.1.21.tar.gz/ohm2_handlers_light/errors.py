from django.utils.translation import ugettext as _

BASE_ERROR_CODE = 79253

INVALID_JSON_OBJECT = {
	"code": BASE_ERROR_CODE | 1, "message": _("Invalid JSON object"),
}
INVALID_DB_TYPE = {
	"code": BASE_ERROR_CODE | 2, "message": _('invalid db type'),
}
INVALID_STRING = {
	"code": BASE_ERROR_CODE | 3, "message": _('invalid string'),
}
INVALID_EMAIL = {
	"code" : BASE_ERROR_CODE | 4, "message": _('invalid email'),
}
INVALID_PASSWORD = {
	"code": BASE_ERROR_CODE | 5, "message": _('invalid password'),
}
INVALID_BOOL = {
	"code": BASE_ERROR_CODE | 6, "message" : _('invalid bool'),
}
WRONG_TYPE = {
	"code": BASE_ERROR_CODE | 7, "message" : _('wrong type'),
}
INVALID_FILE = {
	"code" : BASE_ERROR_CODE | 8, "message" : _('invalid file'),
}
INVALID_UPLOAD_FILE = {
	"code" : BASE_ERROR_CODE | 9, "message" : _('invalid upload file'),
}
INVALID_IP_ADDRESS = {
	"code" : BASE_ERROR_CODE | 10, "message" : _('invalid ip address'),
}
INVALID_REQUEST = {
	"code" : BASE_ERROR_CODE | 11, "message" : _('invalid request'),
}
INVALID_CUSTOM_REQUEST = {
	"code" : BASE_ERROR_CODE | 12, "message" : _('invalid custom request'),
}
INVALID_USERNAME = {
	"code" : BASE_ERROR_CODE | 13, "message" : _('invalid username'),
}
INVALID_MIX_TYPE = {
	"code" : BASE_ERROR_CODE | 15, "message" : _('invalid mix type'),
}
INVALID_REGEX = {
	"code" : BASE_ERROR_CODE | 16, "message" : _('invalid regex'),
}
INVALID_TYPE = {
	"code" : BASE_ERROR_CODE | 17, "message" : _('invalid type'),
}
QUERY_SET = {
	"code" : BASE_ERROR_CODE | 18, "message" : _('error processing queryset'),
}
NO_UNIQUE_STRING_FOUND = {
	"code" : BASE_ERROR_CODE | 19, "message" : _('No unique string found'),
}
NO_UNIQUE_RANDOM_FOUND = {
	"code" : BASE_ERROR_CODE | 20, "message" : _('no unique random found'),
}
ERROR_SENDING_REQUEST = {
	"code" : BASE_ERROR_CODE | 21, "message" : _('Error sending request'),
}
INVALID_URL = {
	"code" : BASE_ERROR_CODE | 22, "message" : _('Invalid url'),
}
INVALID_NUMBER = {
	"code" : BASE_ERROR_CODE | 23, "message" : _('invalid number'),
}
INVALID_DEVICE = {
	"code" : BASE_ERROR_CODE | 24, "message" : _('invalid device'),
}
NO_EMAIL_HANDLER_PROVIDED = {
	"code" : BASE_ERROR_CODE | 25, "message" : _('no email handler provided'),
}
ERROR_SENDING_REQUEST = {
	"code" : BASE_ERROR_CODE | 26, "message" : _('Error sending request'),
}
INVALID_GOOGLE_RECHAPTCHA = {
	"code" : BASE_ERROR_CODE | 27, "message" : _('Invalid recaptcha'),
}
INVALID_INTEGER = {
	"code" : BASE_ERROR_CODE | 28, "message" : _('Invalid integer'),
}
INVALID_FLOAT = {
	"code" : BASE_ERROR_CODE | 29, "message" : _('Invalid float'),
}
INVALID_DICT = {
	"code" : BASE_ERROR_CODE | 30, "message" : _('Invalid dictionary'),
}
INVALID_STRUCTURE = {
	"code" : BASE_ERROR_CODE | 31, "message" : _('Invalid structure'),
}
INVALID_OHM2_ADDRESS_LIGHT = {
	"code" : BASE_ERROR_CODE | 32, "message" : _('Invalid OHM2 address light'),
}
NO_UNIQUE_SLUG_FOUND = {
	"code" : BASE_ERROR_CODE | 33, "message" : _('No unique slug found'),
}