from django.contrib import admin

from .models import Bool_from_rxnconsys


class BoolFromRxnconsysModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "model_path", "symbol_path", "init_path", "updated", "timestamp"]
    list_display_links = ["__str__"]
    list_filter = ["updated", "timestamp"]
    search_fields = ["__str__", "content"]

    class Meta:
        model = Bool_from_rxnconsys


admin.site.register(Bool_from_rxnconsys, BoolFromRxnconsysModelAdmin)
