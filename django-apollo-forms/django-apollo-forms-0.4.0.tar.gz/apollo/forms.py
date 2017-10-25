from django import forms


class SubmissionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # apollo fields are the Apollo FormField objects defined in an Apollo Form object
        apollo_fields = kwargs.pop('apollo_fields', [])
        super(SubmissionForm, self).__init__(*args, **kwargs)

        for f in apollo_fields:
            field_kwargs = dict(
                required=f.is_required
            )

            if f.validation_rule == 'EMAIL':
                self.fields[f.name] = forms.EmailField(**field_kwargs)
            else:
                self.fields[f.name] = forms.CharField(**field_kwargs)
