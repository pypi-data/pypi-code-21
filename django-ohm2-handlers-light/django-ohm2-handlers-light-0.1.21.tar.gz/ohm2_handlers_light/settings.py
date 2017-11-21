from django.conf import settings
from django.utils.translation import ugettext as _
import os


DEBUG = getattr(settings, 'DEBUG')
BASE_DIR = getattr(settings, 'DEBUG')
STRING_SINGLE = getattr(settings, 'STRING_SINGLE')
STRING_SHORT = getattr(settings, 'STRING_SHORT')
STRING_MEDIUM = getattr(settings, 'STRING_MEDIUM')
STRING_NORMAL = getattr(settings, 'STRING_NORMAL')
STRING_LONG = getattr(settings, 'STRING_LONG')
STRING_DOUBLE = getattr(settings, 'STRING_DOUBLE')
HOST = getattr(settings, 'HOST')
SUBDOMAINS = getattr(settings, 'SUBDOMAINS')
PROTOCOL = getattr(settings, 'PROTOCOL')
HOSTNAME = getattr(settings, 'HOSTNAME')
WEBSITE_URL = getattr(settings, 'WEBSITE_URL')
STATIC_URL = getattr(settings, 'STATIC_URL')
STATIC_ROOT = getattr(settings, 'STATIC_ROOT')
MEDIA_URL = getattr(settings, 'MEDIA_URL')
MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
ADMINS = getattr(settings, 'ADMINS', [])

APP = 'OHM2_HANDLERS_LIGHT_'

DEFAULT_EXCEPTION_CODE =  getattr(settings, APP + 'DEFAULT_EXCEPTION_CODE', -1)
DEFAULT_EXCEPTION_MESSAGE =  getattr(settings, APP + 'DEFAULT_EXCEPTION_CODE', _("Uncaught exception"))


DATEUTIL_ENABLED = getattr(settings, APP + 'DATEUTIL_ENABLED', False)

DETECT_DEVICE = getattr(settings, APP + 'DETECT_DEVICE', False)
DEVICE_IOS_NAME = getattr(settings, APP + 'IOS_NAME', "iOS")
DEVICE_ANDROID_NAME = getattr(settings, APP + 'ANDROID_NAME', "Android")
DEVICE_PC_NAME = getattr(settings, APP + 'PC_NAME', "Default")
SUPPORTED_DEVICES = (
	DEVICE_IOS_NAME.strip().lower(),
	DEVICE_ANDROID_NAME.strip().lower(),
	DEVICE_PC_NAME.strip().lower(),
)


DETECT_COUNTRY = getattr(settings, APP + 'DETECT_COUNTRY', False)
GEOIP_PATH = getattr(settings, APP + "GEOIP_PATH", os.path.join( os.path.dirname(os.path.realpath(__file__))) )
DETECT_LATITUDE_AND_LONGITUDE =  getattr(settings, APP + 'DETECT_LATITUDE_AND_LONGITUDE', False)

SAVE_SENT_EMAILS = getattr(settings, APP + 'SAVE_SENT_EMAILS', False)
MAILGUN_DOMAIN = getattr(settings, APP + 'MAILGUN_DOMAIN', None)
MAILGUN_API_KEY = getattr(settings, APP + 'MAILGUN_API_KEY', None)

CREATE_QR_CODES = getattr(settings, APP + 'CREATE_QR_CODES', False)
CREATE_BARCODES = getattr(settings, APP + 'CREATE_BARCODES', False)

ENCRYPTION_ENABLED = getattr(settings, APP + 'ENCRYPTION_ENABLED', False)
PILL_ENABLED = getattr(settings, APP + 'PILL_ENABLED', False)

UNIDECODE_ENABLED = getattr(settings, APP + 'UNIDECODE_ENABLED', False)
HTMLMIN_MINIFY_ENABLED = getattr(settings, APP + 'UNIDECODE_ENABLED', False)

FILE_UPLOAD_TEMP_DIR = settings.FILE_UPLOAD_TEMP_DIR

INCLUDE_GEOBASEMODEL = getattr(settings, APP + 'INCLUDE_GEOBASEMODEL', False)

DICT_STOP_WORD = getattr(settings, APP + 'DICT_STOP_WORD', "#;-|")

OHM2_ADDRESS_LIGHT_STRUCTURE = getattr(settings, APP + 'OHM2_ADDRESS_LIGHT_STRUCTURE', {
	"country": {
		"optional": False,
		"validation": (
			("dict", "country", ("alpha_2",)),
		),
	},
	"first_level": {
		"optional": True,
		"validation": (
			("string", "first_level", 0),
		),
	},
	"second_level": {
		"optional": True,
		"validation": (
			("string", "second_level", 0),
		),
	},
	"third_level": {
		"optional": True,
		"validation": (
			("string", "third_level", 0),
		),
	},
	"fourth_level": {
		"optional": True,
		"validation": (
			("string", "fourth_level", 0),
		),
	},
	"street": {
		"optional": True,
		"validation": (
			("string", "street", 0),
		),
	},
	"number": {
		"optional": True,
		"validation": (
			("string", "number", 0),
		),
	},
	"floor": {
		"optional": True,
		"validation": (
			("string", "floor", 0),
		),
	},
	"tower": {
		"optional": True,
		"validation": (
			("string", "tower", 0),
		),
	},
	"block": {
		"optional": True,
		"validation": (
			("string", "block", 0),
		),
	},
	"coordinates": {
		"optional": True,
		"validation": (
			("dict", "coordinates", ("latitude", "longitude")),
		),
	},
})


SLUGIFLY_ENABLED = getattr(settings, APP + 'SLUGIFLY_ENABLED', False)
