from __future__ import absolute_import, unicode_literals

import json
import os
import logging

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.db import models
from django.forms.fields import FileField
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from model_utils.managers import InheritanceManager

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.wagtailadmin.edit_handlers import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.wagtailadmin.utils import send_mail
from wagtail.wagtailforms.models import AbstractFormField, FORM_FIELD_CHOICES

from wapps.utils import timehash

from .forms import FormBuilder

log = logging.getLogger(__name__)


def file_url(filename):
    return os.path.join(settings.MEDIA_URL, filename)


class FormSubmission(models.Model):
    '''Stored Form submission data'''
    form_data = JSONField()
    form = models.ForeignKey('BaseForm', on_delete=models.CASCADE)
    submit_time = models.DateTimeField(verbose_name=_('submit time'), auto_now_add=True)

    def get_data(self):
        return json.loads(self.form_data)

    def __str__(self):
        return self.form_data

    class Meta:
        verbose_name = _('form submission')


class FormField(AbstractFormField):
    FORM_FIELD_CHOICES = list(FORM_FIELD_CHOICES) + [
        ('image', _('Upload Image')),
        ('file', _('File Upload'))
    ]
    field_type = models.CharField(
        verbose_name=_('field type'),
        max_length=16,
        choices=FORM_FIELD_CHOICES)
    form = ParentalKey('BaseForm', related_name='form_fields')

    admin_display = models.BooleanField(_('Show in admin'), default=False,
                                        help_text=_('Display this field in the admin'))
    admin_filter = models.BooleanField(_('Filterable'), default=False,
                                       help_text=_('Is this field filterable ?'))
    admin_search = models.BooleanField(_('Searchable'), default=False,
                                       help_text=_('Is this field searchable ?'))

    panels = AbstractFormField.panels + [FieldRowPanel([
        FieldPanel('admin_display', classname="col4"),
        FieldPanel('admin_filter', classname="col4"),
        FieldPanel('admin_search', classname="col4"),
    ])]


class BaseForm(ClusterableModel):
    name = models.CharField(_('Name'), max_length=255)
    store_submission = models.BooleanField(
        _('Store submissions'),
        default=False,
        help_text=_('Store all form submissions in the database. This has to comply with local privacy laws.')  # NOQA
    )
    button_label = models.CharField(_('Button label'),
                                    max_length=128,
                                    default=_('Submit'),
                                    help_text=_('Submit button label'))
    recaptcha = models.BooleanField(_('Enable reCaptcha'),
                                    default=True,
                                    help_text=_('Prevent submissions by non-humans'))
    success_message = models.CharField(
        _('Success message'),
        blank=True,
        max_length=255,
        help_text=_('An optional success message to show when the form has been succesfully submitted')  # NOQA
    )
    panels = [
        FieldPanel('name'),
        FieldPanel('store_submission'),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('recaptcha'),
        FieldPanel('button_label'),
    ]

    objects = InheritanceManager()

    class Meta:
        verbose_name = _('Form')
        verbose_name_plural = _('Forms')

    def __str__(self):
        return self.name

    def get_form_class(self):
        fb = FormBuilder(self.form_fields.all(), recaptcha=self.recaptcha)
        return fb.get_form_class()

    def get_form_parameters(self):
        return {}

    def get_form(self, *args, **kwargs):
        form_class = self.get_form_class()
        form_params = self.get_form_parameters()
        form_params.update(kwargs)

        return form_class(*args, **form_params)

    def save_file(self, file):
        root = settings.WAPPS_FORMS_UPLOAD_ROOT
        prefix = timehash(10)
        relative_filename = os.path.join(root, prefix, file.name)
        filename = os.path.join(settings.MEDIA_ROOT, relative_filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb+') as out:
            for chunk in file.chunks():
                out.write(chunk)
        return relative_filename

    def process_form_submission(self, form):
        cleaned_data = form.cleaned_data

        for name, field in form.fields.items():
            # if isinstance(field, WagtailImageField):
            #     image_file_data = cleaned_data[name]
            #     if image_file_data:
            #         ImageModel = get_image_model()
            #         image = ImageModel(
            #             file=cleaned_data[name],
            #             title=filename_to_title(cleaned_data[name].name),
            #             collection=self.upload_image_to_collection,
            #             # assumes there is always a user - will fail otherwise
            #             uploaded_by_user=form.user,
            #             )
            #         image.save()
            #         cleaned_data.update({name: image.id})
            #     else:
            #         # remove the value from the data
            #         del cleaned_data[name]

            if isinstance(field, FileField):
                filename = self.save_file(cleaned_data[name])
                cleaned_data[name] = filename

        if self.store_submission:
            return FormSubmission.objects.create(
                form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
                form=self)

    def add_to_context(self, ctx, form=None):
        ctx['formdef'] = self
        ctx['form'] = form or self.get_form()
        ctx['form_id'] = self.id
        ctx['button_label'] = self.button_label
        ctx['recaptcha'] = settings.RECAPTCHA_PUBLIC_KEY if self.recaptcha else False
        ctx['action_url'] = self.action_url
        return ctx

    @property
    def action_url(self):
        return reverse('wapps_forms_process', kwargs={'pk': self.id})


class EmailForm(BaseForm):
    '''A form sending emails on submission'''
    to_address = models.CharField(
        verbose_name=_('to address'), max_length=255, blank=True,
        help_text=_("Optional - form submissions will be emailed to these addresses. Separate multiple addresses by comma.") # NOQA
    )
    from_address = models.CharField(
        verbose_name=_('from address'), max_length=255, blank=True)
    subject = models.CharField(
        verbose_name=_('subject'), max_length=255, blank=True)

    class Meta:
        verbose_name = _('Email form')

    panels = BaseForm.panels + [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]

    def process_form_submission(self, form):
        super().process_form_submission(form)

        if self.to_address:
            self.send_form_mail(form)

    def send_form_mail(self, form):
        addresses = [x.strip() for x in self.to_address.split(',')]
        content = []
        for name, field in form.fields.items():
            data = form.cleaned_data.get(name)
            if name == 'recaptcha' or not data:
                continue
            content.append(
                field.label + ': ' + six.text_type(data))

        send_mail(
            self.subject, '\n'.join(content), addresses, self.from_address)
