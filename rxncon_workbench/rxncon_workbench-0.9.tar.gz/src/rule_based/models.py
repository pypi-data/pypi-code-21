from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify


def upload_location(instance, filename):
    return "%s/%s/%s" % (instance.slug, "graphs", filename)


class Rule_based_from_rxnconsys(models.Model):
    project_name = models.CharField(max_length=120)
    slug = models.SlugField(blank=True)
    comment = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)  # initial timestamp will be saved one time
    updated = models.DateTimeField(auto_now=True,
                                   auto_now_add=False)  # auto_now refers to every modification, updated gets reset when Post is updated -duh
    # rxncon2bngl
    model_path = models.FileField(null=True)

    def __str__(self):
        return self.project_name

    def __unicode__(self):
        return self.project_name

    def get_model_filename(self):
        return str(self.model_path.name).split("/")[-1]

    def get_project_slug(self):
        return self.slug

    def get_relative_model_path(self):
        return str(self.model_path).split("/media_cdn/")[-1]

    def get_model_download_url(self):
        media_url = settings.MEDIA_URL
        return media_url + "%s" % (self.get_relative_model_path())

    class Meta:
        ordering = ["-updated", "-timestamp"]


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.project_name)


pre_save.connect(pre_save_post_receiver, sender=Rule_based_from_rxnconsys)
