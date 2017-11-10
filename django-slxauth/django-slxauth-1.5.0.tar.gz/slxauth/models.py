from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class AbstractSolarluxUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    Email and password are required. Other fields are optional.
    """
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required.'),
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )

    TITLE_CHOICES = (
        ('MR', _('Mr.')),
        ('MRS', _('Mrs.')),
    )

    title = models.CharField(_('title'), choices=TITLE_CHOICES, max_length=20, null=True, blank=True)
    first_name = models.CharField(_('first name'), max_length=30, null=True, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, null=True, blank=True)

    customer_no = models.IntegerField(_('customer no'), null=True, blank=True)
    customer_name = models.CharField(_('customer name'), max_length=200, null=True, blank=True)

    CUSTOMER_CATEGORY_CHOICES = (
        ('QUALITY_PARTNER', _('quality partner')),
        ('DEALER', _('dealer')),
        ('ARCHITECT_PLANNER', _('architect/planner')),
        ('HOUSING_SOCIETY', _('housing society')),
        ('PRIVATE_CUSTOMER', _('private customer')),
        ('OTHERS', _('others')),
    )

    customer_category = models.CharField(_('customer category'), choices=CUSTOMER_CATEGORY_CHOICES, max_length=200, null=True, blank=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    is_customer_admin = models.BooleanField(
        _('is customer admin'),
        default=False,
    )

    language = models.CharField(
        _('language'),
        max_length=2,
        null=True, blank=True)

    crm_contact_id = models.UUIDField(
        _('CRM contact id'),
        null=True, blank=True
    )

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    um_id = models.IntegerField(_('user management id'), null=True, blank=True)
    avatar_attachment_id = models.IntegerField(_('avatar attachment id'), null=True, blank=True)
    company_logo_attachment_id = models.IntegerField(_('company logo attachment id'), null=True, blank=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


