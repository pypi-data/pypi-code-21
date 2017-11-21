import logging
from django.db import models
from django.utils.translation import gettext as _


class EventLoggingModel(models.Model):
    LOG_LEVELS = (
        (logging.NOTSET, _('NotSet')),
        (logging.INFO, _('Info')),
        (logging.WARNING, _('Warning')),
        (logging.DEBUG, _('Debug')),
        (logging.ERROR, _('Error')),
        (logging.FATAL, _('Fatal')),
    )

    id = models.BigAutoField(primary_key=True)
    level = models.PositiveSmallIntegerField(choices=LOG_LEVELS, default=logging.INFO, db_index=True)
    actor = models.CharField(max_length=30, null=False)
    action = models.PositiveSmallIntegerField(null=True)
    target = models.CharField(max_length=100, null=True)
    payload = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_logging'
        app_label = 'event_logging'
