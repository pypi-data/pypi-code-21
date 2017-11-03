# encoding: utf-8

import tkMessageBox
from Tkconstants import NORMAL, HORIZONTAL, W, EW

import logging_helper; logging = logging_helper.setup_logging()

from pydnserver.gui.nameservers_frame import NameserversConfigWindow
from networkutil.gui.redirect_frame import RedirectConfigWindow
from scenario_frame import ScenariosConfigWindow, AddEditScenarioWindow
from ..intercept.request_intercept import RequestIntercept
from networkutil.device_config import Devices
from networkutil.gui.endpoint_config_launcher_frame import EndpointsLauncherFrame, ROOT_LAYOUT
from uiutil.frame.frame import BaseFrame
from uiutil.frame.label import BaseLabelFrame
from uiutil.helper.layout import nice_grid
from uiutil.window.root import RootWindow
from uiutil.widget.label import Label
from uiutil.widget.button import Button
from uiutil.widget.switchbox import SwitchBox, Switch


THREADED = u'Threaded'
PROFILE = u'Profile'
START_SERVERS = u'Start Servers'
STOP_SERVERS = u'Stop Servers'


class InterceptFrame(BaseFrame):

    def __init__(self,
                 servers=RequestIntercept,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.intercept_server = servers()

        Label(text=u'Endpoints:',
              sticky=W)

        button_width = 20

        self.endpoints_config = EndpointsLauncherFrame(parent=self,
                                                       layout_key=ROOT_LAYOUT,
                                                       grid_row=self.row.next(),
                                                       grid_column=self.column.start())
        self.endpoints_config.grid(sticky=EW,
                                   columnspan=4)

        self.separator(orient=HORIZONTAL,
                       row=self.row.next(),
                       columnspan=4,
                       sticky=EW,
                       padx=5,
                       pady=5)

        Label(text=u'Request intercept:',
              row=self.row.next(),
              sticky=W)

        Button(state=NORMAL,
               text=u'Nameservers Config',
               width=button_width,
               command=self._nameservers_config,
               row=self.row.next(),
               tooltip=u'Configure DNS\n'
                       u'Nameservers')

        Button(state=NORMAL,
               text=u'Configure Redirection',
               width=button_width,
               command=self._redirection_config,
               column=self.column.next(),
               tooltip=u'Configure active\n'
                       u'redirection intercept\n'
                       u'addresses')

        Button(state=NORMAL,
               text=u'Configure Scenarios',
               width=button_width,
               command=self._scenarios_config,
               column=self.column.next(),
               tooltip=u'Modify, add\n'
                       u'or remove\n'
                       u'scenarios')

        Button(state=NORMAL,
               text=u'Edit Active Scenario',
               width=button_width,
               command=self._active_scenario_config,
               column=self.column.next(),
               tooltip=u'Configure settings\n'
                       u'for the current\n'
                       u'active scenario')

        self.blank_row()

        self.column.start()

        self.separator(orient=HORIZONTAL,
                       row=self.row.next(),
                       column=self.column.next(),
                       columnspan=2,
                       sticky=EW,
                       padx=5,
                       pady=5)

        self.switches = SwitchBox(text=THREADED,
                                  row=self.row.next(),
                                  column=self.column.start(),
                                  sticky=W,
                                  sort=False,
                                  switches=(THREADED,
                                            PROFILE),
                                  switch_states={THREADED: Switch.ON,
                                                 PROFILE: Switch.OFF},
                                  switch_parameters = {THREADED: {u"tooltip": u"Check to Run\n"
                                                                              u"intercept with\n"
                                                                              u"threading enabled"},
                                                       PROFILE:  {u"tooltip": u"When profiling\n"
                                                                              u"is enabled, the\n"
                                                                              u"logs will contain\n"
                                                                              u"information to\n"
                                                                              u"help identify\n"
                                                                              u"bottlenecks in\n"
                                                                              u"handlers and\n"
                                                                              u"modifiers"}})

        self.start_stop_button = Button(state=NORMAL,
                                        initial_value=START_SERVERS,
                                        width=button_width,
                                        command=self.start_stop,
                                        column=self.column.next(),
                                        sticky=EW,
                                        columnspan=2,
                                        tooltip=u"")

    def start_stop(self):
        if self.start_stop_button.value == START_SERVERS:
            self.start()
        else:
            self.stop()

    def start(self):

        active_devices = Devices().get_active_items()

        if active_devices:
            self.intercept_server.start(threaded=self.switches.switch_state(THREADED),
                                        profiling=self.switches.switch_state(PROFILE))
            self.start_stop_button.value = STOP_SERVERS
            self.switches.disable()
            self.start_stop_button.tooltip.text = (u'Stop the\n'
                                                   u'running\n'
                                                   u'Intercept\n'
                                                   u'Servers.')
        else:
            tkMessageBox.showinfo(parent=self,
                                  icon=u'info',
                                  title=u"No Active Devices",
                                  message=u"You need at least one active device associated with\n"
                                          u"each network interface under test in order to start\n"
                                          u"the DNS intercept server for that interface.")

    def stop(self):

        self.intercept_server.stop()
        self.start_stop_button.value = START_SERVERS
        self.switches.enable()
        self.start_stop_button.tooltip.text = (u'Start Intercept\n'
                                                u'Servers for\n'
                                                u'active devices')

    def _nameservers_config(self):
        window = NameserversConfigWindow(
                     fixed=True,
                     parent_geometry=(self.parent
                                          .winfo_toplevel()
                                          .winfo_geometry()))

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

    def _redirection_config(self):
        window = RedirectConfigWindow(
                     fixed=True,
                     parent_geometry=(self.parent
                                          .winfo_toplevel()
                                          .winfo_geometry()))

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

    def _scenarios_config(self):
        window = ScenariosConfigWindow(
                     fixed=True,
                     intercept_server=self.intercept_server,
                     parent_geometry=(self.parent
                                          .winfo_toplevel()
                                          .winfo_geometry()))

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        try:
            self.intercept_server.reload_config()
        except AttributeError as e:
            logging.exception(e)

    def _active_scenario_config(self):

        window = AddEditScenarioWindow(
                     edit=True,
                     fixed=True,
                     intercept_server=self.intercept_server,
                     parent_geometry=(self.parent
                                          .winfo_toplevel()
                                          .winfo_geometry()))
        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        try:
            self.intercept_server.reload_config()
        except AttributeError as e:
            logging.exception(e)


class StandaloneInterceptWindow(RootWindow):

    def __init__(self,
                 servers=RequestIntercept,
                 *args,
                 **kwargs):
        self.servers = servers
        super(StandaloneInterceptWindow, self).__init__(*args, **kwargs)

    def _setup(self):
        self.title(u"Intercept")

        self.base = BaseLabelFrame(self._main_frame,
                                   grid_column=0,
                                   grid_row=0)
        self.base.grid(sticky=EW)

        self.intercept = InterceptFrame(parent=self.base,
                                        servers=self.servers,
                                        grid_row=self.base.row.next(),
                                        grid_column=self.base.column.current)
        self.intercept.grid(sticky=EW)
        nice_grid(self.intercept)
