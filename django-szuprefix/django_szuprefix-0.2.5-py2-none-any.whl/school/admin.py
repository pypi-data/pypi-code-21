from django.contrib import admin
from django.contrib.contenttypes.fields import GenericRelation

from . import models


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'create_time')
    raw_id_fields = ('party',)
    search_fields = ("name",)
    readonly_fields = ('party',)


admin.site.register(models.School, SchoolAdmin)


class SessionAdmin(admin.ModelAdmin):
    list_display = ('school', "name")
    raw_id_fields = ("school",)
    search_fields = ("school__name",)


admin.site.register(models.Session, SessionAdmin)


class GradeAdmin(admin.ModelAdmin):
    list_display = ('school', "name")
    raw_id_fields = ("school",)
    search_fields = ("school__name",)

admin.site.register(models.Grade, GradeAdmin)


class ClazzAdmin(admin.ModelAdmin):
    list_display = ('school', "name")
    raw_id_fields = ("school", "entrance_session", "graduate_session", "primary_teacher", "grade")
    search_fields = ("school__name",)

admin.site.register(models.Clazz, ClazzAdmin)
