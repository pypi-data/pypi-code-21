from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, \
    PasswordChangeForm
from django.contrib.auth import password_validation
from django.utils.html import format_html
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import HTML, Div, Submit, BaseInput, Hidden, Field

from cosmicdb.models import User

class CosmicFormHelper(FormHelper):
    def __init__(
        self,
        form,
        no_submit_row=False,
        submit_row=None,
        submit_value=None,
        submit_classes=None,
        submit_div_classes=None,
        field_layout=(),
        *args,
        **kwargs
    ):
        super(CosmicFormHelper, self).__init__(*args, **kwargs)
        field_layout = field_layout
        if not field_layout:
            field_layout = tuple(field.name for field in form.visible_fields()) + tuple(field.name for field in form.hidden_fields())
        if submit_row is None and not no_submit_row:
            submit_value = submit_value
            if submit_value is None:
                submit_value = 'Save'
            submit_classes = submit_classes
            if submit_classes is None:
                submit_classes = ''
            submit_div_classes = submit_div_classes
            if submit_div_classes is None:
                submit_div_classes = ''
            submit_row = Div(Submit('save', submit_value, type='submit', css_class=submit_classes), css_class=submit_div_classes)
        if no_submit_row or submit_row is None:
            submit_row = Div()
        field_layout = Layout(
            *field_layout,
            submit_row,
        )
        self.layout = field_layout


class CosmicFormsetHelper(FormHelper):
    template = 'bootstrap3/table_inline_formset.html'

    def __init__(self, *args, **kwargs):
        super(CosmicFormsetHelper, self).__init__(*args, **kwargs)
        self.form_tag = False


class CosmicAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CosmicAuthenticationForm, self).__init__(*args, **kwargs)
        self.helper = CosmicFormHelper(self, submit_value='Sign In', submit_classes='btn-block btn-flat')


class CosmicSignupUserForm(forms.ModelForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if email == '' or email is None:
            raise forms.ValidationError('You must fill in your email address.')
        if User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError('This email is in use.')
        return email
    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 5:
            raise forms.ValidationError('Username must be 5 or more characters.')
        return username
    def clean_password(self):
        password = self.cleaned_data.get('password')
        self.instance.username = self.cleaned_data.get('username')
        password_validation.validate_password(password, self.instance)
        return password

    def __init__(self, *args, **kwargs):
        super(CosmicSignupUserForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput()
        self.helper = CosmicFormHelper(self, submit_value='Create account', submit_div_classes='box-footer')

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        help_items = [format_html('<li>{}</li>', help_text) for help_text in password_validation.password_validators_help_texts()]
        help_text_html = '<ul class="help-block">%s</ul>' % ''.join(help_items)
        help_texts = {
            'password': help_text_html,
        }


class CosmicPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(CosmicPasswordResetForm, self).__init__(*args, **kwargs)
        self.helper = CosmicFormHelper(self, submit_value='Send Reset Email', submit_classes='btn-block btn-flat')


class CosmicSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CosmicSetPasswordForm, self).__init__(*args, **kwargs)
        self.helper = CosmicFormHelper(self, submit_value='Reset Password', submit_classes='btn-block btn-flat')


class CosmicPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CosmicPasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = CosmicFormHelper(self, submit_value='Change password', submit_div_classes='box-footer')
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-4'
        self.helper.field_class = 'col-sm-6'
