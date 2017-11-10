from django.utils.translation import ugettext as _

BASE_ERROR_CODE = 499264

USER_ALREADY_LOGGED_IN = {
	"code" : BASE_ERROR_CODE | 1,
	"message" : _("The user is already logged in"),
}