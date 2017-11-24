from django import forms
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import User


class RegisterForm(UserCreationForm):
    """
    Main form for registration. Extends base Django`s
    ``UserCreationForm`` by including also email.
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class PasswordResetFormWithEmailExistenceCheck(PasswordResetForm):
    """
    Adding verification that the user exists in the database to PasswordResetForm.

    https://github.com/django/django/blob/master/django/contrib/auth/views.py
    """

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise ValidationError(_("Email does not exists"))
        return email
