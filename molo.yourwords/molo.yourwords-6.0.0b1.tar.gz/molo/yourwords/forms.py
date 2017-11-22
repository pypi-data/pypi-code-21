from django import forms

from molo.yourwords.models import YourWordsCompetitionEntry


class CompetitionEntryForm(forms.ModelForm):
    terms_or_conditions_approved = forms.BooleanField(required=True)

    class Meta:
        model = YourWordsCompetitionEntry
        fields = ['story_name', 'story_text', 'terms_or_conditions_approved',
                  'hide_real_name']
