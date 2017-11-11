from django import forms

from .models import Graph_from_File


class regGraphFileForm(forms.ModelForm):
    class Meta:
        model = Graph_from_File
        fields = [
            "comment",
        ]


class reaGraphFileForm(forms.ModelForm):
    class Meta:
        model = Graph_from_File
        fields = [
            "comment",
        ]


class DeleteGraphForm(forms.ModelForm):
    class Meta:
        model = Graph_from_File
        fields = []
