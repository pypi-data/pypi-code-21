from django.db import models
import random


class IDField(models.Field):

    def __init__(self, alphabet=None, readable=False, *args, **kwargs):
        self.max_length = kwargs.get('max_length', 10)
        self.readable = readable
        self.alphabet = alphabet
        if not self.alphabet:
            if self.readable:
                self.alphabet = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
            else:
                self.alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
        super(IDField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'char({})'.format(self.max_length)

    def pre_save(self, model_instance, add):
        value = super(IDField, self).pre_save(model_instance, add)
        if not value:
            value = ''
            for i in range(0, self.max_length): value += random.choice(self.alphabet)
            setattr(model_instance, self.attname, value)
        return value

    def formfield(self, **kwargs):
        return super(IDField, self).formfield(**kwargs)

    def deconstruct(self):
        return super(IDField, self).deconstruct()
