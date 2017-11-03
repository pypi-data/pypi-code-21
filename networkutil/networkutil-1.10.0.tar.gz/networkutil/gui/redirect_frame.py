# encoding: utf-8

import tkMessageBox
import logging_helper
from Tkconstants import NORMAL, DISABLED, HORIZONTAL, E, W, S, EW, NSEW
from Tkinter import StringVar, BooleanVar
from collections import OrderedDict
from uiutil.widget.tooltip import ToolTip
from networkutil.endpoint_config import Endpoints, EnvAndAPIs
from uiutil.frame.frame import BaseFrame
from uiutil.helper.layout import nice_grid
from uiutil.window.child import ChildWindow
from tableutil import Table
from fdutil.string_tools import make_multi_line_list
from pydnserver import dns_lookup
from configurationutil import Configuration

logging = logging_helper.setup_logging()

PASS_THROUGH = u'Pass Through'


class AddEditRedirectFrame(BaseFrame):

    def __init__(self,
                 selected_record=None,
                 edit=False,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.edit = edit

        self.cfg = Configuration()

        self.endpoints = Endpoints()
        self.env_and_apis = EnvAndAPIs()

        try:
            key = u'{cfg}.{h}'.format(cfg=dns_lookup.DNS_LOOKUP_CFG,
                                      h=selected_record)

            self.selected_host_config = self.cfg[key]

        except LookupError:
            self.selected_host = None
            self.selected_host_config = None

        else:
            self.selected_host = selected_record

        label_column = self.column.start()
        entry_column = self.column.next()
        self.columnconfigure(entry_column, weight=1)
        cancel_column = self.column.next()
        save_column = self.column.next()

        self.label(text=u'Hostname:',
                   row=self.row.next(),
                   column=label_column,
                   sticky=W)

        existing_endpoints = dns_lookup.get_redirection_config().keys()

        host_endpoints = set([endpoint.hostname
                              for endpoint in self.endpoints
                              if endpoint.hostname not in (u'Body.all',
                                                           u'URI.all',
                                                           u'Header.all')])

        host_endpoints = list(host_endpoints.difference(existing_endpoints))
        host_endpoints = sorted(host_endpoints)

        self.__host_var = StringVar(self.parent)
        self.__host_var.set(self.selected_host if self.edit else host_endpoints[0])
        self.__host = self.combobox(textvariable=self.__host_var,
                                    values=host_endpoints,
                                    state=DISABLED if self.edit else NORMAL,
                                    row=self.row.current,
                                    column=entry_column,
                                    sticky=EW,
                                    columnspan=3)

        self.rowconfigure(self.row.current,
                          weight=1)

        self.label(text=u'Redirect:',
                   row=self.row.next(),
                   column=label_column,
                   sticky=W)

        self.__redirect_var = StringVar(self.parent)
        self.__redirect_var.set(self.selected_host_config[dns_lookup.REDIRECT_HOSTNAME]
                                if self.edit else u'')
        self.__redirect = self.combobox(textvariable=self.__redirect_var,
                                        row=self.row.current,
                                        column=entry_column,
                                        sticky=EW,
                                        columnspan=3)

        self.populate_redirect_list()

        self.label(text=u'Redirect Address:',
                   row=self.row.next(),
                   column=label_column,
                   sticky=W)

        self.__address_var = StringVar(self.parent)
        self.__address_var.set(self.selected_host_config[dns_lookup.REDIRECT_ADDRESS]
                               if self.edit else u'default')

        self.__address = self.entry(textvariable=self.__address_var,
                                    row=self.row.current,
                                    column=entry_column,
                                    sticky=EW,
                                    columnspan=3)

        self.__address_tooltip = ToolTip(self.__address, u'')

        self.rowconfigure(self.row.current,
                          weight=1)

        self.separator(orient=HORIZONTAL,
                       row=self.row.next(),
                       column=label_column,
                       columnspan=4,
                       sticky=EW,
                       padx=5,
                       pady=5)

        self.__cancel_button = self.button(state=NORMAL,
                                           text=u'Cancel',
                                           width=15,
                                           command=self.__cancel,
                                           row=self.row.next(),
                                           column=cancel_column)

        self.__save_button = self.button(state=NORMAL,
                                         text=u'Save',
                                         width=15,
                                         command=self.__save,
                                         row=self.row.current,
                                         column=save_column)

    def __save(self):
        redirect_name = self.__host_var.get()
        redirect_hostname = self.__redirect_var.get()

        try:
            if redirect_hostname == PASS_THROUGH or redirect_hostname.strip() == u'':
                redirect_hostname = None

            else:
                # TODO: What are we achieving here??
                apis = self.endpoints.get_apis_for_host(redirect_name)
                matched_endpoint = None
                for api in apis:
                    try:
                        matched_endpoint = self.endpoints.get_endpoint_for_api_and_environment(
                                                api=api,
                                                environment=redirect_hostname)
                        break  # We got one!
                    except ValueError:
                        pass

                # TODO: Figure this out???
                redirect_hostname = matched_endpoint.hostname

            values = {dns_lookup.REDIRECT_HOSTNAME: redirect_hostname,
                      dns_lookup.REDIRECT_ADDRESS: self.__address_var.get(),
                      dns_lookup.ACTIVE: self.selected_host_config[dns_lookup.ACTIVE] if self.edit else False}

            key = u'{cfg}.{h}'.format(cfg=dns_lookup.DNS_LOOKUP_CFG,
                                      h=redirect_name)

            self.cfg[key] = values

        except Exception as err:
            logging.error(u'Cannot save record, Does the endpoint exist?')
            logging.exception(err)

        self.parent.master.exit()

    def __cancel(self):
        self.parent.master.exit()

    def populate_redirect_list(self):
        host = self.__host_var.get()

        try:
            host_apis = self.endpoints.get_apis_for_host(host)
            redirect_environments = set()
            for host_api in host_apis:
                redirect_environments.update(
                    set(self.env_and_apis.get_environments_for_api(host_api)))
            redirect_environments.add(PASS_THROUGH)

            pass_through_environment = self.endpoints.get_environment_for_host(host)

            redirect_environments.remove(pass_through_environment)

            redirect_environments = sorted(list(redirect_environments))
            try:
                redirect_hostname = self.selected_host_config[dns_lookup.REDIRECT_HOSTNAME]
                endpoint = [endpoint
                            for endpoint in self.endpoints
                            if endpoint.hostname == redirect_hostname
                            ][0]

                if endpoint.hostname == host:
                    env = PASS_THROUGH
                else:
                    env = endpoint.environment
            except (IndexError, TypeError):
                env = PASS_THROUGH

            self.__redirect.config(values=redirect_environments)
            self.__redirect.current(redirect_environments.index(env))
            self.__redirect_var.set(env)

        except KeyError:
            logging.error(u'Cannot load redirect list, Invalid hostname!')


class AddEditRedirectWindow(ChildWindow):

    def __init__(self,
                 selected_record=None,
                 edit=False,
                 *args,
                 **kwargs):

        self.selected_record = selected_record
        self.edit = edit

        super(AddEditRedirectWindow, self).__init__(*args, **kwargs)

    def _setup(self):
        self.title(u"Add/Edit Redirection Config Record")

        self.config = AddEditRedirectFrame(parent=self._main_frame,
                                           selected_record=self.selected_record,
                                           edit=self.edit)
        self.config.grid(sticky=NSEW)


class RedirectConfigFrame(BaseFrame):

    def __init__(self,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.__selected_record = StringVar(self.parent)

        self.cfg = Configuration()

        self.endpoints = Endpoints()

        self.dns_radio_list = {}
        self.dns_active_var_list = {}
        self.dns_active_list = {}

        self.columnconfigure(self.column.start(), weight=1)

        self.REDIRECT_ROW = self.row.next()
        self.rowconfigure(self.REDIRECT_ROW, weight=1)
        self.BUTTON_ROW = self.row.next()

        self.__build_record_frame()
        self.__build_button_frame()

    def __build_record_frame(self):

        self.record_frame = BaseFrame(self)
        self.record_frame.grid(row=self.REDIRECT_ROW,
                               column=self.column.current,
                               sticky=NSEW)

        left_col = self.record_frame.column.start()
        middle_col = self.record_frame.column.next()
        right_middle_col = self.record_frame.column.next()
        right_col = self.record_frame.column.next()

        headers_row = self.record_frame.row.next()

        tooltip_text = u"Examples:\n"

        example = OrderedDict()
        example[u'Hostname'] = u'ethpersonalised.recs.sky.com'
        example[u'Redirect'] = u'TS15'
        example[u'Redirect Address'] = u'<Null>'

        tooltip_text += Table.init_from_tree(example,
                                             title=make_multi_line_list(u"requests for "
                                                                        u"'ethpersonalised.recs.sky.com' "
                                                                        u"are diverted to an endpoint "
                                                                        u"defined for TS15"),
                                             table_format=Table.LIGHT_TABLE_FORMAT).text() + u'\n'

        example = OrderedDict()
        example[u'Hostname'] = u'ethpersonalised.recs.sky.com'
        example[u'Redirect'] = u'Pass Through (Null value)'
        example[u'Redirect Address'] = u'default'

        tooltip_text += Table.init_from_tree(example,
                                             title=make_multi_line_list(u"requests for 'ethpersonalised.recs.sky.com'"
                                                                        u" are diverted to the intercept server"
                                                                        u" ('default'), which allows modification of"
                                                                        u" intercepted messages. The endpoint is not"
                                                                        u" changed."),
                                             table_format=Table.LIGHT_TABLE_FORMAT).text() + u'\n'

        example = OrderedDict()
        example[u'Hostname'] = u'ethpersonalised.recs.sky.com'
        example[u'Redirect'] = u'TS15'
        example[u'Redirect Address'] = u'default'

        tooltip_text += Table.init_from_tree(example,
                                             title=make_multi_line_list(u"requests for 'ethpersonalised.recs.sky.com'"
                                                                        u" are diverted to the intercept server"
                                                                        u" ('default'), which allows modification of"
                                                                        u" intercepted messages. The endpoint used by"
                                                                        u" the intercept server to make the request is"
                                                                        u" changed to the endpoint for TS15."),
                                             table_format=Table.LIGHT_TABLE_FORMAT).text()

        self.record_frame.label(text=u'Hostname',
                                row=headers_row,
                                column=left_col,
                                tooltip=tooltip_text,
                                sticky=W)

        self.record_frame.label(text=u'Redirect',
                                row=headers_row,
                                column=middle_col,
                                tooltip=tooltip_text,
                                sticky=W)

        self.record_frame.label(text=u'Redirect Address',
                                row=headers_row,
                                column=right_middle_col,
                                tooltip=tooltip_text,
                                sticky=W)

        self.record_frame.label(text=u'Active',
                                row=headers_row,
                                column=right_col,
                                tooltip=tooltip_text,
                                sticky=W)

        self.record_frame.separator(orient=HORIZONTAL,
                                    row=self.record_frame.row.next(),
                                    column=left_col,
                                    columnspan=5,
                                    sticky=EW,
                                    padx=5,
                                    pady=5)

        for host, host_config in iter(dns_lookup.get_redirection_config().items()):

            redirect_row = self.record_frame.row.next()

            if not self.__selected_record.get():
                self.__selected_record.set(host)

            self.dns_radio_list[host] = self.record_frame.radiobutton(text=host,
                                                                      variable=self.__selected_record,
                                                                      value=host,
                                                                      row=redirect_row,
                                                                      column=left_col,
                                                                      sticky=W)

            try:
                text = self.endpoints.get_environment_for_host(host_config[u'redirect_hostname'])

            except LookupError:
                text = PASS_THROUGH

            self.record_frame.label(text=text,
                                    row=redirect_row,
                                    column=middle_col,
                                    sticky=W)

            self.record_frame.label(text=host_config[u'address'],
                                    row=redirect_row,
                                    column=right_middle_col,
                                    sticky=W)

            self.dns_active_var_list[host] = BooleanVar(self.parent)
            self.dns_active_var_list[host].set(host_config[u'active'])

            self.dns_active_list[host] = self.record_frame.checkbutton(
                variable=self.dns_active_var_list[host],
                command=(lambda host=host,
                         flag=self.dns_active_var_list[host]:
                         self.__update_active(host=host,
                                              flag=flag)),
                row=redirect_row,
                column=right_col
            )

        self.record_frame.separator(orient=HORIZONTAL,
                                    row=self.record_frame.row.next(),
                                    column=left_col,
                                    columnspan=5,
                                    sticky=EW,
                                    padx=5,
                                    pady=5)

        nice_grid(self.record_frame)

    def __build_button_frame(self):

        button_width = 15

        self.button_frame = BaseFrame(self)
        self.button_frame.grid(row=self.BUTTON_ROW,
                               column=self.column.current,
                               sticky=(E, W, S))

        button_row = self.button_frame.row.start()

        left_col = self.button_frame.column.start()
        middle_col = self.button_frame.column.next()
        right_middle_col = self.button_frame.column.next()
        right_col = self.button_frame.column.next()

        self.button(frame=self.button_frame,
                    name=u'_close_button',
                    text=u'Close',
                    width=button_width,
                    command=self.parent.master.destroy,
                    row=button_row,
                    column=left_col)

        self.button(frame=self.button_frame,
                    name=u'_delete_record_button',
                    text=u'Delete Record',
                    width=button_width,
                    command=self.__delete_record,
                    row=button_row,
                    column=middle_col,
                    tooltip=u'Delete\nselected\nrecord')

        self.button(frame=self.button_frame,
                    name=u'_add_record_button',
                    text=u'Add Record',
                    width=button_width,
                    command=self.__add_record,
                    row=button_row,
                    column=right_middle_col,
                    tooltip=u'Add record\nto dns list')

        self.button(frame=self.button_frame,
                    name=u'_edit_record_button',
                    text=u'Edit Record',
                    width=button_width,
                    command=self.__edit_record,
                    row=button_row,
                    column=right_col,
                    tooltip=u'Edit\nselected\nrecord')

        nice_grid(self.button_frame)

    def __add_record(self):
        window = AddEditRedirectWindow(fixed=True,
                                       parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()))

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self.record_frame.destroy()
        self.__build_record_frame()

        self.parent.master.update_geometry()

    def __edit_record(self):
        window = AddEditRedirectWindow(selected_record=self.__selected_record.get(),
                                       edit=True,
                                       fixed=True,
                                       parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()))

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self.record_frame.destroy()
        self.__build_record_frame()

        self.parent.master.update_geometry()

    def __delete_record(self):
        result = tkMessageBox.askquestion(title=u"Delete Record",
                                          message=u"Are you sure you "
                                                  u"want to delete {r}?".format(r=self.__selected_record.get()),
                                          icon=u'warning',
                                          parent=self)

        if result == u'yes':
            key = u'{c}.{h}'.format(c=dns_lookup.DNS_LOOKUP_CFG,
                                    h=self.__selected_record.get())

            del self.cfg[key]

            self.record_frame.destroy()
            self.__build_record_frame()

            self.parent.master.update_geometry()

    def __update_active(self, host, flag):
        key = u'{c}.{h}.{active}'.format(c=dns_lookup.DNS_LOOKUP_CFG,
                                         h=host,
                                         active=dns_lookup.ACTIVE)

        self.cfg[key] = flag.get()


class RedirectConfigWindow(ChildWindow):

    def __init__(self,
                 *args,
                 **kwargs):

        super(RedirectConfigWindow, self).__init__(*args, **kwargs)

    def _setup(self):
        self.title(u"Redirection configuration")

        self.config = RedirectConfigFrame(parent=self._main_frame)
        self.config.grid(sticky=NSEW)
