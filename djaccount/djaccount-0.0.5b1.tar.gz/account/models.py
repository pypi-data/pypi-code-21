"""
Look at this: https://docs.djangoproject.com/en/1.11/topics/auth/customizing/
"""
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.urls.base import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .managers import AccountManager


class Account(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.')
                                   )
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as active.'
                                                ' Unselect this instead of deleting accounts.')
                                    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')

    def get_absolute_url(self):
        return reverse('account:view-one', None, (self.id,))

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '{first_name} {last_name}'.format(first_name=self.first_name, last_name=self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def __str__(self):
        return self.get_full_name() or self.get_username()


class EmailValidation(models.Model):
    account = models.ForeignKey(Account, related_name='email_validations')
    email = models.CharField(max_length=254)
    key = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    class Meta:
        indexes = [
            models.Index(fields=['account', 'email'], name='account_email_idx'),
            models.Index(fields=['key'], name='key_idx'),
        ]
