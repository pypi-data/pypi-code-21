from django.db import models
from django.utils.translation import ugettext_lazy as _


class IndexedItem(models.Model):
    content_type_pk = models.BigIntegerField(
        help_text=_("The primary key of the referenced content type."),
    )

    instance_pk = models.BigIntegerField(
        help_text=_("The primary key of the referenced instance."),
    )

    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text=_("The date on which this entry was created."),
    )

    class Meta:
        ordering = ("-created", )
        unique_together = ("content_type_pk", "instance_pk",)
