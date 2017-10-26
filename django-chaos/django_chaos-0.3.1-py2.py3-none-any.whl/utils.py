# codign: utf-8
import os
import uuid
import logging
from django.utils.translation import ugettext_lazy as _
from .models import TaskStatus
from .signals import task_status_changed
logger = logging.getLogger(__name__)


def get_output_path(directory, filename):

    if not directory:
        raise ValueError('directory is mandatory')

    if not filename:
        raise ValueError('filename is mandatory')

    try:
        name, extension = filename.split('.')
    except:
        raise ValueError('filename must be composed of filename.extension')

    uid = uuid.uuid4().hex
    full_name = '{0}-{1}.{2}'.format(name, uid, extension)

    return os.path.join(directory, full_name)


def get_model(model_name):

    """
    model_name must be app.model
    """

    try:
        from django.db.models import get_model
    except:
        from django.apps import apps
        get_model = apps.get_model

    app, model = model_name.split('.')
    if not app or not model:
        raise ValueError('model_name is must be in the format app.model')
    return get_model(app, model)


def get_responsibles(task_changes, include_project=True):
    """
    Returns a unique list of users
    responsible for the tasks in these
    changes.
    """
    if not task_changes:
        return None
    changes = TaskHandler.flatten(task_changes)
    users = list([c.task.responsible for c in changes if c.task.responsible is not None])
    if include_project and task_changes.task.project.responsible:
        users.append(task_changes.task.project.responsible)
    return list(set(users))


class TaskChange(object):

    """
    this holds a list of task changes that
    needs to be done when talking about status.
    we gather them, so they can be applied later
    and trigger all kinds of side effects, like
    notifications.
    Task is the task that will be modified.
    action is a string that contains a description of
    the action itself, like opening, reopening or closing
    status is the new status of the task. since
    we can have custom open/closed status, this means
    we have to pass this status along.
    initial_target is the initial task that was operated
    on. since that target can cascade different changes
    up/down the tree, we maintain it, so we can give
    accurate notifications.
    """
    task = None
    action = None
    status = None
    initial_target = None
    related_changes = None

    def __init__(self, task, action, status, initial_target=None):
        self.task = task
        self.action = action
        self.status = status
        self.initial_target = initial_target
        self.related_changes = list()

    def __str__(self):
        return '%s task %s. related changes: %s' % (self.action, self.task, len(self.related_changes))

    def perform(self):
        logger.info(
            '%s: changing task %s status from %s to %s',
            self.action,
            self.task,
            self.task.status,
            self.status
        )
        self.task.status = self.status
        self.task.save()
        for related in self.related_changes:
            related.perform()


class TaskChangeDetector(object):

    def __init__(self,
                 allow_all=True):
        # allow_all determines if it's possible to
        # change states that have the same semantics,
        # like  from a (open) > b (open)
        self.allow_all = allow_all
        self.open_status = TaskStatus.objects.get(code='OPEN')
        self.closed_status = TaskStatus.objects.get(code='CLOSED')

    def detect(self, task, status):
        """
        performs a state change in the task.
        this will receive a new status and it
        will analyze it, and call the correct
        function for it.
        """
        if not task:
            logger.warn('detect cannot be run without task')
            raise ValueError('task is mandatory')
        if not status:
            logger.warn('detect cannot be run without status')
            raise ValueError('status is mandatory')

        if task.status.pk == status.pk:
            return None

        if status.is_closing_status:
            action = self._close
        else:
            action = self._open

        return action(task, status, task)

    def _open(self, task, status=None, initial_target=None):

        if not status:
            status = self.open_status

        if not task.status.is_closing_status:
            action = 'state change'
        else:
            action = 'opening'

        if not self.allow_all and not task.status.is_closing_status:
            # if this is already open, we just change the state
            # of this task
            logger.info(
                'task %s is already open on state %s, skipping change to %s',
                task,
                task.status,
                status
            )
            return None

        changes = TaskChange(task, action, status, initial_target)
        if task.parent and task.parent.status.is_closing_status:
            changes.related_changes.append(self._open(task.parent, status, initial_target))
        return changes

    def _close(self, task, status=None, initial_target=None):
        if not status:
            status = self.closed_status

        if task.status.is_closing_status:
            action = 'state change'
        else:
            action = 'closing'

        if not self.allow_all and task.status.is_closing_status:
            # if it's closed, we are not closing it again
            logger.info(
                'task %s is already closed on state %s, skipping change to %s',
                task,
                task.status,
                status
            )
            return None

        siblings_open = task.get_siblings().filter(status__is_closing_status=False)
        if siblings_open.count() == 0 and task.parent:
            # close parent and let him close everything
            # else
            logger.info(
                'all siblings from %s are closed. closing parent task %s',
                task,
                task.parent
            )
            return self._close(task.parent, status, initial_target)

        changes = TaskChange(task, action, status, initial_target)
        logger.info(
            'detected task change for %s task. changing from %s to %s state',
            task,
            task.status,
            status
        )
        for child_task in task.get_descendants().filter(status__is_closing_status=False):
            changes.related_changes.append(
                TaskChange(child_task, action, status, initial_target)
            )
        return changes


class TaskHandler(object):

    """
    This class allows you to operate
    certain actions on the tasks.
    it will discover the changes that
    are needed and will make them happen
    """

    def __init__(self, detector_class=None):
        if not detector_class:
            detector_class = TaskChangeDetector
        self.detector = detector_class()

    @classmethod
    def flatten(cls, change):
        """
        This method will flatten changes and return a list of TaskChange
        """
        changes = list()
        if not change:
            return changes
        changes.append(change)
        for related in change.related_changes:
            changes.extend(cls.flatten(related))
        return changes

    def _flatten(self, change):
        return self.__class__.flatten(change)

    def to_status(self, task, status, dry_run=False, user=None):
        """
        Changes the task to a certain status, closing or opening it
        depending on the status.
        """
        if not user:
            user = _('system')
        changes = self.detector.detect(task, status)
        if not dry_run:
            logger.info('TaskHandler not in dry run mode. Executing changes.')
            changes.perform()
            task_status_changed.send_robust(
                sender=self.__class__,
                task=task,
                status=status,
                changes=changes,
                user=user
            )
            logger.info('TaskHandler done with change execution.')
        return changes
