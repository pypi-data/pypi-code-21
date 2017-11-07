# -*- coding: utf-8 -*-
from django.db import models
from pages.utils.database import AuditableMixin


class Product(AuditableMixin):
    page = models.ForeignKey('Page')
    reference_id = models.CharField(max_length=40)

    def __str__(self):
        return self.reference_id

    class Meta:
        db_table = 'products'
        unique_together = ('page', 'reference_id')
