from django.db import models


class AuditTrailModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.UUIDField(blank=True, null=True)
    modified_by = models.UUIDField(blank=True, null=True)

    class Meta:
        abstract = True
        get_latest_by = "modified_at"
