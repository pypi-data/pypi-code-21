from django.contrib import admin
from adminsortable.admin import SortableAdmin
from parler.admin import TranslatableAdmin
from .models import (
    FilterName,
    ObjectVendor,
    ObjectModel,
    ObjectGeneration,
    ObjectVariant,
    ObjectFilter,
)


class FilterNameAdmin(TranslatableAdmin, SortableAdmin):
    list_display = ('title', 'default')
    search_fields = ('translations__title',)


admin.site.register(FilterName, FilterNameAdmin)


class ObjectVendorAdmin(admin.ModelAdmin):
    list_display = ('title', 'added')
    search_fields = ('title',)


admin.site.register(ObjectVendor, ObjectVendorAdmin)


class ObjectModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'object_vendor', 'added')
    list_filter = ('object_vendor',)
    search_fields = ('title', 'object_vendor__title')
    raw_id_fields = ('object_vendor',)


admin.site.register(ObjectModel, ObjectModelAdmin)


class ObjectGenerationAdmin(admin.ModelAdmin):
    list_display = ('years', 'object_model', 'added')
    list_filter = ('object_model__object_vendor',)
    search_fields = ('title', 'object_model__title', 'object_model__object_vendor__title')
    raw_id_fields = ('object_model',)

    def years(self, obj) -> str:
        return str(obj)


admin.site.register(ObjectGeneration, ObjectGenerationAdmin)


class ObjectFilterInline(admin.TabularInline):
    model = ObjectFilter
    extra = 1


class ObjectVariantAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'object_generation',
        'slug',
        'added',
    )
    list_filter = ('object_generation__object_model__object_vendor',)
    search_fields = (
        'title',
        'object_generation__object_model__title',
        'object_generation__object_model__object_vendor__title',
    )
    raw_id_fields = ('object_generation',)
    inlines = [ObjectFilterInline]


admin.site.register(ObjectVariant, ObjectVariantAdmin)
