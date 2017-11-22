from django.db import models

class task(models.Model):
    description = models.CharField(null=True, blank=True, max_length=100)
    percent = models.IntegerField(null=True, blank=True, max_length=100)


