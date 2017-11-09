from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Container


NUM_COLUMNS = [
    (i, '%s' % i) for i in range(1, 13)
]


class ContainerPluginForm(forms.ModelForm):
    create = forms.ChoiceField(
        choices=[(0, '')] + NUM_COLUMNS,
        label=_('Create Cells'),
        help_text=_('Optionally create this number of cells'),
        initial=0
    )
    mobile_size = forms.ChoiceField(
        choices=NUM_COLUMNS, label=_('Mobile Cell Width'),
        help_text=('Width of created cells on a mobile device.  '
                   '12 is full page width. '
                   'You can still change this later.'),
        initial=12
    )
    desktop_size = forms.ChoiceField(
        choices=NUM_COLUMNS, label=_('Desktop Cell Width'),
        help_text=('Width of created cells on a desktop.  '
                   '12 is full page width. '
                   'You can still change this later.'),
        initial=12
    )


    class Meta:
        model = Container
        exclude = ('page', 'position', 'placeholder', 'language', 'plugin_type')
