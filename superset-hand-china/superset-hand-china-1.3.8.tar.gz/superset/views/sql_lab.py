from flask import redirect, g

from flask_appbuilder import expose
from flask_appbuilder.models.sqla.interface import SQLAInterface

from flask_babel import gettext as __
from flask_babel import lazy_gettext as _

from superset import appbuilder
from superset.models.sql_lab import Query, SavedQuery
from .base import SupersetModelView, BaseSupersetView, DeleteMixin


class QueryView(SupersetModelView):
    list_title = _("List Query")
    show_title = _("Show Query")
    add_title = _("Add Query")
    edit_title = _("Edit Query")
    datamodel = SQLAInterface(Query)
    list_columns = ['user', 'database', 'status', 'start_time', 'end_time']
    # search_columns = [
    #     'results_key', 'tracking_url', 'user', 'status', 'select_sql',
    #     'schema', 'sql', 'sql_editor_id', 'executed_sql', 'database',
    #     'tmp_table_name', 'error_message', 'tab_name', 'client_id',
    #     'changed_on', 'end_result_backend_time', 'progress', 'start_time',
    #     'limit', 'start_running_time', 'rows', 'end_time']
    edit_columns = ['sql', 'database', 'start_time', 'end_time' ]
    search_columns = edit_columns
    label_columns = {
        'results_key': _("Results Key"),
        'tracking_url': _("Tracking Url"),
        'user': _("User"),
        'status': _("Status"),
        'select_sql': _("Select Sql"),
        'schema': _("Schema"),
        'sql': _("Sql"),
        'sql_editor_id': _("Sql Editor Id"),
        'executed_sql': _("Executed Sql"),
        'database': _("Database"),
        'tmp_table_name': _("Tmp Table Name"),
        'error_message': _("Error Message"),
        'tab_name': _("Tab Name"),
        'client_id': _("Client Id"),
        'changed_on': _("Changed On"),
        'end_result_backend_time': _("End Result Backend Time"),
        'progress': _("Progress"),
        'start_time': _("Start Time"),
        'limit': _("Limit"),
        'start_running_time': _("Start Running Time"),
        'rows': _("Rows"),
        'end_time': _("End Time"),
        'ctas': _("Select As Cta"),
        'limit_reached': _("Limit reached"),
        'limit_used': _("Limit Used"),
        'select_as_cta_used': _("Select As Cta Used"),
    }

appbuilder.add_view(
    QueryView,
    "Queries",
    label=__("Queries"),
    category="Manage",
    category_label=__("Manage"),
    icon="fa-search")


class SavedQueryView(SupersetModelView, DeleteMixin):
    datamodel = SQLAInterface(SavedQuery)

    list_title = _('List Saved Query')
    show_title = _('Show Saved Query')
    add_title = _('Add Saved Query')
    edit_title = _('Edit Saved Query')

    list_columns = [
        'label', 'user', 'database', 'schema', 'description',
        'modified', 'pop_tab_link']
    order_columns = ['label', 'description', 'modified']
    show_columns = [
        'id', 'label', 'user', 'database',
        'description', 'sql', 'pop_tab_link']
    search_columns = ('label', 'user', 'database', 'schema', 'changed_on')
    add_columns = ['label', 'database', 'description', 'sql']
    edit_columns = add_columns
    base_order = ('changed_on', 'desc')
    label_columns = {
        'id': _("ID"),
        'schema': _("Schema"),
        'sql': _("Sql"),
        'label': _('Label'),
        'user': _('User'),
        'database': _('Database'),
        'description': _('Description'),
        'modified': _('Modified'),
        'end_time': _('End Time'),
        'pop_tab_link': _('Pop Tab Link'),
        'changed_on': _('Changed on'),
    }

    def pre_add(self, obj):
        obj.user = g.user

    def pre_update(self, obj):
        self.pre_add(obj)


class SavedQueryViewApi(SavedQueryView):
    show_columns = ['label', 'db_id', 'schema', 'description', 'sql']
    add_columns = show_columns
    edit_columns = add_columns
    label_columns = {
        'label': _("Label"),
        # 'db_id': _("DataBases Id"),
        'schema': _("Schema"),
        'description': _("Description"),
        'sql': _("Sql"),
    }

appbuilder.add_view_no_menu(SavedQueryViewApi)
appbuilder.add_view_no_menu(SavedQueryView)

appbuilder.add_link(
    __('Saved Queries'),
    href='/sqllab/my_queries/',
    icon="fa-save",
    category='SQL Lab')


class SqlLab(BaseSupersetView):
    """The base views for Superset!"""
    @expose("/my_queries/")
    def my_queries(self):
        """Assigns a list of found users to the given role."""
        return redirect(
            '/savedqueryview/list/?_flt_0_user={}'.format(g.user.id))


appbuilder.add_view_no_menu(SqlLab)
