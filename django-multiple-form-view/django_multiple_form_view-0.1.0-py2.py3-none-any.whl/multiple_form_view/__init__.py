
from collections import OrderedDict
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import ProcessFormView
from django.utils.encoding import force_text


class MultipleFormMixin(ContextMixin):
    """
    A mixin that provides a way to show and handle a heterogeneous set of forms in a
    request.

    form_classes: an ordered map of form names to form classes.
    initial: a map of form names to initial values

    """

    initial = {}
    form_classes = None
    success_url = None

    def __init__(self, *args, **kwargs):
        self.form_classes = OrderedDict(self.form_classes)
        return super(MultipleFormMixin, self).__init__(*args, **kwargs)

    def get_initial(self, name):
        """
        Returns the initial data to use for forms on this view.
        """
        self.initial.setdefault(name, {})
        return self.initial[name].copy()

    def get_prefix(self, name):
        """
        Returns the prefix to use for forms on this view
        """
        return name

    def get_form_class(self, name):
        """
        Returns the form class to use in this view
        """
        return self.form_classes[name]

    def get_form_kwargs(self, name):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            'initial': self.get_initial(name),
            'prefix': self.get_prefix(name),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_form(self, name, form_class=None):
        """
        Returns an instance of the form to be used in this view.
        """
        if form_class is None:
            form_class = self.get_form_class(name)
        return form_class(**self.get_form_kwargs(name))

    def get_forms(self, names=None, form_classes=None):
        if names is None:
            names = self.form_classes.keys()

        if form_classes is None:
            form_classes = {}

        return OrderedDict(
            [(name, self.get_form(name, form_classes.get(name, None)))
             for name in names]
        )

    def get_success_url(self):
        """
        Returns the supplied success URL.
        """
        if self.success_url:
            # Forcing possible reverse_lazy evaluation
            url = force_text(self.success_url)
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
        return url

    def forms_valid(self, forms):
        """
        If the forms are valid, redirect to the supplied URL.
        """
        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, forms):
        """
        If the forms are invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(forms=forms))


class ProcessMultipleFormsView(ProcessFormView):
    """
    A mixin that renders forms on GET and processes them on POST.
    """

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        forms = self.get_forms()
        return self.render_to_response(self.get_context_data(forms=forms))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        forms = self.get_forms()
        if all(form.is_valid() for form in forms.values()):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)


class BaseMultipleFormView(MultipleFormMixin, ProcessMultipleFormsView):
    """
    A base view for displaying a heterogeneous set of forms.
    """


class MultipleFormView(TemplateResponseMixin, BaseMultipleFormView):
    """
    A view for displaying a heterogeneous set of forms and rendering a template response.
    """
