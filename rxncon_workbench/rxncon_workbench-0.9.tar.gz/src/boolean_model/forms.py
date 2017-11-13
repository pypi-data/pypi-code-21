from django import forms

from .models import Bool_from_rxnconsys


class BoolForm(forms.ModelForm):
    class Meta:
        model = Bool_from_rxnconsys
        fields = [
            "comment",
            "smoothing",
            "knockout",
            "overexpr",
            "k_plus",
            "k_minus"
        ]


class DeleteBoolForm(forms.ModelForm):
    class Meta:
        model = Bool_from_rxnconsys
        fields = []
