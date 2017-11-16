# -*- coding:utf8 -*-
# Author:DenisHuang
# Date:
# Usage:

from django.contrib import admin
from . import models


class MessageAdmin(admin.ModelAdmin):
    list_display = ('create_time', 'type', 'from_id', 'to_id', 'content')


admin.site.register(models.Message, MessageAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'openid', 'province', 'city', 'user')
    raw_id_fields = ('user',)


admin.site.register(models.User, UserAdmin)
