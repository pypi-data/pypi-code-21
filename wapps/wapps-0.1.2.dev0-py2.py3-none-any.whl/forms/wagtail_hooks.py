import types
import json
import os

from django.apps import apps
from django.conf.urls import url
from django.contrib.admin.utils import quote
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe


from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from wagtail.contrib.modeladmin.helpers import AdminURLHelper, ButtonHelper, PermissionHelper

from .models import BaseForm, FormSubmission, file_url
from .views import CreateAdminView, EditAdminView, DeleteAdminView, SubmissionsView


def _get_valid_subclasses(cls):
    clss = []
    for subcls in cls.__subclasses__():
        if subcls._meta.abstract:
            continue
        clss.append(subcls)
        sub_classes = _get_valid_subclasses(subcls)
        if sub_classes:
            clss.extend(sub_classes)
    return clss


def field_getter(field):
    return 'display_{0}'.format(field.clean_name.replace('-', '_'))


def fields_for(fields, **query):
    return [field_getter(f) for f in fields.filter(**query)]


def db_fields_for(fields, **query):
    return ['form_data__{0}'.format(f.clean_name) for f in fields.filter(**query)]


def method_for_field(field, cls):
    method_name = field_getter(field)
    field_name = field.clean_name

    def method(self, obj):
        if isinstance(obj.form_data, str):
            # See:
            obj.form_data = json.loads(obj.form_data)
        value = obj.form_data[field_name]
        if field.field_type == 'file':
            return mark_safe('<a href="{0}" target="_blank">{1}</a>'.format(
                file_url(value), os.path.basename(value)
            ))
        return value

    method.__name__ = method_name
    method.short_description = field.label
    return types.MethodType(method, cls)


class FormsUrlHelper(AdminURLHelper):
    @property
    def root_url(self):
        return r'^%s/' % self.opts.app_label

    @property
    def model_url(self):
        return self.root_url + r'(?P<app_label>\w+)/(?P<model_name>\w+)/'

    @property
    def instance_url(self):
        return self.model_url + r'(?P<instance_pk>[-\w]+)/'

    def _get_action_url_pattern(self, action):
        if action == 'index':
            return self.root_url + r'$'
        return self.model_url + r'%s/$' % action

    def _get_object_specific_action_url_pattern(self, action):
        if action == 'submissions':
            return self.instance_url + r'$'
        return self.instance_url + r'%s/$' % action

    def get_action_url_pattern(self, action):
        if action in ('create', 'index'):
            return self._get_action_url_pattern(action)
        return self._get_object_specific_action_url_pattern(action)

    def get_action_url_name(self, action):
        return 'wapps_forms_admin_%s' % action

    def get_action_url(self, action, *args, **kwargs):
        if action == 'index':
            return reverse(self.get_action_url_name(action))
        url_name = self.get_action_url_name(action)
        return reverse(url_name, args=args, kwargs=kwargs)

    @cached_property
    def index_url(self):
        return self.get_action_url('index')

    @cached_property
    def create_url(self):
        return '#'


class FormsButtonHelper(ButtonHelper):
    def add_button(self, classnames_add=None, classnames_exclude=None):
        attrs = super().add_button(classnames_add=classnames_add,
                                   classnames_exclude=classnames_exclude)

        return {
            'label': _('Add a form'),
            'title': _('Add a new form'),
            'classname': attrs['classname'],
            'url': '#',
            'entries': [
                {
                    # 'title': _('Add a new %s'),
                    'label': _('Add %s') % model._meta.verbose_name,
                    'classname': [],
                    'title': _('Add a new %s') % model._meta.verbose_name,
                    'url': self.url_helper.get_action_url('create', **{
                        'app_label': model._meta.app_label,
                        'model_name': model._meta.model_name
                    })
                }
                for model in _get_valid_subclasses(BaseForm)
            ]
        }

    def inspect_button(self, app_label, model_name, pk, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        classnames = self.inspect_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        return {
            'url': self.url_helper.get_action_url('inspect', app_label, model_name, quote(pk)),
            'label': _('Inspect'),
            'classname': cn,
            'title': _('Inspect this %s') % self.verbose_name,
        }

    def edit_button(self, app_label, model_name, pk, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        classnames = self.edit_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        return {
            'url': self.url_helper.get_action_url('edit', app_label, model_name, quote(pk)),
            'label': _('Edit'),
            'classname': cn,
            'title': _('Edit this %s') % self.verbose_name,
        }

    def submissions_button(self, app_label, model_name, pk, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        classnames = self.edit_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        return {
            'url': self.url_helper.get_action_url('submissions', app_label, model_name, quote(pk)),
            'label': _('Submissions'),
            'classname': cn,
            'title': _('See submissions for this form')
        }

    def delete_button(self, app_label, model_name, pk, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        classnames = self.delete_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        return {
            'url': self.url_helper.get_action_url('delete', app_label, model_name, quote(pk)),
            'label': _('Delete'),
            'classname': cn,
            'title': _('Delete this %s') % self.verbose_name,
        }

    def get_buttons_for_obj(self, obj, exclude=None, classnames_add=None,
                            classnames_exclude=None):
        if exclude is None:
            exclude = []
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        ph = self.permission_helper
        usr = self.request.user
        pk = getattr(obj, obj._meta.pk.attname)
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name
        btns = []
        if ('inspect' not in exclude and ph.user_can_inspect_obj(usr, obj)):
            btns.append(
                self.inspect_button(app_label, model_name, pk, classnames_add, classnames_exclude)
            )
        if ('edit' not in exclude and ph.user_can_edit_obj(usr, obj)):
            btns.append(
                self.edit_button(app_label, model_name, pk, classnames_add, classnames_exclude)
            )
        if (obj.store_submission and 'submissions' not in exclude and ph.user_can_edit_obj(usr, obj)):
            btns.append(
                self.submissions_button(app_label, model_name, pk, classnames_add, classnames_exclude)
            )
        if ('delete' not in exclude and ph.user_can_delete_obj(usr, obj)):
            btns.append(
                self.delete_button(app_label, model_name, pk, classnames_add, classnames_exclude)
            )
        return btns


class NestedButtonHelper(ButtonHelper):
    def __init__(self, model, request):
        self.request = request
        self.model = model
        self.opts = model._meta
        self.verbose_name = force_text(self.opts.verbose_name)
        self.verbose_name_plural = force_text(self.opts.verbose_name_plural)
        self.permission_helper = PermissionHelper(model)
        self.url_helper = AdminURLHelper(model)


class FormModelAdmin(ModelAdmin):
    def __init__(self, parent):
        super().__init__(parent)
        self.url_helper = parent.url_helper


@modeladmin_register
class FormsAdmin(ModelAdmin):
    model = BaseForm
    # menu_label = _('Form definitions')
    menu_icon = 'icon icon-table'
    list_display = ('name', 'form_type')
    # list_filter = ('form', )
    index_template_name = 'forms/admin/index.html'
    button_helper_class = FormsButtonHelper
    url_helper_class = FormsUrlHelper
    create_view_class = CreateAdminView
    edit_view_class = EditAdminView
    delete_view_class = DeleteAdminView
    submissions_view_class = SubmissionsView

    def form_type(self, obj):
        return obj._meta.verbose_name
    form_type.short_description = _('Form type')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_subclasses()

    def get_admin_urls_for_registration(self):
        urls = (
            url(self.url_helper.get_action_url_pattern('index'),
                self.index_view,
                name=self.url_helper.get_action_url_name('index')),
            url(self.url_helper.get_action_url_pattern('create'),
                self.create_view,
                name=self.url_helper.get_action_url_name('create')),
            url(self.url_helper.get_action_url_pattern('edit'),
                self.edit_view,
                name=self.url_helper.get_action_url_name('edit')),
            url(self.url_helper.get_action_url_pattern('submissions'),
                self.submissions_view,
                name=self.url_helper.get_action_url_name('submissions')),
            url(self.url_helper.get_action_url_pattern('delete'),
                self.delete_view,
                name=self.url_helper.get_action_url_name('delete')),
        )
        if self.inspect_view_enabled:
            urls = urls + (
                url(self.url_helper.get_action_url_pattern('inspect'),
                    self.inspect_view,
                    name=self.url_helper.get_action_url_name('inspect')),
            )
        return urls

    def admin_class_for(self, model):
        object_name = model._meta.object_name
        class_name = "{}Admin".format(object_name)
        definition = {
            'model': model,
            'create_view_class': self.create_view_class,
            # 'menu_label': cls._meta.verbose_name,
            # 'menu_order': 100,
            'menu_icon': 'icon icon-form',
        }
        return type(class_name, (FormModelAdmin, ), definition)

    def submissions_admin_class_for(self, form):
        form_name = form.name
        class_name = '{0}FormAdmin'.format(form_name)
        definition = {
            'model': FormSubmission,
            'menu_label': form.name,
            'menu_icon': 'icon icon-table',
            'list_display': fields_for(form.form_fields, admin_display=True) + ['submit_time'],
            # Commented while https://code.djangoproject.com/ticket/26184
            # 'list_filter': db_fields_for(form.form_fields, admin_filter=True),
            # 'search_fields': db_fields_for(form.form_fields, admin_search=True),
            'get_queryset': lambda self, request: FormSubmission.objects.filter(form=form),
        }
        cls = type(class_name, (FormModelAdmin, ), definition)
        for field in form.form_fields.all():
            method = method_for_field(field, cls)
            setattr(cls, method.__name__, method)
        return cls

    def create_view(self, request, app_label, model_name):
        """
        Instantiates a class-based view to provide 'creation' functionality for
        the assigned model, or redirect to Wagtail's create view if the
        assigned model extends 'Page'. The view class used can be overridden by
        changing the 'create_view_class' attribute.
        """
        model = apps.get_model(app_label, model_name)
        admin_class = self.admin_class_for(model)
        admin = admin_class(self)
        kwargs = {'model_admin': admin}
        view_class = self.create_view_class
        return view_class.as_view(**kwargs)(request)

    def inspect_view(self, request, app_label, model_name, instance_pk):
        """
        Instantiates a class-based view to provide 'inspect' functionality for
        the assigned model. The view class used can be overridden by changing
        the 'inspect_view_class' attribute.
        """
        model = apps.get_model(app_label, model_name)
        admin_class = self.admin_class_for(model)
        admin = admin_class(self)
        kwargs = {'model_admin': admin, 'instance_pk': instance_pk}
        view_class = self.inspect_view_class
        return view_class.as_view(**kwargs)(request)

    def edit_view(self, request, app_label, model_name, instance_pk):
        """
        Instantiates a class-based view to provide 'edit' functionality for the
        assigned model, or redirect to Wagtail's edit view if the assinged
        model extends 'Page'. The view class used can be overridden by changing
        the  'edit_view_class' attribute.
        """
        model = apps.get_model(app_label, model_name)
        admin_class = self.admin_class_for(model)
        admin = admin_class(self)
        kwargs = {'model_admin': admin, 'instance_pk': instance_pk}
        view_class = self.edit_view_class
        return view_class.as_view(**kwargs)(request)

    def delete_view(self, request, app_label, model_name, instance_pk):
        """
        Instantiates a class-based view to provide 'delete confirmation'
        functionality for the assigned model, or redirect to Wagtail's delete
        confirmation view if the assinged model extends 'Page'. The view class
        used can be overridden by changing the 'delete_view_class'
        attribute.
        """
        model = apps.get_model(app_label, model_name)
        admin_class = self.admin_class_for(model)
        admin = admin_class(self)
        kwargs = {'model_admin': admin, 'instance_pk': instance_pk}
        view_class = self.delete_view_class
        return view_class.as_view(**kwargs)(request)

    def submissions_view(self, request, app_label, model_name, instance_pk):
        """
        Instantiates a class-based view to provide 'delete confirmation'
        functionality for the assigned model, or redirect to Wagtail's delete
        confirmation view if the assinged model extends 'Page'. The view class
        used can be overridden by changing the 'delete_view_class'
        attribute.
        """
        model = apps.get_model(app_label, model_name)
        form = model.objects.get(pk=instance_pk)
        admin_class = self.submissions_admin_class_for(form)
        admin = admin_class(self)
        view_class = self.submissions_view_class
        kwargs = {'model_admin': admin}
        return view_class.as_view(**kwargs)(request)
