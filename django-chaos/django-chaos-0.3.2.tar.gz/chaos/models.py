# -*- coding: utf-8 -*-
import uuid
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from recurrence.fields import RecurrenceField
from mptt.models import MPTTModel, TreeForeignKey
from common.models import (
    CreatedByMixIn,
    DateCreatedMixIn,
    DateUpdatedMixIn,
    DateRangeMixIn,
    DomainModelMixIn,
)
from dirtyfields import DirtyFieldsMixin
from colorfield.fields import ColorField
from file_context.managers import Files
from taggit.managers import TaggableManager
from .scores import (
    calculate_project_score,
    calculate_node_score
)


def default_task_status():
    """
    returns the default status
    for tasks
    """
    try:
        return TaskStatus.objects.get(code='OPEN')
    except:
        return None


@python_2_unicode_compatible
class ProjectType(CreatedByMixIn,
                  DomainModelMixIn):

    """
    Models a ProjectType. Right now it's a simple FK, but later on
    we can have several different rules/behavior for different project
    types.
    """

    def __str__(self):

        return self.code

    class Meta:
        verbose_name = _('Project Type')
        verbose_name_plural = _('Project Types')


@python_2_unicode_compatible
class Project(CreatedByMixIn,
              DateCreatedMixIn,
              DateUpdatedMixIn):

    """
    Project. This model is the container for all tasks.
    """

    name = models.CharField(
        max_length=64,
        verbose_name=_('Project'),
    )

    type = models.ForeignKey(
        ProjectType,
        verbose_name=_('Type')
    )

    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='projects',
        null=True
    )

    description = models.TextField(
        verbose_name=_('Description'),
        null=True
    )

    template = models.BooleanField(
        verbose_name=_('Is Template?'),
        default=False
    )

    files = Files()

    tags = TaggableManager()

    @property
    def root_tasks(self):
        """
        Returns a project's roots tasks
        """
        return Task.objects.filter(project=self, parent=None)

    @property
    def score(self):

        """
        Returns the project score, based on
        how many open/closed tasks it has
        """
        return calculate_project_score(self)

    def clone(self,
              new_name,
              new_type=None,
              new_responsible=None,
              new_date=None,
              new_status=None,
              keep_tasks=True,
              keep_comments=False,
              keep_attachments=False,
              keep_tags=False):
        from .cloning import clone_project
        return clone_project(
            self,
            new_name,
            new_type,
            new_responsible,
            new_date,
            new_status,
            keep_tasks,
            keep_comments,
            keep_attachments,
            keep_tags
        )

    def __str__(self):
        return self.name

    class Meta:

        verbose_name = _('Project')
        verbose_name_plural = _('Projects')


@python_2_unicode_compatible
class TaskStatus(CreatedByMixIn,
                 DomainModelMixIn):

    """
    This models a TaskStatus. These are statuses that a task
    can be in. There is no restriction from-to states that a
    task might go.
    This defines two flags:
    * is_system_status - if it's a system status, it cannot be changed by the user.
    * is_closing_status - if it's a closing status, it will be considered when
    * couting closed/open tasks.
    """

    color = ColorField(default='#A4A4A4')

    is_system_status = models.BooleanField(
        default=False,
        verbose_name=_('Is System?')
    )

    is_closing_status = models.BooleanField(
        default=False,
        verbose_name=_('Is Closing Status?')
    )

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = _('Task Status')
        verbose_name_plural = _('Task Statuses')


@python_2_unicode_compatible
class Task(MPTTModel,
           DirtyFieldsMixin,
           CreatedByMixIn,
           DateCreatedMixIn,
           DateUpdatedMixIn,
           DateRangeMixIn):

    """
    Task. Indicates that something should be done about it.
    It's a MPTT Model and can recurse ad-eternum.
    """

    uuid = models.UUIDField(
        verbose_name=_('UUID'),
        default=uuid.uuid4,
        editable=False
    )

    project = models.ForeignKey(
        Project,
        related_name='tasks',
    )

    parent = TreeForeignKey(
        'self',
        null=True,
        related_name='children',
        db_index=True
    )

    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='tasks',
        null=True
    )

    status = models.ForeignKey(
        TaskStatus,
        verbose_name=_('Status'),
        default=default_task_status
    )

    weight = models.IntegerField(
        default=1,
        verbose_name=_('Weight')
    )

    name = models.CharField(
        max_length=128,
        verbose_name=_('Name')
    )

    description = models.TextField(
        verbose_name=_('Description'),
        null=True
    )

    attachments = GenericRelation(
        'chaos.TaskAttachment',
        related_query_name='tasks'
    )

    files = Files()

    tags = TaggableManager()

    def __str__(self):
        return self.name

    @property
    def duration(self):
        if self.start_date and self.end_date:
            return self.end_date - self.start_date
        return None

    @property
    def score(self):
        """
        Calculates and returns the score for this node
        and children
        """
        return calculate_node_score(self)

    @property
    def followers(self):
        """
        Returns attached users
        """
        User = get_user_model()
        user_ct = ContentType.objects.get_for_model(User)
        return self.attachments.filter(
            content_type=user_ct
        )

    @property
    def related_tasks(self):
        task_ct = ContentType.objects.get_for_model(self)
        return self.attachments.filter(
            content_type=task_ct,
            task_id=self.pk
        )

    def attach(self, model, user=None):
        """
        attaches a model to this task.
        if the model is already attached, it will do
        nothing.
        you can attach anything to the model
        """
        if not model:
            raise ValueError('model is mandatory')

        content_type = ContentType.objects.get_for_model(model)
        try:
            attachment = TaskAttachment.objects.get(
                content_type=content_type,
                object_id=model.pk
            )
        except TaskAttachment.DoesNotExist:
            attachment = TaskAttachment.objects.create(
                content_object=model,
                task=self,
                created_by=user
            )
        return attachment

    def detach(self, model):
        """
        Detaches a model from
        this task.
        if this attachment does not exist,
        it will do nothing
        """
        if not model:
            raise ValueError('model is mandatory')

        content_type = ContentType.objects.get_for_model(model)
        try:
            attachment = TaskAttachment.objects.get(
                content_type=content_type,
                object_id=model.pk
            )
            attachment.delete()
        except TaskAttachment.DoesNotExist:
            pass

    def clone(self,
              new_project=None,
              new_node=None,
              new_status=None,
              new_date=None,
              new_responsible=None,
              keep_comments=False,
              keep_attachments=False,
              keep_tags=True):
        """
        Copies this task and all it's children to
        a target_node on this project or another project.
        If specified, we will set a new date for this task
        and it's children, based on the detal between each
        one.
        """
        from .cloning import clone_task
        return clone_task(
            self,
            new_project,
            new_node,
            new_status,
            new_date,
            new_responsible,
            keep_comments,
            keep_attachments,
            keep_tags
        )

    class MPTTMeta:
        order_insertion_by = ['date_created']

    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')


@python_2_unicode_compatible
class Comment(CreatedByMixIn,
              DateCreatedMixIn,
              DateUpdatedMixIn):

    """
    Comment for a task.
    Can have attachments and text.
    System updates are also published
    as comments that cannot be edited.
    The created_by field allows the creator
    to edit the comment or remove it.
    """

    task = models.ForeignKey(
        Task,
        related_name='comments'
    )

    text = models.TextField(
        verbose_name=_('Text')
    )

    files = Files()

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ('-date_created', )


@python_2_unicode_compatible
class TaskAttachment(CreatedByMixIn,
                     DateCreatedMixIn,
                     DateUpdatedMixIn):

    """
    Enables the user to attach other system objects
    to the the task.
    Something like, to which item does this task belong
    to?
    """

    task = models.ForeignKey(
        Task,
        related_name='attachments'
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    object_id = models.PositiveIntegerField()

    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):

        return _('Task Attachment: {0}').format(self.content_object)


@python_2_unicode_compatible
class Reminder(CreatedByMixIn,
               DateCreatedMixIn,
               DateUpdatedMixIn):

    """
    Defines a reminder on the system to
    alert the user of a certain thing.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('User'),
        related_name='reminders'
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )

    start_date_field = models.CharField(
        max_length=128,
        verbose_name=_('Start Date Field'),
        default='start_date',
    )

    object_id = models.PositiveIntegerField()

    content_object = GenericForeignKey('content_type', 'object_id')

    time_delta = models.DurationField(
        verbose_name=_('Time Delta')
    )

    repeat = RecurrenceField(
        verbose_name=_('Repeat'),
        null=True,
    )

    @property
    def is_recurring(self):
        return self.repeat is not None

    @property
    def event_start(self):
        """
        Returns the start date of the event, that is,
        the content_object.
        """
        return getattr(self.content_object, self.start_date_field)

    @property
    def start(self):
        """
        Returns the first date of the reminder.
        This is basically the start date of the event, minus
        the time_delta
        """
        start_date = getattr(self.content_object, self.start_date_field)
        if start_date:
            return start_date - self.time_delta
        return None

    @property
    def end(self):
        """
        Returns the last date of the reminder.
        if we have recurrence and a start date of
        the event, the end of the reminders is equal
        the start date of the event.
        """
        start_date = self.event_start
        if start_date and self.repeat:
            return start_date
        return None

    @property
    def reminder_dates(self):
        """
        Returns a list of dates
        that these reminders must be sent.
        if we dont have the content_object
        start date, it will return None.
        if the reminder is recurring, the last
        reminder will be sent on the start date
        of the content_object.
        the first reminder is sent on the start_date
        minus the timedelta.
        """
        original_start_date = self.start
        original_end_date = self.end

        if not original_start_date:
            return None

        first_reminder_date = original_start_date
        if not self.is_recurring:
            return [first_reminder_date]

        return self.repeat.between(
            original_start_date,
            original_end_date,
            dtstart=original_start_date,
            inc=True
        )

    def __str__(self):
        return _('Reminder: {0}').format(self.content_object)

    class Meta:
        verbose_name = _('Reminder')
        verbose_name_plural = _('Reminders')
