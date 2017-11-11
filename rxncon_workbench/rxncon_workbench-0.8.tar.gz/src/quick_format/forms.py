from django import forms

from .models import Quick


class QuickForm(forms.ModelForm):
    class Meta:
        model = Quick
        fields = [
            "name",
            "quick_input",
            "comment",
        ]


class DeleteQuickForm(forms.ModelForm):
    class Meta:
        model = Quick
        fields = []
