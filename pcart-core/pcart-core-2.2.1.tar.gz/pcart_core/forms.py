from django import forms
from django_ace import AceWidget
from django.utils.translation import ugettext_lazy as _
from .models import ThemeSettings, RootFile


class EditRootFileForm(forms.ModelForm):
    content = forms.CharField(
        label=_('Content'),
        widget=AceWidget(
            wordwrap=False,
            width="100%",
            height="300px",
            showprintmargin=True))

    class Meta:
        model = RootFile
        fields = '__all__'


class EditThemeSettingsDataForm(forms.ModelForm):
    class Meta:
        model = ThemeSettings
        fields = '__all__'


class EditThemeSettingsForm(forms.ModelForm):
    class Meta:
        model = ThemeSettings
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditThemeSettingsForm, self).__init__(*args, **kwargs)
        self.images_ids = []
        self.old_data = {}
        if 'instance' in kwargs:
            self.obj = kwargs['instance']
            if self.obj is not None:
                self.settings_fields = self.obj.get_settings_fields()
                self.old_data = self.obj.data
                for group in self.settings_fields:
                    for o in group['settings']:
                        if o['type'] in ['checkbox']:
                            self.fields[o['id']] = forms.BooleanField(required=False)
                        elif o['type'] in ['radio', 'select', 'text', 'collection', 'textarea', 'color', 'blog', 'link_list']:
                            self.fields[o['id']] = forms.CharField(required=False)
                        elif o['type'] in ['image']:
                            self.fields[o['id']] = forms.ImageField(required=False)
                            if 'current' in self.obj.data and self.obj.data['current'].get(o['id']):
                                self.images_ids.append(o['id'])

    def save(self, commit=True):
        from django.core.files.uploadedfile import UploadedFile
        instance = super(EditThemeSettingsForm, self).save(commit=False)

        _old_current = self.old_data.get('current', {})
        _current = dict()

        for i in self.images_ids:
            if i in _old_current:
                _current[i] = _old_current[i]

        for k, v in self.cleaned_data.items():
            if k not in ['site', 'data']:
                if issubclass(type(v), UploadedFile):
                    _current[k] = k
                else:
                    if k not in self.images_ids:
                        _current[k] = v
                    elif v is False:
                        del _current[k]
        instance.data['current'] = _current
        if commit:
            instance.save()
        return instance

