from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group as DjangoGroup

from .models import Group, User


admin.site.unregister(DjangoGroup)
admin.register(Group)(GroupAdmin)

admin.register(User)(UserAdmin)
