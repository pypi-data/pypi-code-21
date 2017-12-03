from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy
from django.conf.urls import url
from abc import ABCMeta, abstractmethod
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages


# Creates all views needed for a model
class JcmsCrud(object):
    __metaclass__ = ABCMeta

    # Model for all views
    @property
    @abstractmethod
    def model(self):
        pass

    # All fields that should be can be set when creating or editing
    @property
    @abstractmethod
    def create_edit_list(self):
        pass

    # All fields that need to be shown in the list page
    @property
    @abstractmethod
    def list_fields(self):
        pass

    # Gets all url objects for to create the urls
    def get_crud_urls(self):
        return [
            url(r'^' + self().get_model_name() + 's/$',
                self().list_view(),
                name=self().get_model_name() + 'List'),
            url(r'^' + self().get_model_name() + '/(?P<pk>[0-9]+)/$',
                self().detail_view(),
                name=self().get_model_name() + 'Detail'),
            url(r'^' + self().get_model_name() + '/create/$',
                self().create_view(),
                name=self().get_model_name() + 'Create'),
            url(r'^' + self().get_model_name() + '/(?P<pk>[0-9]+)/delete/$',
                self().delete_view(),
                name=self().get_model_name() + 'Delete'),
            url(r'^' + self().get_model_name() + '/(?P<pk>[0-9]+)/edit/$',
                self().edit_view(),
                name=self().get_model_name() + 'Edit'),
        ]

    # Mixin with permission and login
    class PermissionMixin(LoginRequiredMixin, PermissionRequiredMixin):
        pass

    # List view with permission create_model_name
    def list_view(self):
        class ObjectList(self.PermissionMixin, ListView):
            fields = self.list_fields
            model = self.model
            template_name = 'jcms-admin/crud/list.html'
            permission_required = 'jcms.create_' + self.get_model_name()

        return ObjectList.as_view()

    # Detail view with permission create_model_name
    def detail_view(self):
        class ObjectDetail(self.PermissionMixin, DetailView):
            model = self.model
            template_name = 'jcms-admin/crud/detail.html'
            permission_required = 'jcms.create_' + self.get_model_name()

        return ObjectDetail.as_view()

    # Create view with permission create_model_name
    def create_view(self):
        class ObjectCreate(self.PermissionMixin, SuccessMessageMixin, CreateView):
            model = self.model
            fields = self.create_edit_list
            template_name = 'jcms-admin/crud/edit_or_create.html'
            success_url = reverse_lazy('jcms:' + self.get_model_name() + 'List')
            permission_required = 'jcms.create_' + self.get_model_name()
            success_message = 'Successfully created ' + self.get_model_name()

        return ObjectCreate.as_view()

    # Edit view with permission change_model_name
    def edit_view(self):
        class ObjectEdit(self.PermissionMixin, SuccessMessageMixin, UpdateView):
            model = self.model
            fields = self.create_edit_list
            template_name = 'jcms-admin/crud/edit_or_create.html'
            success_url = reverse_lazy('jcms:' + self.get_model_name() + 'List')
            permission_required = 'jcms.change_' + self.get_model_name()
            success_message = 'Successfully edited ' + self.get_model_name()

        return ObjectEdit.as_view()

    # Delete view with permission delete_model_name
    def delete_view(self):
        class ObjectDelete(self.PermissionMixin, DeleteView):
            model = self.model
            permission_required = 'jcms.delete_' + self.get_model_name()
            success_url = reverse_lazy('jcms:' + self.get_model_name() + 'List')
            success_message = 'Successfully deleted ' + self.get_model_name()

            def delete(self, request, *args, **kwargs):
                messages.success(self.request, self.success_message)
                return super(ObjectDelete, self).delete(request, *args, **kwargs)
        return ObjectDelete.as_view()

    # Gets name of the model
    def get_model_name(self):
        return self.model.__name__.lower()
