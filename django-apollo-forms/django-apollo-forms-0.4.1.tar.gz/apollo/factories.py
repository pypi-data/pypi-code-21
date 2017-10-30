import factory
from apollo import models


class FormFactory(factory.django.DjangoModelFactory):
    name = 'Test Form'

    class Meta:
        model = models.Form


class FormFieldTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FormFieldTemplate


class FormFieldFactory(factory.django.DjangoModelFactory):
    form = factory.SubFactory(FormFactory)
    template = factory.SubFactory(FormFieldTemplateFactory)

    class Meta:
        model = models.FormField


class FormSubmissionFactory(factory.django.DjangoModelFactory):
    form = factory.SubFactory(FormFactory)

    class Meta:
        model = models.FormSubmission