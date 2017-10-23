
import flatpages.translation

from django.apps import apps
from django.db import models
from django.contrib import admin

from modeltranslation.admin import TranslationAdmin

from flatpages.forms import FlatpageForm
from flatpages.models import FlatPage


class FlatPageAdmin(TranslationAdmin):

    form = FlatpageForm

    list_display = ['url', 'title', 'site']

    list_filter = ['site', 'registration_required']

    search_fields = ['url', 'title']

    def __init__(self, *args, **kwargs):

        if apps.is_installed('ckeditor_uploader'):
            from ckeditor_uploader.widgets import CKEditorUploadingWidget
            self.formfield_overrides = {
                models.TextField: {'widget': CKEditorUploadingWidget}
            }

        elif apps.is_installed('ckeditor'):
            from ckeditor.widgets import CKEditorWidget
            self.formfield_overrides = {
                models.TextField: {'widget': CKEditorWidget}
            }

        super(FlatPageAdmin, self).__init__(*args, **kwargs)


admin.site.register(FlatPage, FlatPageAdmin)
