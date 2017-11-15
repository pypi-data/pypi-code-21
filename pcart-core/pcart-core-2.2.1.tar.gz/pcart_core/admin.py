from django.contrib import admin
from .models import ThemeSettings, RootFile
from .forms import EditThemeSettingsForm, EditThemeSettingsDataForm, EditRootFileForm


class ThemeSettingsAdmin(admin.ModelAdmin):
    list_display = ('site', 'added', 'changed')
    search_fields = ['site']

    def get_form(self, request, obj=None, **kwargs):
        if obj is not None:
            if request.GET.get('rawjson', 'no') == 'yes':
                kwargs['form'] = EditThemeSettingsDataForm
                self.exclude = None
            else:
                kwargs['form'] = EditThemeSettingsForm
                self.exclude = ('data',)
        return super(ThemeSettingsAdmin, self).get_form(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ['site']
        else:
            return []

    def change_view(self, request, object_id, form_url='', extra_context=None):
        from django.core.files.storage import default_storage
        extra_context = extra_context or {}

        result = super(ThemeSettingsAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

        if object_id and request.method == 'POST':
            _old_instance = ThemeSettings.objects.get(pk=object_id)
            for filename in request.FILES:
                f = request.FILES[filename]
                fullpath = _old_instance.get_upload_path(filename)
                if default_storage.exists(fullpath):
                    default_storage.delete(fullpath)
                default_storage.save(fullpath, f)
            for k, v in request.POST.items():
                if k.endswith('-clear'):
                    filename = k[:-len('-clear')]
                    if v == 'on':
                        fullpath = _old_instance.get_upload_path(filename)
                        if default_storage.exists(fullpath):
                            default_storage.delete(fullpath)
        return result


admin.site.register(ThemeSettings, ThemeSettingsAdmin)


class RootFileAdmin(admin.ModelAdmin):
    form = EditRootFileForm
    list_display = ('file_name', 'site', 'content_type', 'published', 'changed')
    search_fields = ('file_name', 'content')
    date_hierarchy = 'added'


admin.site.register(RootFile, RootFileAdmin)
