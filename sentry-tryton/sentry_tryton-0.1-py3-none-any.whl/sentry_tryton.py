# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import pkg_resources

from raven.handlers.logging import SentryHandler
from raven.processors import Processor
from trytond import backend
from trytond.exceptions import UserError
from trytond.transaction import Transaction

__version__ = '0.1'
__all__ = ['TrytonProcessor', 'SentryTrytonHandler']


class TrytonProcessor(Processor):

    def __init__(self, client):
        super(TrytonProcessor, self).__init__(client)
        self.modules = {}
        for module in pkg_resources.WorkingSet():
            self.modules[module.key] = module.version

    def get_data(self, data, **kwargs):
        user = {}
        extra = {}
        database = None
        # Must be imported once the logging is set
        from trytond.pool import Pool
        try:
            # Must not fail if connection is not available
            pool = Pool()
        except Exception:
            pool = None
        transaction = Transaction()
        if transaction:
            user['id'] = transaction.user
            extra.update({
                'backend': backend.name(),
                'context': transaction.context,
                'readonly': transaction.readonly,
                })
            if transaction.database:
                database = transaction.database.name
                extra['database'] = database
        if pool:
            try:
                User = pool.get('res.user')
                tryton_user = User(user['id'])
                user.update({
                    'username': tryton_user.rec_name,
                    'login': tryton_user.login,
                    'email': tryton_user.email,
                    })
            except Exception:
                pass
            if database:
                activated_modules = {}
                try:
                    Module = pool.get('ir.module')
                    for module in Module.search([
                                ('state', '=', 'activated'),
                                ]):
                        activated_modules[module.name] = module.version
                except Exception:
                    pass
                extra['activated_modules'] = activated_modules
        return {
            'modules': self.modules,
            'user': user,
            'extra': extra
            }


class SentryTrytonHandler(SentryHandler):

    def __init__(
            self, dsn, error_msg=None, error_description=None, extra_args=None,
            **kwargs):
        # Replace {event_id} as its not possible to use format expresions
        # when using fileConfig
        self.error_msg = error_msg.replace('{event_id}', '%(event_id)s')
        self.error_description = error_description.replace(
            '{event_id}', '%(event_id)s')
        if isinstance(extra_args, dict):
            kwargs.update(extra_args)
        super(SentryTrytonHandler, self).__init__(dsn=dsn, **kwargs)
        self.client.processors += ('sentry_tryton.TrytonProcessor',)

    def emit(self, record):
        event_id = super(SentryTrytonHandler, self).emit(record)
        if self.error_msg:
            message_args = {
                    'event_id': event_id,
                    }
            msg = self.error_msg % message_args
            description = ''
            if self.error_description:
                description = self.error_description % message_args
            raise UserError(msg, description)
        return event_id
