from django.db import models


# Create your models here.
class Article(models.Model):
    code = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=64)
    content = models.TextField(max_length=10000)

    def __str__(self):
        return self.title


class Option(models.Model):
    type = models.CharField(max_length=64)
    value = models.CharField(max_length=64)

    class Meta:
        unique_together = ("type", "value")

    def __str__(self):
        return self.type + ' with ' + self.value


class Setting(models.Model):
    type = models.CharField(max_length=64)
    value = models.CharField(max_length=64)
    category = models.CharField(max_length=64)

    class Meta:
        unique_together = ("type", "value")

    def __str__(self):
        return self.type + ' with ' + self.value
