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


class Quick(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(blank=True)
    loaded = models.BooleanField(default=False)
    quick_input = models.TextField(null=False)
    comment = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)  # initial timestamp will be saved one time
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)  # auto_now refers to every modification,
    # updated gets reset when Post is updated
    rxncon_system = models.OneToOneField(Rxncon_system, null=True, on_delete=models.SET_NULL, blank=True, unique=True,
                                         related_name="rxncon_system_quick")  # pickled object hold here
    reg_graph = models.ForeignKey(Graph_from_File, null=True, on_delete=models.SET_NULL, blank=True,
                                  related_name="regulatory_graph_quick")
    rea_graph = models.ForeignKey(Graph_from_File, null=True, on_delete=models.SET_NULL, blank=True,
                                  related_name="reaction_graph_quick")
    sRea_graph = models.ForeignKey(Graph_from_File, null=True, on_delete=models.SET_NULL, blank=True,
                                   related_name="species reaction_graph_quick+")
    boolean_model = models.ForeignKey(Bool_from_rxnconsys, null=True, on_delete=models.SET_NULL, blank=True,
                                      related_name="bool_quick")
    rule_based_model = models.ForeignKey(Rule_based_from_rxnconsys, null=True, on_delete=models.SET_NULL, blank=True,
                                         related_name="rule_based_quick")

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.slug

    def load(self):
        return reverse("quick_format:quick_load", kwargs={"id": self.id})

    def get_filename(self):
        # no real functionality in quick object, as these do not come from uploaded files
        return self.name

    def get_absolute_url(self):
        return reverse("quick_format:quick_detail", kwargs={"id": self.id})


    def get_download_url(self):
        media_url = settings.MEDIA_URL
        filename = self.slug + "_quick_definition.txt"
        return "%s%s/%s/%s" % (media_url, self.slug, "description", filename)

    def delete_from_harddisk(self):
        media_root = settings.MEDIA_ROOT
        filename = self.slug + "_quick_definition.txt"
        path = "%s/%s/" % (media_root, self.slug)
        if os.path.exists(path):
            shutil.rmtree(path)


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)


pre_save.connect(pre_save_post_receiver, sender=Quick)
