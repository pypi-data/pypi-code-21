from django.contrib import admin
from django.contrib.contenttypes.fields import GenericRelation

from . import models


class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'is_active', 'slug', 'create_time')


admin.site.register(models.Party, PartyAdmin)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "party", "path")
    raw_id_fields = ("party", "parent")
    list_filter = ("party",)
    search_fields = ("name",)
    readonly_fields = ("path",)


admin.site.register(models.Department, DepartmentAdmin)


class WorkerAdmin(admin.ModelAdmin):
    list_display = ('name', 'party', 'position', 'is_active', 'create_time')
    raw_id_fields = ('party', 'departments', 'user')


admin.site.register(models.Worker, WorkerAdmin)
