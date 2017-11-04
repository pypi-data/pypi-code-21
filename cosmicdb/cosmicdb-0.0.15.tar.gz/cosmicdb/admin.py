from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from cosmicdb.models import User, UserSystemMessage, UserSystemNotification


class UserSystemMessageInlineAdmin(admin.TabularInline):
    model = UserSystemMessage


class UserSystemNotificationInlineAdmin(admin.TabularInline):
    model = UserSystemNotification


class UserProfileAdmin(UserAdmin):
    inlines = [
        UserSystemMessageInlineAdmin,
        UserSystemNotificationInlineAdmin,
    ]


admin.site.register(User, UserProfileAdmin)
