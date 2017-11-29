from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import AccountCreate, AccountDetails, AccountUpdate, PasswordReset, PasswordUpdate

urlpatterns = {
    url(r'^auth/', include('rest_framework_social_oauth2.urls'), name='lp_accounts_login'),
    url(r'^account$', AccountDetails.as_view(), name='lp_accounts_retrieve'),
    url(r'^account/create$', AccountCreate.as_view(), name='lp_accounts_create'),
    url(r'^account/update$', AccountUpdate.as_view(), name='lp_accounts_update'),
    url(r'^password-reset$', PasswordReset.as_view(), name='lp_accounts_password_reset'),
    url(r'^password-reset/verify', PasswordUpdate.as_view(), name='lp_accounts_password_update')
}

urlpatterns = format_suffix_patterns(urlpatterns)
