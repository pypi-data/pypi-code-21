# coding: utf-8
"""
This module responsibility is to hold
classes and functions that are related
with cloning projects and tasks.
"""
import logging
from .models import (
    Project,
    Task,
    TaskStatus,
    TaskAttachment,
    Comment,
    Reminder,
)
logger = logging.getLogger(__name__)


def clone_project(source,
                  new_name,
                  new_type=None,
                  new_responsible=None,
                  new_date=None,
                  new_status=None,
                  keep_tasks=False,
                  keep_comments=False,
                  keep_attachments=False,
                  keep_tags=False):
    try:
        if not source:
            raise ValueError('source is mandatory')
        if not new_name:
            raise ValueError('new_name is mandatory')

        logger.info('cloning project %s into %s', source, new_name)

        new_type = new_type if new_type else source.type
        new_status = new_status if new_status else TaskStatus.objects.get(code='OPEN')
        new_responsible = new_responsible if new_responsible else source.responsible
        new = Project()
        new.name = new_name
        new.description = source.description
        new.type = new_type
        new.responsible = new_responsible
        new.save()

        if keep_tags:
            logger.info('cloning project %s tags', source)
            for tag in source.tags.all():
                new.tags.add(tag)

        if keep_tasks:
            logger.info('cloning project %s tasks', source)
            for task in source.root_tasks.all():
                clone_task(
                    task,
                    new_project=new,
                    new_date=new_date,
                    new_status=new_status,
                    keep_comments=keep_comments,
                    keep_attachments=keep_attachments,
                    keep_tags=keep_tags
                )

        return new
    except Exception as ex:
        logger.error(
            'error while cloning project %s. error: %s',
            source,
            ex.message,
            exc_info=True
        )
        return None


def clone_task(source,
               new_project=None,
               new_node=None,
               new_status=None,
               new_date=None,
               new_responsible=None,
               keep_comments=False,
               keep_attachments=False,
               keep_tags=False):
    if not source:
        raise ValueError('source is mandatory')
    if not new_project and not new_node:
        raise ValueError('new_project and new_node cannot be null. you must choose one to be the target of the copied task.')  # noqa
    if new_node and new_project.pk != new_node.project.pk:
        raise ValueError('new_node must be contained in new_project')
    logger.info('cloning task %s', source)
    if new_project:
        project = new_project
    else:
        if new_node.project:
            project = new_node.project
        else:
            project = source.project

    project = new_project if new_project else source.project
    parent = new_node  # this does not coerce because new_node == None is also valid
    responsible = new_responsible if new_responsible else source.responsible
    status = new_status if new_status else source.status
    start_date = new_date if new_date else source.start_date
    if start_date and source.end_date:
        delta = source.end_date - source.start_date
        end_date = start_date + delta
    else:
        end_date = None
    new = Task(
        project=project,
        parent=parent,
        responsible=responsible,
        status=status,
        name=source.name,
        description=source.description,
        start_date=start_date,
        end_date=end_date
    )
    new.save()
    if keep_comments:
        logger.info('cloning task %s comments', source)
        for c in source.comments.all():
            new_comment = Comment(
                created_by=c.created_by,
                task=new,
                text=c.text
            )
            new_comment.save()
    if keep_attachments:
        logger.info('cloning task %s attachments', source)
        for a in source.attachments.all():
            new_attachment = TaskAttachment(
                created_by=a.created_by,
                task=new,
                content_object=a.content_object
            )
            new_attachment.save()
    if keep_tags:
        logger.info('cloning task %s tags', source)
        for tag in source.tags.all():
            new.tags.add(tag)

    logger.info('cloning task %s children', source)
    children = source.get_children()
    for child in children:
        inner_delta = child.start_date - start_date
        inner_start = start_date + inner_delta
        child.copy_to(
            new_project=project,
            new_node=parent,
            new_status=new_status,
            new_date=inner_start,
            new_responsible=new_responsible,
            keep_comemnts=keep_comments,
            keep_attachments=keep_attachments
        )

    return new
