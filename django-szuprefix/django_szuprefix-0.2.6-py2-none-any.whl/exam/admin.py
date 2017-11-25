from django.contrib import admin

from . import models


class PaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'create_time')
    raw_id_fields = ('party',)
    search_fields = ("title",)
    readonly_fields = ('party',)


admin.site.register(models.Paper, PaperAdmin)

