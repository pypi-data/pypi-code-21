from . import models
from django.contrib import admin



class PageAdmin(admin.ModelAdmin):
    list_display = ['name', 'title']

admin.site.register(models.Page, PageAdmin)

