# -*- coding: utf-8 -*-

from django.forms import ModelChoiceField, ModelForm, TextInput, ValidationError
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.template.loader import get_template

from navsy import cache
from navsy.models import Page, Pattern, Route
from navsy.utils import import_function, path_utils, pattern_utils


class PageChoiceField(ModelChoiceField):

    def label_from_instance(self, obj):
        page_data = cache.get_page_data(obj.pk)
        return ' / '.join(page_data.get('path_names', []))


class PageForm(ModelForm):

    parent = PageChoiceField(
        queryset=Page.objects.exclude(home=True),
        required=False)

    class Meta:
        model = Page
        fields = '__all__'

    def clean_home(self):

        home = self.cleaned_data.get('home')
        parent = self.cleaned_data.get('parent')

        if home and parent:
            raise ValidationError(
                'Only pages without parent can be set as home.')
        else:
            return home


class PatternForm(ModelForm):

    class Meta:

        model = Pattern
        fields = '__all__'

    def clean_regex(self):

        regex = self.cleaned_data.get('regex', '')

        if regex:
            regex = regex.strip()

        if regex:
            if regex.startswith('/'):
                regex = regex[1:]

        if regex:
            if regex.endswith('/'):
                regex = regex[0:-1]

        try:
            pattern_utils.get_regex_re('/', regex)

        except Exception as e:
            raise ValidationError('Invalid regex. %s.' % (str(e), ))

        return regex


class RouteForm(ModelForm):

    class Meta:
        model = Route
        fields = '__all__'

    def clean_redirect_to_first_child_page(self):

        redirect_to_first_child_page = self.cleaned_data.get(
            'redirect_to_first_child_page')

        if redirect_to_first_child_page:

            route_obj = self.save(commit=False)
            route_page = route_obj.page

            if route_page:
                if route_page.children.count() == 0:
                    raise ValidationError(
                        'Invalid redirect. Page has not children pages.')
            else:
                raise ValidationError('Invalid redirect. Page cannot be None.')

        return redirect_to_first_child_page

    def clean_redirect_to_page(self):

        redirect_to_page = self.cleaned_data.get('redirect_to_page')

        if redirect_to_page:

            route_obj = self.save(commit=False)
            route_url = route_obj.url
            redirect_url = redirect_to_page.url

            if redirect_url == route_url:
                raise ValidationError('Invalid redirect. \
                    Redirect url "%s" cannot be equal \
                    to route url "%s".' % (redirect_url, route_url, ))

        return redirect_to_page

    def clean_redirect_to_path(self):

        redirect_to_path = self.cleaned_data.get('redirect_to_path')

        if redirect_to_path:
            redirect_to_path = redirect_to_path.strip()

        if redirect_to_path:
            absolute_url_prefixes = ['http://', 'https://', '//']

            for absolute_url_prefix in absolute_url_prefixes:

                if redirect_to_path.startswith(absolute_url_prefix):
                    raise ValidationError(
                        'Invalid redirect. \
                        Redirect path can not be an absolute url, \
                        but it can start with /.')

            redirect_from_root = redirect_to_path.startswith('/')
            redirect_to_path = path_utils.fix_path(redirect_to_path)

            if not redirect_from_root:
                redirect_to_path = redirect_to_path[1:]

            if redirect_to_path.endswith('/') and len(redirect_to_path) > 1:
                redirect_to_path = redirect_to_path[0:-1]

        return redirect_to_path

    def clean_view_template_path(self):

        view_template_path = self.cleaned_data.get('view_template_path')

        if view_template_path:
            view_template_path = view_template_path.strip()

        if view_template_path:
            try:
                view_template = get_template(view_template_path)

            except TemplateDoesNotExist:
                raise ValidationError(
                    'Invalid template path. Template not found at path: \
                    "%s".' % (view_template_path, ))

            except TemplateSyntaxError:
                raise ValidationError(
                    'Invalid template syntax for template at path: \
                    "%s".' % (view_template_path, ))

        return view_template_path

    def clean_view_function_path(self):

        view_function_path = self.cleaned_data.get('view_function_path')

        if view_function_path:
            view_function_path = view_function_path.strip()

        if view_function_path:
            view_function = import_function(view_function_path)

            if not view_function:
                raise ValidationError('Invalid view function path. \
                    View function not found at path: \
                    "%s".' % (view_function_path, ))

        return view_function_path

    def clean_view_name(self):

        view_name = self.cleaned_data.get('view_name')

        if view_name:
            view_name = view_name.strip()

        return view_name or None


class RouteInlineForm(RouteForm):

    def __init__(self, *args, **kwargs):

        super(RouteInlineForm, self).__init__(*args, **kwargs)

        self.fields['view_name'].widget = TextInput(attrs={'size': '25'})
        self.fields['priority'].widget = TextInput(attrs={'size': '5'})
