from django import forms

from .models import File


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = [
            "project_name",
            "file",
            "comment",
        ]


class DeleteFileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = []
