from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields as generic


class LaporemImage(models.Model):
    file = models.ImageField(null=True, verbose_name='Файл', upload_to='laporem_image')
    content_type = models.ForeignKey(ContentType, editable=False)
    content_object = generic.GenericForeignKey()
    object_id = models.TextField(null=True, editable=False)
    weight = models.IntegerField(default=0, verbose_name="Вес", editable=False)
    unique = models.CharField(max_length=200, null=True, blank=True, editable=False)

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        obni = self._meta.model.objects.filter(object_id=self.object_id).order_by("-weight")[:1]
        if obni.count() > 0:
            weight = obni.get().weight + 1
            self.weight = weight
        else:
            self.weight = 0
        return super(LaporemImage,self).save(force_insert, force_update, using, update_fields)