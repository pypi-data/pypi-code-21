import os
from distutils.spawn import find_executable

from simpleflow import execute

PYTHON = os.getenv('BOTIFY_CDF_PYPY_PATH') or '/home/zeb/.virtualenvs/pypy-5.7/bin/python'


def with_pypy(interpreter, fallback_interpreter='python', enable=True):
    def wrapped(func):
        if not enable:
            return func

        py_interpreter = interpreter
        if not find_executable(py_interpreter):
            msg = 'will not be able to execute {}: ' \
                'interpreter {} not found'.format(
                    getattr(func, 'func_name', func.__name__),
                    py_interpreter,
                )

            if not fallback_interpreter:
                raise RuntimeError(msg)

            print(msg + ' (continuing...)')
            py_interpreter = fallback_interpreter

        f = execute.python(py_interpreter)(func)
        return f

    return wrapped


@with_pypy(PYTHON)
def fn():
    import sys
    return 'Python Version: {}'.format(sys.version)
