import logging
from copy import deepcopy
from datetime import datetime, time, timedelta
from importlib import import_module
from pkgutil import walk_packages

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django.dispatch import Signal
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from jsonfield.fields import JSONField

from .base import BaseReport
from .conf import ORG_MODEL, REPORT_PACKAGES, TYPE_CHOICES
from .utils import hashed_upload_to

logger = logging.getLogger(__name__)
report_generated = Signal(providing_args=["report"])
REPORTS = {}

# Dynamically load reports
for pkg in REPORT_PACKAGES:
    path = import_module(pkg).__path__
    for loader, name, ispkg in walk_packages(path):
        mod = import_module(".".join([pkg, name]))
        for (name, cls) in mod.__dict__.items():
            if isinstance(cls, type) and issubclass(cls, BaseReport) \
                    and cls != BaseReport:
                report_id = cls.id.strip()
                if report_id in [""]:
                    continue
                if report_id in REPORTS.keys():
                    msg = "Report with id \"{0}\" already registered." \
                        .format(report_id)
                    logger.error(msg)
                    continue
                REPORTS[report_id] = cls


def report_upload_to(instance, filename):
    return hashed_upload_to('reports', instance.document, filename)


class BaseReportModel(models.Model):
    """
    Abstract Base Report Model for Report and ReportSchedule fields.
    Contains common columns.
    """

    REPORT_CHOICES = [(r.id, r.name) for r in REPORTS.values()]

    report = models.CharField(max_length=64, choices=REPORT_CHOICES)
    typ = models.CharField(max_length=32, choices=TYPE_CHOICES)
    organization = models.ForeignKey(ORG_MODEL)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True,
                                   null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    config = JSONField(blank=True, default={})
    emails = ArrayField(models.EmailField(max_length=255), blank=True,
                        null=True)

    class Meta:
        abstract = True


class Report(BaseReportModel):
    name = models.CharField(max_length=64, blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    document = models.FileField(upload_to=report_upload_to, blank=True,
                                null=True, max_length=1024)

    class Meta(object):
        verbose_name = "Report"
        verbose_name_plural = "Reports"

    def __unicode__(self):
        return u'{0} ({1})'.format(self.name, self.get_report_display())

    @property
    def generated(self):
        """
        Indicates that the document is generated
        """

        return bool(self.document)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self._run_instance_method('get_report_name')
        super(Report, self).save(*args, **kwargs)

    def schedule_document_generation(self):
        """
        Schedules a task to generate the document
        """

        from .tasks import generate_document

        if not self.generated:
            kwargs = {'report_id': self.pk}
            generate_document.apply_async(kwargs=kwargs, countdown=10)

    def generate_document(self):
        """
        Generate and save the document
        """

        content = self._run_instance_method('generate')
        name = self._run_instance_method('get_report_filename')

        # Setting save to false to avoid hashed_upload_to raising an exception
        # because of document not having an attached file.
        self.document.save(name, content, save=False)
        self.save()

        report_generated.send(sender=self.__class__, report=self)

    def _run_instance_method(self, method):
        kwargs = deepcopy(self.config)
        kwargs.update({
            'typ': self.typ,
            'start_datetime': self.start_datetime,
            'end_datetime': self.end_datetime,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'organization': self.organization,
        })
        instance = REPORTS[self.report]()
        return getattr(instance, method)(**kwargs)


class ReportSchedule(BaseReportModel):
    PERIOD_DAILY = 'daily'
    PERIOD_WEEKLY = 'weekly'
    PERIOD_MONTHLY = 'monthly'
    PERIOD_QUARTERLY = 'quarterly'
    PERIOD_YEARLY = 'yearly'

    PERIOD_CHOICES = (
        (PERIOD_DAILY, PERIOD_DAILY.title()),
        (PERIOD_WEEKLY, PERIOD_WEEKLY.title()),
        (PERIOD_MONTHLY, PERIOD_MONTHLY.title()),
        (PERIOD_QUARTERLY, PERIOD_QUARTERLY.title()),
        (PERIOD_YEARLY, PERIOD_YEARLY.title()),
    )

    periodic_task = models.ForeignKey(PeriodicTask, null=True, blank=True)
    schedule = JSONField(blank=True, default={})
    period = models.CharField(max_length=32, choices=PERIOD_CHOICES,
                              default=PERIOD_WEEKLY)

    def __unicode__(self):
        return '{}-{} ({})'.format(self.report, self.pk, self.organization.name)

    @classmethod
    def available_periods(cls):
        """
        Simple helper for getting available periods
        """

        return map(lambda x: x[0], cls.PERIOD_CHOICES)

    def set_periodic_task(self):
        """
        Removes existing periodic_task if exists and sets the new one.
        Creates the corresponding CrontabSchedule as well if needed.
        """

        if self.periodic_task:
            self.periodic_task.delete()

        schedule, __ = CrontabSchedule.objects.get_or_create(**self.schedule)

        task = 'reports.tasks.schedule_task'
        data = {
            'name': '{}_{}'.format(task, self.pk),
            'task': task,
            'enabled': True,
            'crontab': schedule,
            'kwargs': {
                'report_schedule_id': self.pk
            }
        }

        self.periodic_task, __ = PeriodicTask.objects.get_or_create(**data)
        self.save()

    def datetimes_by_period(self):
        """
        Constructs start_datetime and end_datetime based on a self.period
        Localizes start_datetime and end_datetime based on
            organization's timezone
        :return: start_datetime, end_datetime
        """

        today = datetime.combine(datetime.today().date(), time(0, 0, 0))

        if self.period == self.PERIOD_DAILY:
            # Yesterday
            start_datetime = today - timedelta(days=1)
            end_datetime = datetime.combine(start_datetime.date(),
                                            time(23, 59, 59))

        elif self.period == self.PERIOD_WEEKLY:
            # Last week starting from monday
            start_datetime = today - timedelta(days=7 + today.weekday())
            end_datetime = datetime.combine(
                (start_datetime + timedelta(days=6)).date(),
                time(23, 59, 59))
        elif self.period == self.PERIOD_MONTHLY:
            # Last Months start and end date
            current_month_start = today.replace(day=1)
            start_datetime = current_month_start - relativedelta(months=1)
            end_datetime = datetime.combine(
                (current_month_start - timedelta(days=1)).date(),
                time(23, 59, 59)
            )

        elif self.period == self.PERIOD_QUARTERLY:
            # Last quarter's start and end date
            year = today.year
            last_quarter = (today.month - 1) / 3
            if last_quarter == 0:
                # in this case it should be last year's Q4
                last_quarter = 4
                year -= 1

            # Getting start and end date of the last quarter
            start_date = datetime(year, 3 * last_quarter - 2, 1)
            end_date = datetime(year, 3 * last_quarter, 1) + \
                relativedelta(months=1) - timedelta(days=1)

            start_datetime = datetime.combine(start_date.date(), time(0, 0, 0))
            end_datetime = datetime.combine(end_date.date(), time(23, 59, 59))

        elif self.period == self.PERIOD_YEARLY:
            # Last year's start and end date
            last_year = today.year - 1
            start_datetime = datetime(last_year, 1, 1, 0, 0, 0)
            end_datetime = datetime(last_year, 12, 31, 23, 59, 59)
        else:
            return None, None

        start_datetime = self.organization.timezone.localize(start_datetime)
        end_datetime = self.organization.timezone.localize(end_datetime)

        return start_datetime, end_datetime

    def set_schedule(self):
        """
        Constructs crontab format schedule based on a period and stores
            it on schedule field
        """

        self.schedule = {
            'minute': '0'
        }
        if self.period == self.PERIOD_DAILY:
            # Runs every day at 6am
            self.schedule.update({
                'hour': '6',
                'day_of_week': '*',
                'day_of_month': '*',
                'month_of_year': '*'

            })
        elif self.period == self.PERIOD_WEEKLY:
            # Runs every Monday at 6am
            self.schedule.update({
                'hour': '6',
                'day_of_week': '1',
                'day_of_month': '*',
                'month_of_year': '*'

            })
        elif self.period == self.PERIOD_MONTHLY:
            # Runs every 1st day of a Month at 6am
            self.schedule.update({
                'hour': '6',
                'day_of_week': '*',
                'day_of_month': '1',
                'month_of_year': '*'

            })
        elif self.period == self.PERIOD_QUARTERLY:
            # Runs every 1st day of a quarter at 6am
            self.schedule.update({
                'hour': '6',
                'day_of_week': '*',
                'day_of_month': '1',
                'month_of_year': '*/3'

            })
        elif self.period == self.PERIOD_YEARLY:
            # Runs every 1st day of a year at 6am
            self.schedule.update({
                'hour': '6',
                'day_of_week': '*',
                'day_of_month': '1',
                'month_of_year': '1'

            })

        self.save()

    def schedule_report(self):
        """
        Creates `Report` instance and schedules it.
        """

        start_datetime, end_datetime = self.datetimes_by_period()

        data = {
            'report': self.report,
            'typ': self.typ,
            'organization': self.organization,
            'created_by': self.created_by,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'config': self.config,
            'emails': self.emails,
        }

        report = Report.objects.create(**data)
        report.schedule_document_generation()
