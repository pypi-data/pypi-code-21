from django.contrib import admin
from . import models


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'city', 'create_time')
    search_fields = ('name',)

admin.site.register(models.Person, PersonAdmin)

