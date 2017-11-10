# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.html import escape

from autoslug import AutoSlugField

from navsy import cache
from navsy.tree.models import NodeModel
from navsy.utils import i18n_utils, path_utils, pattern_utils, url_utils


@python_2_unicode_compatible
class Page(NodeModel):

    name = models.CharField(max_length=100)
    slug = AutoSlugField(
        populate_from='name', unique=True, always_update=True, blank=True, null=True)
    home = models.BooleanField(default=False)
    menu = models.BooleanField(default=True)
    published = models.BooleanField(default=True)

    @staticmethod
    def create_default_objects():
        if Page.objects.count() == 0:
            page_obj = Page.objects.create(name='Home', home=True, menu=False)
            page_obj.create_default_route()

    def create_default_route(self):
        pattern_obj, pattern_created = Pattern.objects.get_or_create(
            regex='')
        route_obj, route_created = Route.objects.get_or_create(
            page=self, pattern=pattern_obj)
        return (route_obj, route_created, )

    def update_unique_home(self):
        if self.home:
            Page.objects.exclude(pk=self.pk).update(home=False)

    def __get_absolute_path(self):
        page_data = cache.get_page_data(self.pk)
        page_path = page_data.get('path', '')
        abs_path = path_utils.fix_path(page_path)
        # print(abs_path)
        return abs_path

    def get_absolute_url(self, language=None):
        abs_url = i18n_utils.call_function_for_language(
            self.__get_absolute_path, language)
        abs_url = url_utils.reverse_url(abs_url)
        # print(abs_url)
        return abs_url

    @property
    def url(self):
        return self.get_absolute_url()

    class Meta:
        ordering = ['-priorities']
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'

    def __str__(self):
        return force_text(self.name)


@python_2_unicode_compatible
class Pattern(models.Model):

    @staticmethod
    def create_default_objects():
        default_regexs = pattern_utils.get_default_regexs()
        # print(default_regexs)
        for regex in default_regexs:
            Pattern.objects.get_or_create(regex=regex)

    regex = models.CharField(
        max_length=255, blank=True, default='', unique=True)
    regex_display = models.CharField(
        max_length=255, blank=True, default='', editable=False)
    regex_format = models.CharField(
        max_length=255, blank=True, default='', editable=False)

    def update_regex_strings(self):
        self.regex_display = pattern_utils.get_regex_display(self.regex)
        self.regex_format = pattern_utils.get_regex_format(self.regex)

    class Meta:
        ordering = ['regex']
        verbose_name = 'Pattern'
        verbose_name_plural = 'Patterns'

    def __str__(self):
        return force_text(self.regex_display)


@python_2_unicode_compatible
class Route(models.Model):

    page = models.ForeignKey(
        'navsy.Page', blank=True, null=True,
        on_delete=models.CASCADE, related_name='routes')
    pattern = models.ForeignKey(
        'navsy.Pattern', on_delete=models.CASCADE)

    view_name = models.CharField(
        max_length=100, unique=True, blank=True, null=True, db_index=True,
        help_text='(unique name used for reverse URL)')
    view_function_path = models.CharField(
        max_length=100, blank=True, help_text='(ex. app.views.view_func)')
    view_template_path = models.CharField(
        max_length=100, blank=True, help_text='(ex. app/template.html)')

    # TODO: add redirect_condition and redirect_to_home_page field
    # redirect_condition = Always, if anonymous user, if logged user, if staff user, if superuser
    # redirect_to_home_page = models.BooleanField(default=False)
    redirect_to_first_child_page = models.BooleanField(default=False)
    redirect_to_page = models.ForeignKey(
        'navsy.Page', blank=True, null=True, on_delete=models.SET_NULL)
    redirect_to_path = models.CharField(max_length=200, blank=True)
    redirect_to_url = models.URLField(blank=True)

    priority = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(9999)])

    published = models.BooleanField(default=True)

    def __get_absolute_url_internal(self, regex_type_key):
        route_data = cache.get_route_data(self.pk)
        route_path = route_data.get(regex_type_key, '')
        page_data = route_data.get('page', {})
        page_path = page_data.get('path', '')
        abs_page_path = path_utils.fix_path(page_path)
        abs_page_url = url_utils.reverse_url(abs_page_path)
        abs_url = path_utils.fix_path(abs_page_url, route_path)
        abs_url = escape(abs_url)
        # print(abs_url)
        return abs_url

    def __get_absolute_url_for_language(self, language, regex_type_key):
        return i18n_utils.call_function_for_language(
            self.__get_absolute_url_internal, language, [regex_type_key])

    def __get_absolute_url_display(self, language=None):
        return self.__get_absolute_url_for_language(language, 'regex_display')

    def __get_absolute_url_format(self, language=None):
        return self.__get_absolute_url_for_language(language, 'regex_format')

    def __get_absolute_url_regex(self, language=None):
        return self.__get_absolute_url_for_language(language, 'regex')

    def get_absolute_url(self, language=None, parameters=None):
        abs_url_format = self.__get_absolute_url_format(language)
        abs_url = url_utils.format_url(abs_url_format, parameters)
        return abs_url

    @property
    def url_display(self):
        return self.__get_absolute_url_display()

    @property
    def url_format(self):
        return self.__get_absolute_url_format()

    @property
    def url_regex(self):
        return self.__get_absolute_url_regex()

    @property
    def url(self):
        return self.__get_absolute_url_format()

    def get_redirect_url(self):

        redirect_url = None

        route_data = cache.get_route_data(self.pk)
        page_data = route_data.get('page', {})
        page_obj = page_data.get('object')

        if self.redirect_to_first_child_page and page_obj and page_obj.children_count > 0:
            first_child_page_pk = page_obj.get_children_pks()[0]
            first_child_page_data = cache.get_page_data(first_child_page_pk)
            first_child_page_obj = first_child_page_data.get('object')
            redirect_url = first_child_page_obj.url

        elif self.redirect_to_page:
            redirect_url = self.redirect_to_page.url

        elif self.redirect_to_url:
            redirect_url = self.redirect_to_url

        elif self.redirect_to_path:
            if self.redirect_to_path.startswith('/'):
                redirect_path = self.redirect_to_path
            else:
                redirect_path = page_obj.url if page_obj else '/'  # base_url
            redirect_url = path_utils.fix_path(redirect_path, self.redirect_to_path)

        # if redirect_url:
        #    print(redirect_url)

        return redirect_url

    @property
    def redirect_url(self):
        return self.get_redirect_url()

    # # TODO: impossible to save more routes without view_name programatically
    # # (not using the admin interface) - write signal on pre_save
    # def save(self, *args, **kwargs):
    #     if not self.view_name:
    #         self.view_name = None
    #     super(Route, self).save(*args, **kwargs)

    class Meta:
        unique_together = (('page', 'pattern', ), )
        ordering = ['page', '-priority']
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'

    def __str__(self):
        # TODO: Fix admin messages escaped html
        # "The Route "/en/&lt;file_name&gt;.&lt;file_ext&gt;" was changed successfully.
        # You may edit it again below."
        return force_text(self.url_display)
