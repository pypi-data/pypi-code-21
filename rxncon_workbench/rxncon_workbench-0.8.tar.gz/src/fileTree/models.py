import os
import shutil

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
try:
    from graphs.models import Graph_from_File
    from boolean_model.models import Bool_from_rxnconsys
    from rule_based.models import Rule_based_from_rxnconsys
    from rxncon_system.models import Rxncon_system

except ImportError:

    from src.graphs.models import Graph_from_File
    from src.boolean_model.models import Bool_from_rxnconsys
    from src.rule_based.models import Rule_based_from_rxnconsys
    from src.rxncon_system.models import Rxncon_system


def upload_location(instance, filename):
    return "%s/%s" % (instance.slug, filename)


class File(models.Model):
    project_name = models.CharField(max_length=120)
    loaded = models.BooleanField(default=False)
    slug = models.SlugField(blank=True)
    file = models.FileField(upload_to=upload_location, null=False, blank=False)
    comment = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)  # initial timestamp will be saved one time
    updated = models.DateTimeField(auto_now=True,
                                   auto_now_add=False)  # auto_now refers to every modification, updated gets reset when Post is updated -duh
    rxncon_system = models.OneToOneField(Rxncon_system, null=True, on_delete=models.SET_NULL, blank=True, unique=True,
                                         related_name="rxncon_system_file")  # pickled object hold here
    reg_graph = models.ForeignKey(Graph_from_File, null=True, on_delete=models.SET_NULL, blank=True,
                                  related_name="regulatory_graph_file")
    rea_graph = models.ForeignKey(Graph_from_File, null=True, on_delete=models.SET_NULL, blank=True,
                                  related_name="reaction_graph_file")
    sRea_graph = models.ForeignKey(Graph_from_File, null=True, on_delete=models.SET_NULL, blank=True,
                                   related_name="species reaction_graph_file+")
    boolean_model = models.ForeignKey(Bool_from_rxnconsys, null=True, on_delete=models.SET_NULL, blank=True,
                                      related_name="bool_file")
    rule_based_model = models.ForeignKey(Rule_based_from_rxnconsys, null=True, on_delete=models.SET_NULL, blank=True,
                                         related_name="rule_based_file")

    def __str__(self):
        return self.file.name

    def __unicode__(self):
        return self.file.name

    def load(self):
        return reverse("fileTree:load", kwargs={"id": self.id})

    def get_filename(self):
        return str(self.file.name).split("/")[-1]

    def get_project_slug(self):
        return self.slug

    def get_absolute_url(self):
        return reverse("fileTree:detail", kwargs={"id": self.id})

    def upload_new_version(self):
        return reverse("fileTree:upload", kwargs={"slug": self.slug, })

    def get_download_url(self):
        media_url = settings.MEDIA_URL
        return media_url + "%s" % (self.file)

    def get_absolute_path(self):
        media_root = settings.MEDIA_ROOT
        return media_root + "/%s" % (self.file)

    def delete_file_from_harddisk(self):
        path = self.get_absolute_path()
        if os.path.exists(path):
            path = os.path.dirname(path)
            shutil.rmtree(path)

    def delete_project_from_harddisk(self):
        path = self.get_absolute_path()
        if os.path.exists(path):
            path = os.path.dirname(path)
            shutil.rmtree(path)

    class Meta:
        ordering = ["-updated", "-timestamp"]


def create_slug(instance, new_slug=None):
    slug = slugify(instance.project_name)


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.project_name)


pre_save.connect(pre_save_post_receiver, sender=File)
