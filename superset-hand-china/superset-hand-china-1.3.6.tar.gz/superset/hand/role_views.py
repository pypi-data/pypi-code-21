
from flask_appbuilder.security.views import (
    RoleModelView, UserDBModelView, UserStatsChartView, PermissionViewModelView)
from flask_appbuilder import ModelView, CompactCRUDMixin, BaseView, expose
from flask_appbuilder.actions import action
from flask import redirect
from flask_babel import gettext as __
from flask_babel import lazy_gettext as _


class DeleteMixin(object):
    @action(
        "muldelete", __("Delete"), __("Delete all Really?"), "fa-trash", single=False)
    def muldelete(self, items):
        self.datamodel.delete_all(items)
        self.update_redirect()
        return redirect(self.get_redirect())
    

class MyRoleViewModel(RoleModelView, DeleteMixin):
    list_template = "hand/role/role_list.html"


class MyUserDBViewModel(UserDBModelView):
    search_columns = [
        'first_name', 'last_name', 'username', 'email', 'active', 'roles',
        'created_by', 'changed', 'last_login','login_count', 'fail_login_count',
        'created', 'created_on', 'changed_by', 'changed_on']
    description_columns = {
        'first_name': _('Write the user first name or names'),
        'last_name': _('Write the user last name'),
        'username': _(
            'Username valid for authentication on DB or LDAP, unused for OID auth'
            ),
        'password': _(
            'Please use a good password policy, this application does not check this for you'
            ),
        'active': _('It\'s not a good policy to remove a user, just make it inactive'),
        'email': _('The user\'s email, this will also be used for OID auth'),
        'roles': _(
            'The user role on the application, this will associate with a list of permissions'
            ),
        'conf_password': _('Please rewrite the user\'s password to confirm')
        }
    label_columns = {
        'first_name': _('First Name'),
        'last_name': _('Last Name'),
        'username': _('User Name'),
        'email': _('EMail'),
        'roles': _('Role'),
        'last_login': _('Last login'),
        'login_count': _('Login count'),
        'fail_login_count': _('Failed login count'),
        'created_on': _('Created on'),
        'created_by': _('Created by'),
        'changed_on': _('Changed on'),
        'changed_by': _('Changed by'),
        'changed': _("Changed"),
        'created': _("Created"),
        'active': _('Is Active?'),
        'password': _('Password'),
    }


class MyUserStatsChartView(UserStatsChartView):
    search_columns = [
        'login_count', 'fail_login_count', 'password', 'username', 'created_by',
        'last_name', 'changed', 'last_login', 'roles', 'created',
        'email', 'created_on', 'changed_by', 'changed_on', 'first_name']

    definitions = [
        {
            'label': _('Login Count'),
            'group': 'username',
            'series': ['login_count']
        },
        {
            'label': _('Failed Login Count'),
            'group': 'username',
            'series': ['fail_login_count']
        }

    ]
    label_columns = {
        'password': _('Password'),
        'first_name': _('First Name'),
        'last_name': _('Last Name'),
        'username': _('User Name'),
        'email': _('EMail'),
        'roles': _('Role'),
        'last_login': _('Last login'),
        'login_count': _('Login count'),
        'fail_login_count': _('Failed login count'),
        'created_on': _('Created on'),
        'created_by': _('Created by'),
        'changed_on': _('Changed on'),
        'changed_by': _('Changed by'),
        'changed': _("Changed"),
        'created': _("Created"),
        'active': _('Is Active?'),
    }
    

class MyPermissionViewViewModel(PermissionViewModelView):
    search_columns = ['permission', 'view_menu', 'role']
    label_columns = {
        'role': _('Role'),
        'permission': _('Permission'), 
        'view_menu': _('View/Menu'),
    }



