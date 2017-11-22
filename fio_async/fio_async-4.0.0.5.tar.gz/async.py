# -*- coding: UTF-8 -*-
"""
    trytond_async.async

    Call Tryton model methods asynchronously by using celery.
    The implementation detail is hidden to provide an interface API that
    tryton developers are familiar with while making it possible to still
    customize behavior.
"""
import logging
from celery import current_app

import wrapt
from trytond.pool import PoolMeta, Pool
from trytond.model import ModelView, Model
from trytond.transaction import Transaction
from trytond_async.serialization import json, JSONDecoder, JSONEncoder
from trytond_async.tasks import execute
from trytond_async.mock_result import MockResult


__metaclass__ = PoolMeta


logger = logging.getLogger('ASYNC')


class task(object):
    """
    A decorator that mimics the task decorator from celery. However, this
    decorator has limited options and behind the scenes it delegates to celery.

    The decorator from celry itself cannot be used because of its limited
    support for instance and class methods which is what tryton models have
    mostly.

    To change the behavior of this decorator, you could either implement a
    new decorator which inherits from this or subclass and change behavior of
    the method `defer` in the model `async.async`. Most of the task deferring
    code itself is implemented there for convenience.
    """

    def __init__(self, ignore_result=True, visibility_timeout=60):
        self.ignore_result = ignore_result
        self.visibility_timeout = visibility_timeout

    @wrapt.decorator
    def __call__(self, wrapped, instance, args, kwargs, **celery_options):
        """
        Read the docstring of this class before you decide to reimplement this.
        change the behavior in the `defer` method of `async.async` model.
        """
        if kwargs.pop('_defer_', False) is False:
            # if not a deferred call, return instantly
            return wrapped(*args, **kwargs)

        # This is a defered call
        model_name = instance.__name__
        if isinstance(instance, Model):
            active_record = instance
        else:
            active_record = None

        Async = Pool().get('async.async')
        return Async.apply_async(
            model=model_name,
            method=wrapped.__name__,
            instance=active_record,
            args=args,
            kwargs=kwargs,
            **celery_options
        )


class Async(ModelView):
    """
    Asynchronous Execution Helper.
    """
    __name__ = 'async.async'

    @classmethod
    def execute_payload(cls, payload):
        """
        Execute the task for the given payload. This method will be called
        by `trytond_async.tasks.execute` with the user and context set. This
        method could be subclaassed and altered by downstream modules.
        """
        (model, method, instance, args, kwargs) = (
            payload['model_name'],
            payload['method_name'],
            payload['instance'],
            payload['args'],
            payload['kwargs'],
        )
        if instance:
            logger.info('%s.%s' % (instance, method))
            return getattr(instance, method)(*args, **kwargs)
        logger.info('%s.%s' % (model, method))
        return getattr(Pool().get(model), method)(*args, **kwargs)

    @classmethod
    def build_payload(
            cls, method, model=None, instance=None,
            args=None, kwargs=None):
        """Generate payload for serialization of task

        :param model: String representing global name of the model or
                      reference to model class itself.
        :param method: Name or method object
        :param instance: The instance on which the method call should happen
                         if it is an instance
        :param args: positional arguments passed on to method as list/tuple.
        :param kwargs: keyword arguments passed on to method as dict.
        """
        if isinstance(method, basestring):
            method_name = method
        else:
            method_name = method.__name__

        if isinstance(model, basestring):
            model_name = model
        elif model:
            model_name = model.__name__
        else:
            model_name = None

        if isinstance(instance, Model):
            model_name = instance.__name__

        args = args or []
        kwargs = kwargs or {}

        if current_app.conf.get('TEST_MODE', False):
            if instance:
                return MockResult(
                    getattr(instance, method_name)(*args, **kwargs)
                )
            else:
                CurrentModel = Pool().get(model_name)
                return MockResult(
                    getattr(CurrentModel, method_name)(*args, **kwargs)
                )

        return {
            'model_name': model_name,
            'instance': instance,
            'method_name': method_name,
            'args': args,
            'kwargs': kwargs,
            'context': Transaction().context,
        }

    @classmethod
    def apply_async(
            cls, method, model=None, instance=None,
            args=None, kwargs=None, **celery_options):
        """Wrapper for painless asynchronous dispatch of method
        inside given model.

        .. note::

            * Works only when called within a transaction.
            * Required only if the menthod is not already decorated as a
              async_sqs_task

        :param model: String representing global name of the model or
                      reference to model class itself.
        :param method: Name or method object
        :param instance: The instance on which the method call should happen
                         if it is an instance
        :param args: positional arguments passed on to method as list/tuple.
        :param kwargs: keyword arguments passed on to method as dict.
        :returns :class:`AsyncResult`:
        """
        payload = cls.build_payload(method, model, instance, args, kwargs)

        if isinstance(payload, MockResult):
            # Test async call will return MockResult
            return payload

        return execute.apply_async(
            # Args for the call
            (
                Transaction().database.name,
                Transaction().user,
                cls.serialize_payload(payload)
            ),
            # Additional celery options
            **celery_options
        )

    @classmethod
    def get_json_encoder(cls):
        """
        Return the JSON encoder class. Use this if you want to implement your
        own serialization
        """
        return JSONEncoder

    @classmethod
    def serialize_payload(cls, payload):
        """
        Serialize the given payload to JSON
        """
        return json.dumps(payload, cls=cls.get_json_encoder())

    @classmethod
    def get_json_decoder(cls):
        """
        Return the JSON decoder class. Use this if you want to implement your
        own serialization.

        .. note::

            JSON Decoder needs to be an instance (unlike encoder)
        """
        return JSONDecoder()

    @classmethod
    def deserialize_payload(cls, payload):
        """
        Deserialize the given message to a javascript payload
        """
        return json.loads(payload, object_hook=cls.get_json_decoder())
