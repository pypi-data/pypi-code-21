from django.contrib import admin

from .models import Rule_based_from_rxnconsys


class RuleBasedFromRxnconsysModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "model_path", "updated", "timestamp"]
    list_display_links = ["__str__"]
    list_filter = ["updated", "timestamp"]
    search_fields = ["__str__", "content"]

    class Meta:
        model = Rule_based_from_rxnconsys


admin.site.register(Rule_based_from_rxnconsys, RuleBasedFromRxnconsysModelAdmin)
