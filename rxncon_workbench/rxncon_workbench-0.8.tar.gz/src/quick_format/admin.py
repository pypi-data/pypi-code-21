from django.contrib import admin

from .models import Quick


class QuickModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "updated", "timestamp", "loaded"]
    list_display_links = ["__str__"]
    list_filter = ["updated", "timestamp"]
    search_fields = ["__str__", "content"]

    class Meta:
        model = Quick


admin.site.register(Quick, QuickModelAdmin)
