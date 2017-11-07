import click
from .signals import signal
from .utils import ClassBoundDecoratorMixin, get_reloader_extra_files
from .actions import ActionFunction
from .decorators import WithActionsDecorator
from flask import current_app
from flask.cli import pass_script_info as pass_script_info_decorator
from werkzeug.serving import run_with_reloader
import inspect
import contextlib
import subprocess


before_command_signal = signal("before_command")
after_command_signal = signal("after_command")


class CommandDecorator(ClassBoundDecoratorMixin):
    """Decorator to delay creation of click commands. Allows
    usage on instance methods.
    """
    def __init__(self, func, name=None, auto_params=True, echo=True, with_app_ctx=True, with_request_ctx=False,\
                 with_reloader=False, pass_script_info=False, cls=click.Command, **options):
        self.real_func = func
        if isinstance(self.real_func, ActionFunction):
            self.real_func = self.real_func.unbound_func
        if isinstance(self.real_func, WithActionsDecorator):
            self.real_func = self.real_func.unbound_func

        self.unbound_func = func
        self.func = self._wrap_func(func)
        self.name = name or self.real_func.__name__.replace("_", "-")
        self.echo = echo
        self.with_app_ctx = with_app_ctx
        self.with_request_ctx = with_request_ctx
        self.with_reloader = with_reloader
        self.pass_script_info = pass_script_info
        self.cls = cls
        self.options = options

        if auto_params:
            self.auto_create_params()

    def auto_create_params(self):
        argspec = inspect.getargspec(self.real_func)
        args = argspec.args
        if args[0] == "self":
            del args[0]
        if self.pass_script_info and args[0] == "info":
            del args[0]
        num_mandatory_args = len(args) - len(argspec.defaults) if argspec.defaults else len(args)
        if num_mandatory_args:
            mandatory_args = args[:num_mandatory_args]
            mandatory_args.reverse()
            for arg in mandatory_args:
                if not self.has_param(arg):
                    click.argument(arg)(self.unbound_func)
        if len(args) > num_mandatory_args:
            for i, arg in enumerate(args[num_mandatory_args:]):
                if not self.has_param(arg):
                    optname = "--%s" % arg.replace("_", "-")
                    default = argspec.defaults[i]
                    if isinstance(default, bool):
                        optname += "/--no-%s" % arg.replace("_", "-")
                    click.option(optname, default=default)(self.unbound_func)

    def has_param(self, name):
        try:
            for param in self.unbound_func.__click_params__:
                if param.name == name:
                    return True
        except AttributeError:
            pass
        return False

    def as_command(self):
        """Creates the click command wrapping the function
        """
        try:
            params = self.unbound_func.__click_params__
            params.reverse()
            del self.unbound_func.__click_params__
        except AttributeError:
            params = []
        help = inspect.getdoc(self.real_func)
        if isinstance(help, bytes):
            help = help.decode('utf-8')
        self.options.setdefault('help', help)
        @pass_script_info_decorator
        def callback(info, *args, **kwargs):
            if self.with_reloader:
                app = info.load_app()
                if app.debug:
                    def inner():
                        return self.command_callback(info, *args, **kwargs)
                    run_with_reloader(inner, extra_files=get_reloader_extra_files())
                    return
            self.command_callback(info, *args, **kwargs)
        return self.cls(name=self.name, callback=callback, params=params, **self.options)

    @contextlib.contextmanager
    def conditional_app_ctx(self, info):
        if self.with_app_ctx:
            with info.load_app().app_context():
                yield
        else:
            yield

    @contextlib.contextmanager
    def conditional_request_ctx(self):
        if self.with_request_ctx:
            kwargs = self.with_request_ctx
            if isinstance(kwargs, str):
                kwargs = {"path": kwargs}
            with current_app.test_request_context(**kwargs):
                yield
        else:
            yield

    def command_callback(self, info, *args, **kwargs):
        if self.pass_script_info:
            args = list(args)
            args.insert(0, info)
        before_command_signal.send(self)
        with self.conditional_app_ctx(info), self.conditional_request_ctx():
            rv = None
            try:
                rv = self.func(*args, **kwargs)
                if rv and self.echo:
                    click_echo_formated(rv)
            except Exception as e:
                if current_app.debug:
                    raise
                click.secho("ERROR of type %s: %s" % (type(e).__name__, e.message), fg="red", bold=True)
        after_command_signal.send(self)

    def format(self, value):
        if isinstance(value, (list, tuple, set)):
            return "\n".join([" - %s" % v for v in value])
        elif isinstance(value, dict):
            return "\n".join([" - %s: %s" % (k, v) for k, v in value.iteritems()])
        return value

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def click_echo_formated(value, **kwargs):
    if isinstance(value, (list, tuple, set)):
        value = "\n".join([" - %s" % v for v in value])
    elif isinstance(value, dict):
        value = "\n".join([" - %s: %s" % (k, v) for k, v in value.iteritems()])
    click.secho(str(value), **kwargs)


def command(*args, **kwargs):
    def decorator(f):
        return CommandDecorator(f, *args, **kwargs)
    return decorator

command.opt = click.option
command.arg = click.argument
command.echo = click_echo_formated


class ShellError(Exception):
    def __init__(self, returncode, stderr):
        super(ShellError, self).__init__(stderr)
        self.returncode = returncode
        self.stderr = stderr


def shell_exec(args, echo=True, fg="green", **kwargs):
    kwargs["stdout"] = subprocess.PIPE
    kwargs["stderr"] = subprocess.STDOUT
    p = subprocess.Popen(args, **kwargs)
    out, _ = p.communicate()
    if p.returncode > 0:
        raise ShellError(p.returncode, out)
    if echo:
        click.secho(out, fg=fg)
    return out
    