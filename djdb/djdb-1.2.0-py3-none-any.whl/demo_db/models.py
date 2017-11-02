from django.db import models

class mymodel(models.Model):
    name = models.TextField()
    url = models.URLField()
