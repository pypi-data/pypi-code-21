
from django import forms

from poll.models import Vote


class VoteForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(VoteForm, self).__init__(*args, **kwargs)

        poll = self.initial.get('poll')

        if poll:
            self.fields['choice'] = forms.ModelChoiceField(
                empty_label=None, queryset=poll.choices.all(),
                widget=forms.RadioSelect)

    class Meta:
        model = Vote
        fields = ['poll', 'choice']
        widgets = {
            'poll': forms.HiddenInput
        }
