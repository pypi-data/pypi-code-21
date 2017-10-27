# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from .models import TaskStatus


def create_task_status(apps=None, schema_editor=None):

    """
    Creates the default task statuses
    """
    TaskStatus.objects.get_or_create(
        code='OPEN',
        description=_('Open'),
        is_system_status=True,
        is_closing_status=False,
        color='#FF4257'
    )
    TaskStatus.objects.get_or_create(
        code='CLOSED',
        description=_('Closed'),
        is_system_status=True,
        is_closing_status=True,
        color='#36BC29'
    )
