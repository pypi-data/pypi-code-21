# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Used to make sure only one database row is created, not more
def validate_only_one_instance(obj):
    model = obj.__class__
    if (model.objects.count() > 0 and
            obj.id != model.objects.get().id):
        raise ValidationError("You cannot create more than 1 %s row, please edit the old one" % model.__name__)
# Example code..
""" 
def clean(self):
    validate_only_one_instance(self)
"""

# Models
class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()

    # def save(self, *args, **kwargs):
    #     message_body = self.name + " : " + self.phone_number + " : " + self.how_you_feel
    #     send_mail(
    #         'New contact request',
    #         message_body,
    #         'info@at-home-doc.com',
    #         ['info@at-home-doc.com'],
    #         fail_silently=False,
    #     )
    #     super(Contact, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.name

class Page(models.Model):
    name = models.CharField(max_length=255)

class Component(models.Model):
    name = models.CharField(max_length=255)
    page = models.ForeignKey(Page, related_name="components", on_delete=models.CASCADE)

class gTitle(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    component = models.ForeignKey(Component, related_name="titles", on_delete=models.CASCADE)

class gTextbox(models.Model):
    name = models.CharField(max_length=255)
    value = models.TextField()
    component = models.ForeignKey(Component, related_name="textboxs", on_delete=models.CASCADE)
