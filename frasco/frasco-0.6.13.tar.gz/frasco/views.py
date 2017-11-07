import flask
import flask.views
from flask.helpers import locked_cached_property
from jinja2 import FileSystemLoader, PrefixLoader
import yaml
from .utils import AttrDict, logger
from .actions import (ActionList, execute_actions, ContextExitException, current_context,\
                     execute_action, load_actions, ReturnValueException)
from .decorators import hook, register_hooks, expose, WithActionsDecorator
import os
import inspect


def exec_before_request_actions(actions, **kwargs):
    """Execute actions in the "before" and "before_METHOD" groups
    """
    groups = ("before", "before_" + flask.request.method.lower())
    return execute_actions(actions, limit_groups=groups, **kwargs)


def exec_request_actions(actions, **kwargs):
    """Execute actions in the None and METHOD groups
    """
    groups = (None, flask.request.method.lower())
    return execute_actions(actions, limit_groups=groups, **kwargs)


def exec_after_request_actions(actions, response, **kwargs):
    """Executes actions of the "after" and "after_METHOD" groups.
    A "response" var will be injected in the current context.
    """
    current_context["response"] = response
    groups = ("after_" + flask.request.method.lower(), "after")
    try:
        rv = execute_actions(actions, limit_groups=groups, **kwargs)
    except ReturnValueException as e:
        rv = e.value
    if rv:
        return rv
    return response


def full_exec_request_actions(actions, func=None, render_func=None):
    """Full process to execute before, during and after actions.
    If func is specified, it will be called after exec_request_actions()
    unless a ContextExitException was raised. If render_func is specified,
    it will be called after exec_request_actions() only if there is no
    response. exec_after_request_actions() is always called.
    """
    response = None
    try:
        exec_before_request_actions(actions, catch_context_exit=False)
        exec_request_actions(actions, catch_context_exit=False)
        if func:
            response = func()
    except ContextExitException as e:
        response = e.result
    except ReturnValueException as e:
        response = e.value
    if render_func and response is None:
        response = render_func()
    return exec_after_request_actions(actions, response)


class RegistrableViewMixin(object):
    """A mixin to add the register() method to views. This method is
    called when a blueprint is registered
    """
    name = None
    # If url_rules is None, an url rule will be created using url and methods
    url = None
    methods = None
    url_rules = None

    def __init__(self, name=None, url=None, methods=None, url_rules=None):
        if name is not None:
            self.name = name
        elif self.name is None:
            self.name = self.__class__.__name__
        if url_rules is not None:
            self.url_rules = url_rules
        elif self.url_rules is None:
            url = url or self.url or "/" + self.name
            if isinstance(url, str):
                url = [url]
            methods = methods or self.methods
            self.url_rules = [(u, {"methods": methods}) for u in url]

    def register(self, target):
        """Registers url_rules on the blueprint
        """
        for rule, options in self.url_rules:
            target.add_url_rule(rule, self.name, self.dispatch_request, **options)


class View(RegistrableViewMixin, flask.views.View):
    """Same as flask.views.View but with RegistrableViewMixin"""


class MethodView(RegistrableViewMixin, flask.views.MethodView):
    """Same as flask.views.MethodView but with RegistrableViewMixin"""


class ActionsView(View):
    """Executes a list of actions and renders a template.
    """
    actions = None
    template = None
    auto_render = True
    func = None

    def __init__(self, name=None, actions=None, func=None, template=None, auto_render=None,
                 self_var=None, **kwargs):
        super(ActionsView, self).__init__(name=name, **kwargs)
        self.actions = ActionList(actions or self.actions or [])
        self.func = func or self.func
        if template is not None:
            self.template = template
        if auto_render is not None:
            self.auto_render = auto_render
        self.self_var = self_var or self

    def add_action(self, action):
        self.actions.append(action)

    def register(self, target):
        self.actions.init_view(self)
        default_methods = self.actions.methods
        for rule, options in self.url_rules:
            if options.get("methods") is None:
                options["methods"] = default_methods
            logger.info("Registering url rule '%s' with url '%s' on methods %s" % (self.name, rule, options["methods"]))
            target.add_url_rule(rule, self.name, self.dispatch_request, **options)

    def dispatch_request(self, *args, **kwargs):
        logger.debug("Dispatching view %s" % self.name)
        current_context.vars.self = self.self_var
        r = self.execute_actions(*args, **kwargs)
        current_context.vars.pop('self', None)
        return r

    def execute_actions(self, *args, **kwargs):
        func = None
        if self.func:
            func = lambda: self.func(*args, **kwargs)
        return full_exec_request_actions(self.actions, func=func, render_func=self._auto_render_func)

    def _auto_render_func(self):
        if self.auto_render:
            current_context.vars.pop('self', None)
            return self.render(**current_context.vars)

    def render(self, **kwargs):
        if self.template is not None:
            logger.debug("Rendering template %s" % self.template)
            return flask.render_template(self.template, **kwargs)


def as_view(url=None, methods=None, view_class=ActionsView, name=None, url_rules=None, **kwargs):
    """Decorator to transform a function into a view class. Be warned that this will replace
    the function with the view class.
    """
    def decorator(f):
        if url is not None:
            f = expose(url, methods=methods)(f)

        clsdict = {"name": name or f.__name__,
                   "actions": getattr(f, "actions", None),
                   "url_rules": url_rules or getattr(f, "urls", None)}

        if isinstance(f, WithActionsDecorator):
            f = f.func
        clsdict['func'] = f

        def constructor(self, **ctorkwargs):
            for k, v in kwargs.items():
                if k not in ctorkwargs or ctorkwargs[k] is None:
                    ctorkwargs[k] = v
            view_class.__init__(self, func=f, **ctorkwargs)

        clsdict["__init__"] = constructor
        return type(f.__name__, (view_class,), clsdict)

    return decorator


class ViewContainerMixin(object):
    """Mixin to add view registration on a class.
    """
    view_class = ActionsView

    def add_view(self, view):
        rv = view
        if inspect.isclass(view):
            view = view(self_var=self)
        self.views[view.name] = view
        return rv

    def view(self, *args, **kwargs):
        """Decorator to automatically apply as_view decorator and register it.
        """
        def decorator(f):
            kwargs.setdefault("view_class", self.view_class)
            return self.add_view(as_view(*args, **kwargs)(f))
        return decorator

    def add_action_view(self, name, url, actions, **kwargs):
        """Creates an ActionsView instance and registers it.
        """
        view = ActionsView(name, url=url, self_var=self, **kwargs)
        if isinstance(actions, dict):
            for group, actions in actions.iteritems():
                view.actions.extend(load_actions(actions, group=group or None))
        else:
            view.actions.extend(load_actions(actions))
        self.add_view(view)
        return view


class Blueprint(ViewContainerMixin, flask.Blueprint):
    """Blueprint class which adds support for actions before/after request
    and to add views
    """
    name = None
    url_prefix = None
    subdomain = None

    def __init__(self, name=None, import_name=None, *args, **kwargs):
        if (name is None or import_name is None) and self.__class__ == Blueprint:
            raise AttributeError("Missing name and import_name parameter. Omitting them requires to subclass Blueprint")
        self.template_prefix = kwargs.pop('template_prefix', None)
        kwargs.setdefault('url_prefix', self.url_prefix)
        kwargs.setdefault('subdomain', self.subdomain)
        super(Blueprint, self).__init__(name or self.name or self.__class__.__name__,
            import_name or self.__class__.__module__, *args, **kwargs)
        self.request_actions = ActionList()
        self.views = {}
        self.register_defaults()

    def register_defaults(self):
        for attr in dir(self):
            attr = getattr(self, attr)
            if hasattr(attr, "urls"):
                self.view()(attr)
            elif hasattr(attr, 'hooks'):
                register_hooks(attr, attr.hooks, self)

    def add_request_action(self, action):
        self.request_actions.append(action)

    @locked_cached_property
    def jinja_loader(self):
        if self.template_folder is None:
            return
        loader = FileSystemLoader(os.path.join(self.root_path, self.template_folder))
        if self.template_prefix:
            loader = PrefixLoader(dict([(self.template_prefix, loader)]))
        return loader

    @hook('record')
    def register_views(self, state):
        logger.info("Registering blueprint '%s' (url_prefix=%s, subdomain=%s)" % (self.name, self.url_prefix, self.subdomain))
        for view in self.views.values():
            view.register(self)

    @hook('before_request')
    def exec_before_request_actions(self, *args, **kwargs):
        try:
            exec_before_request_actions(self.request_actions, catch_context_exit=False)
            exec_request_actions(self.request_actions, catch_context_exit=False)
        except ContextExitException as e:
            return e.result

    @hook('after_request')
    def exec_after_request_actions(self, response):
        return exec_after_request_actions(self.request_actions, response)
