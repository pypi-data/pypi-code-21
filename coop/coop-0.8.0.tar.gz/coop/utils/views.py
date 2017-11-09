"""
Lazily proxy a view module, preventing circular imports when used in a
models file. Useful to work with Wagtail Pages, where the view must be
defined on the model.
"""

from django.utils.functional import cached_property
from django.utils.module_loading import import_module


class ModelViewProxy(object):
    """
    Lazily proxy a view module, preventing circular imports when used in a
    models file. Useful to work with Wagtail Pages, where the view must be
    defined on the model.

    Use like:

    .. code-block:: python

        # myapp/models.py
        views = ModelViewProxy('myapp.views')

        class MyPage(Page):
            serve = views.mypage_detail

    .. code-block:: python

        # myapp/views.py
        def mypage_detail(request, mypage):
            ...

    The ``myapp.views.mypage_detail`` view will be passed arguments ``request``
    and ``page``, as well as any extra args or kwargs from the URL.
    """

    def __init__(self, view_path):
        self.view_path = view_path

    @cached_property
    def module(self):
        """Get the actual view module this instance is proxying"""
        return import_module(self.view_path)

    def __getattr__(self, name):
        """Get a proxy for a view from the proxied module with the same name"""
        return viewproxy(self, name).proxy()

    def __repr__(self):
        return '<ModelViewProxy "{0}">'.format(self.view_path)


class viewproxy(object):
    """Proxy a single view in a model, in a lazy manner."""

    def __init__(self, model_view_proxy, name):
        self.model_view_proxy = model_view_proxy
        self.name = name

    @cached_property
    def view(self):
        """The proxied view function, fetched lazily when required"""
        return getattr(self.model_view_proxy.module, self.name)

    def proxy(self):
        """Make a function that calls the proxied view."""
        def proxy(page, request, *args, **kwargs):
            return self.view(request, page, *args, **kwargs)
        return proxy
