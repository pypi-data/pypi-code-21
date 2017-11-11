from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify


class Rxncon_system(models.Model):
    project_name = models.CharField(max_length=120)
    project_id = models.IntegerField()
    project_type = models.CharField(max_length=5)
    slug = models.SlugField(blank=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    pickled_system = models.BinaryField()

    def __str__(self):
        return self.project_name

    def __unicode__(self):
        return self.project_name

    def get_pickled_system(self):
        return self.pickled_system


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.project_name)


pre_save.connect(pre_save_post_receiver, sender=Rxncon_system)
