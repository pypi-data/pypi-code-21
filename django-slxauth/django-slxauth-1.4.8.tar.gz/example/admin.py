from django.contrib import admin

# Register your models here.
from django.contrib.auth import get_user_model

from slxauth.admin import SolarluxUserAdmin

admin.site.register(get_user_model())

