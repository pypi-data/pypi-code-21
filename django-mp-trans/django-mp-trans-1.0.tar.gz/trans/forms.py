
from django import forms


class TranslateForm(forms.Form):

    text = forms.CharField(max_length=10000, required=True)

    src = forms.CharField(required=True, max_length=2)

    dst = forms.CharField(required=True, max_length=2)

