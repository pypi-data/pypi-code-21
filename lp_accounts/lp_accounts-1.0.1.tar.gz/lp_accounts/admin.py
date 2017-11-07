from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.urlresolvers import reverse
from .models import User


class UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'type', 'account')

    def account(self, obj):
        account = obj.account
        if account:
            url = reverse('admin:%s_%s_change' % (account._meta.app_label, account._meta.model_name), args=[account.id])
            return u'<a href="%s">Edit %s</a>' % (url, account)

        return account

    account.allow_tags = True

UserAdmin.fieldsets += (
    ('Additional Data', {'fields': ('type',)}),
)
admin.site.register(User, UserAdmin)
