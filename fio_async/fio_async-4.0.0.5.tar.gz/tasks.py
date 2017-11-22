# -*- coding: UTF-8 -*-
"""
    trytond_async.tasks

    Implements the actual task runners.

    Usual celery projects would have the method/functions which have the code
    to run as tasks. However, the tryton inheritance and majority of tryton
    code being in class and instance methods makes it hard for the pattern to
    be followed. Read more about the design on the getting started
    documentation of this module.
"""
from __future__ import absolute_import

from trytond import backend
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.cache import Cache

from trytond_async.app import app


class RetryWithDelay(Exception):
    """
    A special case of exception meant to be used by Tryton models to
    indicate to the worker that the task needs to be retried. This is
    needed because Tryton models itself are ignorant to the invocation from
    regular model code and asynchronously through workers!

    :param delay: Delay in seconds after which the task should be retried
    """
    def __init__(self, delay=5, *args, **kwargs):
        super(RetryWithDelay, self).__init__(*args, **kwargs)
        self.delay = delay


def _execute(app, database, user, payload_json):
    """
    Execute the task identified by the given payload in the given database
    as `user`.
    """
    if database not in Pool.database_list():
        # Initialise the database if this is the first time we see the
        # database being used.
        with Transaction().start(database, 0, readonly=True):
            Pool(database).init()

    with Transaction().start(database, 0):
        Cache.clean(database)

    with Transaction().start(database, user) as transaction:
        Async = Pool().get('async.async')
        DatabaseOperationalError = backend.get('DatabaseOperationalError')

        # De-serialize the payload in the transaction context so that
        # active records are constructed in the same transaction cache and
        # context.
        payload = Async.deserialize_payload(payload_json)

        try:
            with Transaction().set_context(payload['context']):
                results = Async.execute_payload(payload)
        except RetryWithDelay, exc:
            # A special error that would be raised by Tryton models to
            # retry the task after a certain delay. Useful when the task
            # got triggered before the record is ready and similar cases.
            transaction.connection.rollback()
            raise app.retry(exc=exc, countdown=exc.delay)
        except DatabaseOperationalError, exc:
            # Strict transaction handling may cause this.
            # Rollback and Retry the whole transaction if within
            # max retries, or raise exception and quit.
            transaction.connection.rollback()
            raise app.retry(exc=exc)
        except Exception, exc:
            transaction.connection.rollback()
            raise
        else:
            transaction.connection.commit()
            return results


@app.task(bind=True, default_retry_delay=2)
def execute(app, database, user, payload_json):
    return _execute(app, database, user, payload_json)
