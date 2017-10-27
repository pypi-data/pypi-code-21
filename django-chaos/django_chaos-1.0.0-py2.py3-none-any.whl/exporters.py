# coding: utf-8
"""
This module is responsible to export
tasks from projects, by user, by project
from the django models.
"""
from __future__ import unicode_literals
from collections import OrderedDict
import os
import codecs
import logging
import pyexcel
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.conf import settings
from rest_framework.reverse import reverse
from icalendar.cal import Event, Calendar
from icalendar import vCalAddress, vText
from .rest import Responses
logger = logging.getLogger(__name__)


class TaskExport(object):

    publish_url = True
    default_filename = None
    request = None
    content_type = 'text/text'

    def __init__(self,
                 publish_url=True,
                 default_filename='task-export.txt',
                 request=None):

        self.publish_url = publish_url
        self.default_filename = default_filename
        self.request = request

    def _get_task_url(self, task):

        if self.publish_url:
            return reverse('task-detail', kwargs={'pk': task.pk}, request=self.request)
        else:
            return ''

    def get_download_name(self, output_path):
        folder, filename = os.path.split(output_path)
        return filename

    def get_output_path(self):
        from .utils import get_output_path as op
        output_path = os.path.join(settings.MEDIA_ROOT, 'export', 'chaos')
        chaos_export_path = settings.CHAOS_EXPORT_PATH if hasattr(settings, 'CHAOS_EXPORT_PATH') else output_path
        return op(chaos_export_path, self.default_filename)

    def export(self, queryset):
        raise NotImplementedError

    def respond(self, queryset):
        raise NotImplementedError


class XLSXTaskExport(TaskExport):

    publish_url = True
    request = None
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    default_filename = 'tasks.xlsx'

    def __init__(self,
                 publish_url=True,
                 default_filename='tasks.xlsx',
                 request=None):
        super(XLSXTaskExport, self).__init__(
            publish_url=publish_url,
            default_filename=default_filename,
            request=request)

    def _serialize_task(self, task):
        parent = task.parent.id if task.parent else None
        created_by = task.created_by.username if task.created_by else None
        responsible = task.responsible.username if task.responsible else None
        description = task.description if task.description else None
        return OrderedDict([
            (_('id'), task.pk),
            (_('UUID'), str(task.uuid)),
            (_('URL'), self._get_task_url(task)),
            (_('Project'), task.project.name),
            (_('Created By'), created_by),
            (_('Date Created'), task.date_created),
            (_('Date Updated'), task.date_updated),
            (_('Name'), task.name),
            (_('Description'), description),
            (_('Parent'), parent),
            (_('Responsible'), responsible),
            (_('Status'), task.status.code),
            (_('Status Description'), task.status.description),
            (_('Weight'), task.weight),
            (_('Start Date'), task.start_date),
            (_('End Date'), task.end_date),
            (_('# Comments'), task.comments.all().count()),
            (_('# Children'), task.children.all().count())
        ])

    def export(self, queryset):

        records = [self._serialize_task(task) for task in queryset]
        output_path = self.get_output_path()
        pyexcel.save_as(
            records=records,
            dest_file_name=output_path,
            dest_sheet_name='tasks'
        )
        return output_path

    def respond(self, queryset):

        """
        Creates a response with
        the export content and returns it
        """
        try:
            logger.info('exporting tasks to xlsx')
            output = self.export(queryset)
            download_name = self.get_download_name(output)
            with open(output, 'rb') as outfile:
                response = HttpResponse(FileWrapper(outfile), content_type=self.content_type)  # noqa
                response['Content-Disposition'] = 'attachment; filename=%s' % download_name
                return response
        except Exception as ex:
            message = ex.message if hasattr(ex, 'message') else ''
            logger.error('error while exporting to xlsx. error: %s', message, exc_info=True)
            return Responses.server_error()


class ICALTaskExport(TaskExport):

    """
    Exports tasks to iCal
    """

    publish_url = True
    request = None
    content_type = 'text/calendar'
    default_filename = 'tasks.ics'

    def __init__(self,
                 publish_url=True,
                 default_filename='tasks.ics',
                 request=None):
        super(ICALTaskExport, self).__init__(
            publish_url=publish_url,
            default_filename=default_filename,
            request=request)

    def _create_attendee(self, user, role=None):

        if not role:
            role = 'REQ-PARTICIPANT'

        attendee = vCalAddress('MAILTO:{0}'.format(user.email))
        attendee.params['cn'] = vText(user.username)
        attendee.params['role'] = role
        return attendee

    def _create_event(self, task):
        event = Event()
        event.add('uid', task.uuid)
        event.add('summary', task.name)
        event.add('description', task.description)
        event.add('dtstamp', task.date_created)
        if self.publish_url:
            event.add('url', self._get_task_url(task))
        if task.start_date:
            event.add('dtstart', task.start_date)
        if task.end_date:
            event.add('dtend', task.end_date)

        already_included_users = []

        if task.created_by:
            organizer = self._create_attendee(task.created_by, 'CHAIR')
            event['organizer'] = organizer
            already_included_users.append(task.created_by.pk)

        if task.responsible and task.responsible != task.created_by:
            attendee = self._create_attendee(task.responsible)
            event.add('attendee', attendee)
            already_included_users.append(task.responsible.pk)

        if task.followers.all().count() > 0:
            for user in task.followers.all():
                if user.pk in already_included_users:
                    continue

                attendee = self._create_attendee(user)
                event.add('attendee', attendee)

        if task.tags.all().count() > 0:
            for tag in task.tags.all():
                event.add('categories', tag)
        return event

    def _create_calendar(self, project, queryset):
        prodid = settings.CHAOS_CALENDAR_PRODID if hasattr(settings, 'CHAOS_CALENDAR_PRODID') else 'chaoscal'
        cal_version = settings.CHAOS_CALENDAR_VERSION if hasattr(settings, 'CHAOS_CALENDAR_VERSION') else '2.0'
        cal = Calendar()
        cal.add('prodid', prodid)
        cal.add('version', cal_version)
        cal['summary'] = project.name
        for task in queryset:
            event = self._create_event(task)
            cal.add_component(event)
        return cal

    def export(self, queryset):
        # TODO: we need to make sure this works on python 2 as well!!!
        if queryset.count() <= 0:
            return None
        project = queryset[0].project
        calendar = self._create_calendar(project, queryset)
        output_path = self.get_output_path()
        with codecs.open(output_path, 'wb') as output_file:
            output_file.write(calendar.to_ical())
        return output_path

    def respond(self, queryset):
        # TODO: we need to make sure this works on python 2 as well!!!
        try:
            logger.info('exporting tasks to ical')

            output_file = self.export(queryset)
            with open(output_file, 'rb') as out:
                output = out.read()
            download_name = self.get_download_name(output_file)
            response = HttpResponse(content_type=self.content_type, charset='UTF-8')
            response['Content-Disposition'] = 'attachment; filename=%s' % download_name
            response.write(output)

            logger.info('exporting tasks to ical finished.')
            return response
        except Exception as ex:
            message = ex.message if hasattr(ex, 'message') else ''
            logger.error('error while exporting tasks to ical. error: %s', message, exc_info=True)  # noqa
            return Responses.server_error()
