from django.contrib import admin

from .models import File


class FileModelAdmin(admin.ModelAdmin):
    list_display = ["id", "__str__", "updated", "timestamp", "loaded"]
    list_display_links = ["__str__"]
    list_filter = ["updated", "timestamp"]
    search_fields = ["__str__", "content"]

    class Meta:
        model = File


admin.site.register(File, FileModelAdmin)
