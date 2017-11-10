from django.utils.translation import ugettext as _

BASE_ERROR_CODE = 57664

INVALID_NOTIFICATION_STATUS_CODE = {
	"code" : BASE_ERROR_CODE | 1, "message" : _("Invalid notification status code"),
}