from django.db import models
from django.utils import timezone


class SoftDeletableQuerySet(models.QuerySet):
    """
    QuerySet for SoftDeletableModel.
    """

    def delete(self, soft=True):
        if soft:
            return self.update(removed=timezone.now())
        return super().delete()

    def restore(self):
        return self.update(removed=None)

    def active(self):
        return self.filter(removed__isnull=True)

    def removed(self):
        return self.filter(removed__isnull=False)


SoftDeletableManager = SoftDeletableQuerySet.as_manager
