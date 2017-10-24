from django.contrib import admin
from django.contrib.admin import ModelAdmin

from automationcommon.models import Audit


class AuditAdmin(ModelAdmin):
    list_display = ('when', 'who', 'model', 'model_pk', 'field', 'old', 'new')


admin.site.register(Audit, AuditAdmin)
