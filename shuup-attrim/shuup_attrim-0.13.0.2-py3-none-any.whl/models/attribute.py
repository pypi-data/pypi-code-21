from django.db import models

from shuup.core.models import Product as ShuupProduct

from attrim.models.cls import Class


class Attribute(models.Model):
    product = models.ForeignKey(
        ShuupProduct,
        related_name='attrim_attrs',
        related_query_name='attrim_attr',
        on_delete=models.CASCADE,
    )
    cls = models.ForeignKey(
        Class,
        related_name='attributes',
        related_query_name='attribute',
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ('cls', 'product')
