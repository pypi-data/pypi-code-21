from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import AccountCreate, AccountRetrieveUpdateDestroy, AccountUploadView, PasswordReset, PasswordUpdate

urlpatterns = {
    url(r'^account/create$', AccountCreate.as_view(), name='lp_accounts_create'),
    url(r'^auth/', include('rest_framework_social_oauth2.urls'), name='lp_accounts_login'),
    url(r'^me$', AccountRetrieveUpdateDestroy.as_view(), name='lp_accounts_retrieveupdatedestroy'),
    url(r'^me/upload$', AccountUploadView.as_view(), name='lp_accounts_upload'),
    url(r'^password-reset$', PasswordReset.as_view(), name='lp_accounts_password_reset'),
    url(r'^password-reset/verify', PasswordUpdate.as_view(), name='lp_accounts_password_update')
}

urlpatterns = format_suffix_patterns(urlpatterns)
