from django import forms

from .models import Rule_based_from_rxnconsys


class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule_based_from_rxnconsys
        fields = [
            "comment"
        ]


class DeleteRuleForm(forms.ModelForm):
    class Meta:
        model = Rule_based_from_rxnconsys
        fields = []
