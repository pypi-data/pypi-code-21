from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from account.models import Account


class AccountCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and password.
    """
    class Meta:
        model = Account
        fields = ('email', 'first_name', 'last_name')


class AccountChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all the fields on the user,
    but replaces the password field with admin's password hash display field.
    """
    class Meta:
        model = Account
        fields = ('email', 'first_name', 'last_name')
