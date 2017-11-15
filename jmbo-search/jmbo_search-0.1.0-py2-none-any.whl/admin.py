from django.contrib import admin

from jmbo.admin import ModelBaseAdmin
from search.models import IndexedItem


admin.site.register(IndexedItem)
