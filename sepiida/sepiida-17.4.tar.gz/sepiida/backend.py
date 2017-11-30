import functools
import importlib
import logging
import threading
import time

import celery
import flask
import kombu
import kombu.exceptions
import raven
import raven.contrib.celery

import sepiida.context
import sepiida.log

LOGGER = logging.getLogger(__name__)

def create(service_name, imports=None, rabbit_url='amqp://', sentry_dsn=None, testing=False, flask_app=None):
    # This little gem of a hack ensures our tasks are getting imported.
    # Normally celery would do this for us, but I think we broke it
    # because of the way we are wrapping celery tasks
    if imports:
        _ = [importlib.import_module(_import) for _import in imports]

    app = celery.Celery(service_name)
    app.conf.update(
        BROKER_TRANSPORT_OPTIONS = {'confirm_publish': True},
        BROKER_URL = rabbit_url,
        CELERY_DEFAULT_QUEUE = service_name,
        CELERY_QUEUES = (
            kombu.Queue(service_name, kombu.Exchange(service_name), routing_key=service_name),
        ),
        CELERY_TIMEZONE = 'UTC',
        CELERYD_LOG_FORMAT = sepiida.log.FORMAT,
    )

    if testing:
        app.conf.update(CELERY_ALWAYS_EAGER=True)

    if sentry_dsn:
        client = raven.Client(sentry_dsn)
        raven.contrib.celery.register_signal(client)

    create.application = app
    create.flask_app = flask_app

    if not TaskProxy.instances:
        LOGGER.warning(
            "When registering all backend tasks none were found - something may be wrong with you app setup logic. "
            "This can be caused by failing to call sepiida.backend.task as a function"
        )
    TaskProxy.register_all()

    return app
create.application = None
create.flask_app = None

def start_celery_pump(name, interval=180):
    """
    Start a separate daemon thread that does nothing but send no-op tasks through
    the task queue system so that we can ensure the connection stays alive. This is
    important in environments like Docker Swarm
    """
    pump = threading.Thread(
        daemon = True,
        kwargs = {'interval': interval},
        name   = 'celery-pump-' + name,
        target = _celery_pump,
    )
    pump.start()
    LOGGER.info("Started celery pump thread %s", pump)

def _celery_pump(interval):
    delay = 0
    while True:
        try:
            delay = min(30, (delay ** (1.1)) + 0.5)
            null_op.delay()
            delay = 0
            time.sleep(interval)
        except OSError as e:
            LOGGER.warning("Failed to send null-op: %s. Waiting %f seconds to retry", e, delay)
            time.sleep(delay)
        except Exception as e: # pylint: disable=broad-except
            LOGGER.exception("Death in the celery pump thread: %s", e)
            LOGGER.warning("Waiting %f seconds to retry", delay)
            time.sleep(delay)

class TaskProxy(object):
    instances = []
    def __init__(self, func, *args, schedule=None, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.celery_task = None
        self.schedule = schedule
        TaskProxy.instances.append(self)

    @staticmethod
    def register_all():
        for instance in TaskProxy.instances:
            instance.ensure_registered()

    def ensure_registered(self):
        if not self.celery_task:
            base = self.kwargs.pop('base', None)
            if base:
                raise Exception("You can't change the base class, sorry")
            self.celery_task = create.application.task(*self.args, base=TaskWithCredentials, **self.kwargs)(self.func)
            if self.schedule:
                create.application.conf['CELERYBEAT_SCHEDULE'][self.name] =  {
                    'task'      : self.name,
                    'schedule'  : self.schedule,
                }

    def __call__(self, *args, **kwargs):
        self.ensure_registered()
        return self.celery_task(*args, **kwargs)

    def __getattr__(self, name):
        self.ensure_registered()
        return getattr(self.celery_task, name)

def has_task_context():
    return task_credentials.current_task is not None

def task_credentials():
    if not has_task_context():
        raise Exception("Cannot retrieve task credentials - not in a task context")
    return task_credentials.current_task.credentials
task_credentials.current_task = None

class TaskWithCredentials(celery.Task): # pylint: disable=abstract-method
    @staticmethod
    def _add_credentials_headers(options):
        if has_task_context():
            credentials = task_credentials()
        else:
            credentials = sepiida.context.extract_credentials(flask.request)

        LOGGER.debug("Extracted credentials %s", credentials)
        options['headers'] = options.get('headers', {})
        options['headers'].update({
            'credentials': credentials,
        })

    def apply_async(self, args=None, kwargs=None, task_id=None, producer=None, link=None, link_error=None, **options):
        self._add_credentials_headers(options)
        return super(TaskWithCredentials, self).apply_async(
            args       = args,
            kwargs     = kwargs,
            task_id    = task_id,
            producer   = producer,
            link       = link,
            link_error = link_error,
            **options
        )

    def retry(self, args=None, kwargs=None, exc=None, throw=True, eta=None, countdown=None, max_retries=None, **options): # pylint: disable=too-many-arguments
        self._add_credentials_headers(options)
        return super(TaskWithCredentials, self).retry(
            args        = args,
            kwargs      = kwargs,
            exc         = exc,
            throw       = throw,
            eta         = eta,
            countodwn   = countdown,
            max_retries = max_retries,
            **options
        )

    @property
    def credentials(self):
        return self.get_header('credentials')

    def get_header(self, key, default=None):
        return (self.request.headers or {}).get(key, default)

def task(*args, **kwargs):
    def decorator(func):
        @functools.wraps(func)
        def __add_task_context(*args, **kwargs):
            if args and isinstance(args[0], TaskWithCredentials):
                _task = args[0]
            else:
                _task = None
            try:
                task_credentials.current_task = _task
                return func(*args, **kwargs)
            finally:
                task_credentials.current_task = None
        return TaskProxy(__add_task_context, *args, **kwargs)
    return decorator

def with_app_context(func):
    @functools.wraps(func)
    def __inner(*args, **kwargs):
        with create.flask_app.app_context():
            return func(*args, **kwargs)
    return __inner

@task()
def null_op():
    LOGGER.debug("Handled a null op")
