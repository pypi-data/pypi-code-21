"""
This module contains a number of helper functions for performing basic Carrot functions, e.g. publish, schedule and
consume

Most users should use the functions defined in this module, rather than attempting to subclass the base level objects

"""


import json
from json2html.jsonconv import Json2Html
import importlib
from django.conf import settings
from carrot.objects import VirtualHost, Message
from carrot.models import ScheduledTask
from carrot.consumer import ConsumerSet
from django.utils.decorators import method_decorator
from carrot import DEFAULT_BROKER


def get_host_from_name(name):
    """
    Gets a host object from a given queue name based on the Django configuration

    If no queue name is provided (as may be the case from some callers), this function returns a VirtualHost based on
    the CARROT.default_broker value.

    May raise an exception if the given queue name is not registered in the settings.

    :param str name: the name of the queue to lookup.
    :rtype: :class:`carrot.objects.VirtualHost`

    """

    try:
        if not name:
            conf = settings.CARROT.get('default_broker', DEFAULT_BROKER)
            try:
                return VirtualHost(**conf)
            except TypeError:
                return VirtualHost(url=conf)

        queues = settings.CARROT['queues']
        queue_host = list(filter(lambda queue: queue['name'] == name, queues))[0]['host']
        try:
            vhost = VirtualHost(**queue_host)
        except TypeError:
            vhost = VirtualHost(url=queue_host)

        return vhost

    except IndexError:
        raise Exception('Cannot find queue called %s in settings.CARROT queue list' % name)


def validate_task(task):
    """
    Helper function for dealing with task inputs which may either be a callable, or a path to a callable as a string

    In case of a string being provided, this function checks whether the import path leads to a valid callable

    Otherwise, the callable is converted back into a string (as the :class:`carrot.objects.Message` requires a string
    input)

    This function is used by the following other utility functions:
    - :func:`.create_scheduled_task`
    - :func:`.create_message`

    :param task: a callable or a path to one as a string
    :type task: str or callable
    :return: a validated path to the callable, as a string

    """
    mod, fname = (None, ) * 2

    if isinstance(task, str):
        try:
            fname = task.split('.')[-1]
            mod = '.'.join(task.split('.')[:-1])
            module = importlib.import_module(mod)
            getattr(module, fname)
        except ImportError as err:
            raise ImportError('Unable to find the module: %s' % err)

        except AttributeError as err:
            raise AttributeError('Unable to find a function called %s in the module %s: %s' % (fname, mod, err))
    else:
        task = '%s.%s' % (task.__module__, task.__name__)

    return task


def create_message(task, priority=0, task_args=(), queue=None, exchange='', routing_key=None, task_kwargs=None):
    """
    Creates a :class:`carrot.objects.Message` object without publishing it

    The task to execute (as a string or a callable) needs to be supplied. All other arguments are optional
    :param task: the task to be handled asynchronously.
    :type task: str or func
    :param int priority: the priority to be applied to the message when it is published to RabbitMQ

    :param tuple task_args: the positional arguments to be passed to the function when it is called

    :param queue: the name of the queue to publish the message to. Will be set to "default" if not provided
    :type queue: str or None
    :param str exchange: the exchange name
    :param routing_key: the routing key
    :type routing_key: str or NoneType

    :param dict task_kwargs: the keyword arguments to be passed to the function when it is called
    :rtype: :class:`carrot.objects.Message`

    """

    if not task_kwargs:
        task_kwargs = {}

    task = validate_task(task)

    vhost = get_host_from_name(queue)
    msg = Message(virtual_host=vhost, queue=queue, routing_key=routing_key, exchange=exchange, task=task,
                  priority=priority, task_args=task_args, task_kwargs=task_kwargs)

    return msg


def publish_message(task, *task_args, priority=0, queue=None, exchange='', routing_key=None, **task_kwargs):
    """
    Wrapped for :func:`.create_message`, which publishes the task to the queue

    This function is the primary method of publishing tasks to a message queue
    """
    msg = create_message(task, priority, task_args, queue, exchange, routing_key, task_kwargs)
    return msg.publish()


def create_consumer_set(queue_name, concurrency=1, name='consumer', logfile='/var/log/carrot.log',
                        consumer_class='carrot.consumer.Consumer', loglevel='DEBUG'):
    """
    Helper function for creating :class:`carrot.consumer.ConsumerSet` objects.

    :param str queue_name: the name of the queue to consume from
    :param int concurrency: the number of consumers to create
    :param str name: the name to be given to individual :class:`carrot.consumer.Consumer` objects
    :param str logfile: path to the log file
    :param str consumer_class: the consumer class
    :param str loglevel: the logging level (DEBUG, INFO, WARNING, ERROR or CRITICAL)

    :rtype: :class:`carrot.consumer.ConsumerSet`

    """
    host = get_host_from_name(queue_name)
    c = ConsumerSet(host=host, queue=queue_name, concurrency=concurrency, name=name, logfile=logfile,
                    consumer_class=consumer_class, loglevel=loglevel)
    return c


def create_scheduled_task(task, interval, queue=None, **kwargs):
    """
    Helper function for creating a :class:`carrot.models.ScheduledTask`

    :param task: a callable, or a valid path to one as a string
    :type task: str or callable
    :param dict interval: the interval at which to publish the message, as a dict, e.g.: {'seconds': 5}
    :param str queue: the name of the queue to publish the message to.
    :param kwargs: the keyword arguments to be passed to the function when it is executed
    :rtype: :class:`carrot.models.ScheduledTask`

    """

    task = validate_task(task)

    try:
        assert isinstance(interval, dict)
        assert len(interval.items()) == 1
    except AssertionError:
        raise AttributeError('Interval must be a dict with a single key value pairing, e.g.: {\'seconds\': 5}')

    type, count = list(*interval.items())

    t = ScheduledTask.objects.create(
        queue=queue,
        interval_type=type,
        interval_count=count,
        routing_key=queue,
        task=task,
        content=json.dumps(kwargs or '{}'),
    )
    return t


class JsonConverter(Json2Html):
    """
    Helper function that converts a JSON object into a HTML table. Used by :class:`carrot.views.MessageView`
    """
    def convert(self, json="", table_attributes='border="1"', first_row=None, clubbing=True, encode=False, escape=True):
        if first_row:
            table_attributes = '%s> %s' % (table_attributes, first_row)

        return super(JsonConverter, self).convert(json, table_attributes, clubbing, encode, escape)

    def convert_object(self, json_input):
        if not json_input:
            return ""
        converted_output = self.table_init_markup + "<tr>"
        converted_output += "</tr><tr>".join([
            "<td>%s</td><td>%s</td>" %(
                self.convert_json_node(k),
                self.convert_json_node(v)
            )
            for k, v in json_input.items()
        ])
        converted_output += '</tr></table>'
        return converted_output


def get_mixin(decorator):
    """
    Helper function that allows dynamic application of decorators to a class-based views

    :param func decorator: the decorator to apply to the view
    :return:
    """
    class Mixin:
        @method_decorator(decorator)
        def dispatch(self, request, *args, **kwargs):
            return super(Mixin, self).dispatch(request, *args, **kwargs)

    return Mixin


def create_class_view(view, decorator):
    """
    Applies a decorator to the dispatch method of a given class based view. Can be chained

    :param class view: the class-based view to apply the decorator to
    :param function decorator: the decorator to apply

    :rtype: the updated class based view
    """
    class DecoratedView(get_mixin(decorator), view):
        pass

    return DecoratedView


def decorate_class_view(view_class, decorators=None):
    """
    Loop through a list of string paths to decorator functions, and call :func:`.create_class_view` for each one

    :param class view_class: the class-based view to attach the decorators to
    :param list decorators: a list of string decorators, e.g. ['myapp.mymodule.decorator1', 'myapp.mymodule.decorator2']

    :return: the class based view with all decorators attached to the dispatch method

    """
    if decorators is None:
        decorators = []

    for decorator in decorators:
        _module = '.'.join(decorator.split('.')[:-1])
        module = importlib.import_module(_module)
        _decorator = getattr(module, decorator.split('.')[-1])
        view_class = create_class_view(view_class, _decorator)

    return view_class


def create_function_view(view, decorator):
    """
    Similar to :func:`.create_class_view`, but attaches a decorator to a function based view, instead of a class-based
    one

    :param func view: the function based view to attach a decorator tio
    :param func decorator: the decorator attach

    :rtype: the updated view function

    """
    @decorator
    def wrap(request, *args, **kwargs):
        return view(request, *args, **kwargs)

    return wrap


def decorate_function_view(view, decorators=None):
    """
    Similar to :func:`.decorate_class_view`, but for function based views
    """
    if not decorators:
        decorators = []

    for decorator in decorators:
        _module = '.'.join(decorator.split('.')[:-1])
        module = importlib.import_module(_module)
        _decorator = getattr(module, decorator.split('.')[-1])
        view = create_function_view(view, _decorator)

    return view
