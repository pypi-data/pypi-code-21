#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2017/8/2
 """
from __future__ import unicode_literals, absolute_import
from celery.app import shared_task
from djdg_core.settings import LOGGER_NAME
import logging


class Subject(object):
    """
    可订阅的主题
    """
    def __init__(self, name, hub):
        self.name = name
        self.hub = hub
        self.hub.register_subject(self)

    def publish(self, *args, **kwargs):
        self.hub.publish(self, *args, **kwargs)

    def async_publish(self, app, *args, **kwargs):
        task_name = celery_task_of_hubs.get(self.hub)
        if not task_name:
            raise Exception('订阅发布总线{}找不到对应的celery任务名称！'.format(self.hub.__class__.name))
        _args = [self.name]
        _args.extend(args)
        app.send_task(
            task_name,
            _args,
            kwargs
        )


class Subscriber(object):
    """
    订阅者
    """
    def __init__(self, hub, subject, *args, **kwargs):
        self.hub = hub
        self.subject = subject
        self.args = args
        self.kwargs = kwargs
        context = kwargs.pop('context', None) or {}
        self.context = context

    def subscribe(self, subject, priority=20):
        self.hub.subscribe(subject, self, priority)

    def notify(self):
        pass

    def filter(self):
        return True


class SubHub(object):
    """
    订阅中心
    """
    def __init__(self, async_publish=None, logger=None):
        self.subject_map = {}
        self.subscriber_map = {}
        self.async_publish = async_publish
        self.logger = logger

    def set_logger(self, logger):
        self.logger = logger

    def set_async_publish(self, async_publish):
        self.async_publish = async_publish

    def register_subject(self, subject):
        if subject.name not in self.subject_map:
            self.subject_map[subject.name] = subject

    def create_or_get_subject(self, name):
        if name not in self.subject_map:
            self.subject_map[name] = Subject(name, self)
        return self.subject_map[name]

    def subscribe(self, subject, subscriber, priority=20):
        if isinstance(subject, Subject):
            name = subject.name
        else:
            name = subject
        if name not in self.subscriber_map:
            pqueue = []
            self.subscriber_map[name] = pqueue
        else:
            pqueue = self.subscriber_map[name]
        pqueue.append((priority, subscriber))
        pqueue.sort(key=lambda x: x[0])

    def subscribe_subjects(self, subscriber, subjects, priority=20):
        for s in subjects:
            self.subscribe(s, subscriber, priority)

    def connect_subscribers(self, subject, subscribers, priority=20):
        for s in subscribers:
            self.subscribe(subject, s, priority)

    def sync_publish(self, subject, *args, **kwargs):
        if isinstance(subject, Subject):
            name = subject.name
        else:
            name = subject
        subscribers = self.subscriber_map.get(name, [])
        context = kwargs.pop('context', {})
        kwargs['context'] = context
        for priority, subscriber in subscribers:
            try:
                s = subscriber(self, subject, *args, **kwargs)
                if s.filter():
                    s.notify()
                    if s.context:
                        context.update(s.context)
            except Exception as e:
                if self.logger:
                    self.logger.exception(e.message)
                    self.logger.error('subject {} subscriber {} args {} kwargs {}'.format(
                        subject,
                        subscriber.__name__,
                        args,
                        kwargs
                    ))

    def publish(self, subject, *args, **kwargs):
        """
        发布内容
        :param subject:
        :param args:
        :param kwargs:
        :return:
        """
        if isinstance(subject, Subject):
            name = subject.name
        else:
            name = subject
        publish_func = self.async_publish if self.async_publish else self.sync_publish
        publish_func(name, *args, **kwargs)


subscribe_hubs = {}
async_publish_funcs = {}
celery_task_of_hubs = {}


def create_async_publish_function(name, hub):
    """
    创建异步发布方法
    :param name:
    :param hub:
    :return:
    """
    @shared_task(name=name)
    def inner(subject, *args, **kwargs):
        hub.sync_publish(subject, *args, **kwargs)
    return inner.delay


def get_or_create_subscribe_hub(hub_name=None, celery_task=None, log_obj=None):
    """
    创建hub，或取得存在的Hub
    :param hub_name:
    :param celery_task:
    :param log_obj:
    :return:
    """
    if hub_name in subscribe_hubs:
        return subscribe_hubs[hub_name]
    _hub = SubHub()
    async_publish = None
    if celery_task:
        if celery_task not in async_publish_funcs:
            async_publish = create_async_publish_function(celery_task, _hub)
            async_publish_funcs[celery_task] = async_publish
            celery_task_of_hubs[_hub] = celery_task
        else:
            raise Exception('subscribe hub celery task {} had been used.'.format(celery_task))
    if not log_obj:
        log_obj = logging.getLogger(LOGGER_NAME)
    _hub.set_logger(log_obj)
    _hub.set_async_publish(async_publish)
    subscribe_hubs[hub_name] = _hub
    return _hub
