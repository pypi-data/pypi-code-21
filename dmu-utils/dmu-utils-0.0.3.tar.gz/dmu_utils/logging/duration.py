import time
import functools

from dmu_utils.misc import get_call_repr


class Duration(object):

    def __init__(self, logger_method, operation=None, log_args=False, prefix=None):
        self.logger_method = logger_method
        self._operation = operation
        self.log_args = log_args
        self.prefix = prefix

        self.start_time = None

    def __call__(self, func_or_meth):
        @functools.wraps(func_or_meth)
        def wrapper(*args, **kwargs):
            if self._operation:
                operation = self._operation
            else:
                if self.log_args:
                    # TODO(dmu) HIGH: Handle method printing
                    operation = get_call_repr(func_or_meth, args, kwargs)
                else:
                    operation = get_call_repr(func_or_meth)

            with Duration(self.logger_method, operation=operation, log_args=self.log_args,
                          prefix=self.prefix):
                return func_or_meth(*args, **kwargs)

        return wrapper

    @property
    def operation(self):
        operation = self._operation or 'Block'
        if self.prefix:
            operation = self.prefix + operation
        return operation

    def __enter__(self):
        self.start_time = time.time()
        self.logger_method('%s started...', self.operation)

    def __exit__(self, exc_type, exc_value, traceback):
        finish_time = time.time()

        message = self.operation + ' is done in {:.06f} seconds'.format(
            finish_time - self.start_time)

        if exc_type:
            message += ' with {!r}'.format(exc_value)

        self.logger_method(message)
