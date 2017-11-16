#!/usr/bin/env python
# -*- coding: utf-8 -*-
#     DStat Interface - An interface for the open hardware DStat potentiostat
#     Copyright (C) 2014  Michael D. M. Dryden -
#     Wheeler Microfluidics Laboratory <http://microfluidics.utoronto.ca>
#
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" GUI Interface for Wheeler Lab DStat """

from __future__ import division, absolute_import, print_function, unicode_literals

import sys
import os
import platform
import multiprocessing
import uuid
from collections import OrderedDict
from datetime import datetime
import logging
from pkg_resources import parse_version

from serial import SerialException
import zmq

from dstat_interface.core.utils.version import getVersion
from dstat_interface.core.experiments import idle, pot
from dstat_interface.core import params, analysis, dstat
from dstat_interface.core.dstat import boards
from dstat_interface.core.interface import (exp_window, adc_pot, plot_ui, data_view,
                           save, hw_info)
from dstat_interface.core.errors import InputError
from dstat_interface.core.plugin import DstatPlugin, get_hub_uri

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GObject
except ImportError:
    print("ERR: GTK not available")
    sys.exit(1)

mod_dir = os.path.dirname(os.path.abspath(__file__))
conf_path = os.path.join(os.path.expanduser("~"), '.dstat-interface')

# if __name__ == "__parents_main__":  # Only runs for forking emulation on win
# sys.path.append(mod_dir)

# Setup Logging
logger = logging.getLogger(__name__)
core_logger = logging.getLogger("dstat_interface.core")
loggers = [logger, core_logger]

log_handler = logging.StreamHandler()
log_formatter = logging.Formatter(
                    fmt='%(asctime)s %(levelname)s: [%(name)s] %(message)s',
                    datefmt='%H:%M:%S'
                )
log_handler.setFormatter(log_formatter)

for log in loggers:
    log.setLevel(level=logging.INFO)
    log.addHandler(log_handler)


class Main(object):
    """Main program """
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(
            os.path.join(mod_dir, 'core/interface/dstatinterface.glade'))
        self.builder.connect_signals(self)
        self.cell = Gtk.CellRendererText()

        # Create instance of interface components
        self.statusbar = self.builder.get_object('statusbar')
        self.ocp_disp = self.builder.get_object('ocp_disp')
        self.window = self.builder.get_object('window1')
        self.aboutdialog = self.builder.get_object('aboutdialog1')
        self.stopbutton = self.builder.get_object('pot_stop')
        self.startbutton = self.builder.get_object('pot_start')
        self.startbutton.set_sensitive(False)
        self.adc_pot = adc_pot.adc_pot()

        self.error_context_id = self.statusbar.get_context_id("error")
        self.message_context_id = self.statusbar.get_context_id("message")

        self.exp_window = exp_window.Experiments(self.builder)
        self.exp_window.connect('run_utility', self.stop_ocp)
        self.exp_window.connect('done_utility', self.start_ocp)
        
        self.analysis_opt_window = analysis.AnalysisOptions(self.builder)

        # Setup Autosave
        self.autosave_checkbox = self.builder.get_object('autosave_checkbutton')
        self.autosavedir_button = self.builder.get_object('autosavedir_button')
        self.autosavename = self.builder.get_object('autosavename')

        # Setup Plots
        self.plot_notebook = self.builder.get_object('plot_notebook')
        self.main_notebook = self.builder.get_object('main_notebook')
        self.data_view = data_view.DataPage(self.main_notebook)
        self.info_page = data_view.InfoPage(self.main_notebook)

        # fill adc_pot_box
        self.adc_pot_box = self.builder.get_object('gain_adc_box')
        self.adc_pot_container = self.adc_pot.builder.get_object('vbox1')
        self.adc_pot_container.reparent(self.adc_pot_box)

        # fill serial
        self.serial_connect = self.builder.get_object('serial_connect')
        self.serial_pmt_connect = self.builder.get_object('pmt_mode')
        self.serial_disconnect = self.builder.get_object('serial_disconnect')
        self.serial_disconnect.set_sensitive(False)
        self.serial_combobox = self.builder.get_object('serial_combobox')
        self.serial_combobox.pack_start(self.cell, True)
        self.serial_combobox.add_attribute(self.cell, 'text', 0)
        self.serial_liststore = self.builder.get_object('serial_liststore')
        self.serial_devices = dstat.comm.SerialDevices()

        for i in self.serial_devices.ports:
            self.serial_liststore.append([i])

        self.serial_combobox.set_active(0)

        self.spinner = self.builder.get_object('spinner')

        self.mainwindow = self.builder.get_object('window1')
        
        self.menu_dstat_info = self.builder.get_object('menu_dstat_info')
        self.menu_dstat_info.set_sensitive(False)
        self.dstat_info_window = hw_info.InfoDialog(
             parent=self.mainwindow,
             connect=self.menu_dstat_info
        )
        self.menu_dstat_fw = self.builder.get_object('menu_dstat_fw')
        self.menu_dstat_fw.set_sensitive(False)
        self.dstat_fw_window = dstat.dfu.FWDialog(
            parent=self.mainwindow,
            connect=self.menu_dstat_fw,
            stop_callback=self.stop_ocp,
            disconnect_callback=self.on_serial_disconnect_clicked
        )
        self.menu_dstat_reset = self.builder.get_object('menu_dstat_reset')
        self.menu_dstat_reset.set_sensitive(False)
        self.menu_dstat_reset_window = hw_info.ResetDialog(
            parent=self.mainwindow,
            connect=self.menu_dstat_reset,
            stop_callback=self.stop_ocp,
            disconnect_callback=self.on_serial_disconnect_clicked
        )
        
        # Set Version Strings
        try:
            ver = getVersion()
        except ValueError:
            ver = "1.x"
            logger.warning("Could not fetch version number")
        self.mainwindow.set_title(" ".join(("DStat Interface", ver)))
        self.aboutdialog.set_version(ver)

        self.mainwindow.show_all()
        self.exp_window.hide_exps()
        
        self.expnumber = 0

        self.connected = False
        self.pmt_mode = False
        
        self.menu_dropbot_connect = self.builder.get_object(
                                                         'menu_dropbot_connect')
        self.menu_dropbot_disconnect = self.builder.get_object(
                                                      'menu_dropbot_disconnect')
        self.dropbot_enabled = False
        self.dropbot_triggered = False
        
        self.metadata = None # Should only be added to by plugin interface

        self.params_loaded = False
        # Disable 0MQ plugin API by default.
        self.plugin = None
        self.plugin_timeout_id = None
        # UUID for active experiment.
        self.active_experiment_id = None
        # UUIDs for completed experiments.
        self.completed_experiment_ids = OrderedDict()

    def on_window1_destroy(self, object, data=None):
        """ Quit when main window closed."""
        self.quit()

    def on_gtk_quit_activate(self, menuitem, data=None):
        """Quit when Quit selected from menu."""
        self.quit()

    def quit(self):
        """Disconnect and save parameters on quit."""
        
        try:
            params.save_params(self, os.path.join(conf_path, 'last_params.yml'))
            self.on_serial_disconnect_clicked()
        except KeyError:
            pass
            
        mainloop.quit()

    def on_gtk_about_activate(self, menuitem, data=None):
        """Display the about window."""
        self.aboutdialog.run()  # waits for user to click close
        self.aboutdialog.hide()

    def on_menu_analysis_options_activate(self, menuitem, data=None):
        self.analysis_opt_window.show()

    def on_serial_refresh_clicked(self, data=None):
        """Refresh list of serial devices."""
        try:
            self.serial_devices.refresh()
            self.serial_liststore.clear()
        except ValueError:
            logger.warning("No DStats found")

        for i in self.serial_devices.ports:
            self.serial_liststore.append([i])

    def on_serial_connect_clicked(self, widget):
        """Connect and retrieve DStat version."""
        if widget is self.serial_pmt_connect:
            self.pmt_mode = True
            self.adc_pot.ui['short_true'].set_active(True)
            self.adc_pot.ui['short_true'].set_sensitive(False)
            
        try:
            self.serial_connect.set_sensitive(False)
            self.serial_pmt_connect.set_sensitive(False)
            dstat.comm.version_check(
                self.serial_liststore.get_value(
                    self.serial_combobox.get_active_iter(), 0
                )
            )

            dstat.state.board_instance = boards.find_board(
                dstat.state.dstat_version)()

            self.statusbar.remove_all(self.error_context_id)

            self.adc_pot.set_version()
            self.statusbar.push(
                self.message_context_id,
                "DStat version: {}".format(
                    dstat.state.dstat_version.base_version)
            )

            dstat.comm.read_settings()

            try:
                if dstat.state.settings['dac_units_true'][1] != b'1':
                    dstat.state.settings['dac_units_true'][1] = b'1'
                    dstat.comm.write_settings()
            except KeyError:
                logger.warning("Connected DStat does not support sending DAC units.")
                dialog = Gtk.MessageDialog(
                    self.window, 0, Gtk.MessageType.WARNING,
                    Gtk.ButtonsType.OK, "Connected DStat does not support sending DAC units." +
                                        "Update firmware or set potentials will be incorrect!")

                dialog.run()
                dialog.destroy()

            self.start_ocp()
            self.connected = True
            self.serial_disconnect.set_sensitive(True)

        except:
            self.serial_connect.set_sensitive(True)
            self.serial_pmt_connect.set_sensitive(True)
            self.adc_pot.ui['short_true'].set_sensitive(True)
            raise

        if self.params_loaded == False:
            try:
                try: 
                    os.makedirs(conf_path)
                except OSError:
                    if not os.path.isdir(conf_path):
                        raise
                params.load_params(self,
                    os.path.join(conf_path, 'last_params.yml')
                )
            except IOError:
                logger.info("No previous parameters found.")
        
    def on_serial_disconnect_clicked(self, data=None):
        """Disconnect from DStat."""
        if self.connected == False:
            return

        try:
            if self.ocp_is_running:
                self.stop_ocp()
            else:
                self.on_pot_stop_clicked()
            dstat.state.ser.disconnect()

        except AttributeError as err:
            logger.warning("AttributeError: %s", err)
            pass
        
        if self.pmt_mode is True:
            self.adc_pot.ui['short_true'].set_sensitive(True)
        
        self.pmt_mode = False
        self.connected = False
        self.serial_connect.set_sensitive(True)
        self.serial_pmt_connect.set_sensitive(True)
        self.serial_disconnect.set_sensitive(False)
        self.startbutton.set_sensitive(False)
        self.stopbutton.set_sensitive(False)
        self.menu_dstat_info.set_sensitive(False)
        self.menu_dstat_fw.set_sensitive(False)
        self.menu_dstat_reset.set_sensitive(False)
        self.adc_pot.ui['short_true'].set_sensitive(True)
        
        dstat.state.reset()

    def start_ocp(self, data=None):
        """Start OCP measurements."""
        if dstat.state.dstat_version >= parse_version('1.2'):
            # Flush data pipe
            dstat.state.ser.flush_data()

            if self.pmt_mode is True:
                logger.info("Start PMT idle mode")
                dstat.state.ser.start_exp(idle.PMTIdle())
                self.ocp_is_running = True
                self.ocp_proc = (GObject.timeout_add(250, self.ocp_running_proc)
                                 ,
                                 )

            else:
                logger.info("Start OCP")
                dstat.state.ser.start_exp(idle.OCPExp())

                self.ocp_proc = (GObject.timeout_add(300, self.ocp_running_data),
                                 GObject.timeout_add(250, self.ocp_running_proc)
                                )
                self.ocp_is_running = False
                
            GObject.timeout_add(100, self.ocp_assert)  # Check if getting data

        else:
            logger.info("OCP measurements not supported on v1.1 boards.")
        return

    def stop_ocp(self, data=None):
        """Stop OCP measurements."""

        if dstat.state.dstat_version >= parse_version('1.2'):
            if self.pmt_mode == True:
                logger.info("Stop PMT idle mode")
            else:
                logger.info("Stop OCP")
            dstat.state.ser.send_ctrl('a')
            
            for i in self.ocp_proc:
                GObject.source_remove(i)
            while self.ocp_running_proc():
                pass
            self.ocp_disp.set_text("")
            self.ocp_is_running = False
            self.startbutton.set_sensitive(True)
            self.menu_dstat_info.set_sensitive(True)
            self.menu_dstat_fw.set_sensitive(True)
            self.menu_dstat_reset.set_sensitive(True)
        else:
            logger.error("OCP measurements not supported on v1.1 boards.")
        return

    def ocp_assert(self):
        if self.ocp_is_running:
            self.startbutton.set_sensitive(True)
            self.menu_dstat_info.set_sensitive(True)
            self.menu_dstat_fw.set_sensitive(True)
            self.menu_dstat_reset.set_sensitive(True)
            return False
        else:
            return True

    def ocp_running_data(self):
        """Receive OCP value from experiment process and update ocp_disp field

        Returns:
        True -- when experiment is continuing to keep function in GTK's queue.
        False -- when experiment process signals EOFError or IOError to remove
            function from GTK's queue.
        """

        try:
            incoming = dstat.state.ser.get_data()
            while incoming is not None:
                if isinstance(incoming, basestring): # test if incoming is str
                    self.on_serial_disconnect_clicked()
                    return False
                
                try:
                    data = "".join(["OCP: ",
                                    "{0:.3f}".format(incoming),
                                    " V"])
                    self.ocp_disp.set_text(data)
                    self.ocp_is_running = True
                except ValueError:
                    pass

                incoming = dstat.state.ser.get_data()

            return True

        except EOFError:
            return False
        except IOError:
            return False

    def ocp_running_proc(self):
        """Handles signals on proc_pipe_p for OCP.

        Returns:
        True -- when experiment is continuing to keep function in GTK's queue.
        False -- when experiment process signals EOFError or IOError to remove
            function from GTK's queue.
        """

        try:
            proc_buffer = dstat.state.ser.get_proc()
            while proc_buffer is not None:
                logger.debug("ocp_running_proc: %s", proc_buffer)
                if proc_buffer in ["DONE", "SERIAL_ERROR", "ABORT"]:
                    if proc_buffer == "SERIAL_ERROR":
                        self.on_serial_disconnect_clicked()

                    dstat.state.ser.flush_data()
                    return False
                proc_buffer = dstat.state.ser.get_proc()
            return True

        except EOFError:
            return False
        except IOError:
            return False

    def on_pot_start_clicked(self, data=None):
        try:
            self.run_active_experiment()
        except (ValueError, KeyError, InputError, SerialException,
                AssertionError):
            # Ignore expected exceptions when triggering experiment from UI.
            pass

    def run_active_experiment(self, param_override=None, metadata=None):
        """Run currently visible experiment."""
        # Assign current experiment a unique identifier.
        experiment_id = uuid.uuid4()
        self.active_experiment_id = experiment_id
        logger.info("Current measurement id: %s", experiment_id.hex)
        
        self.metadata = metadata
        
        if self.metadata is not None:
            logger.info("Loading external metadata")       

        def exceptions():
            """ Cleans up after errors """
            self.spinner.stop()
            self.startbutton.set_sensitive(True)
            self.stopbutton.set_sensitive(False)
            self.start_ocp()

        self.stop_ocp()
        self.statusbar.remove_all(self.error_context_id)

        dstat.state.ser.flush_data()

        parameters = {}
        parameters['metadata'] = self.metadata

        # Make sure these are defined
        parameters['sync_true'] = False
        parameters['shutter_true'] = False
        try:
            if param_override is not None:
                params.set_params(self, param_override)
            
            parameters.update(params.get_params(self))
            
            self.line = 0
            self.lastline = 0
            self.lastdataline = 0

            self.spinner.start()
            self.startbutton.set_sensitive(False)
            self.stopbutton.set_sensitive(True)
            self.statusbar.remove_all(self.error_context_id)
            
            self.current_exp = self.exp_window.setup_exp(parameters)
            
            plot_ui.replace_notebook_exp(
                self.plot_notebook, self.current_exp, self.window
                )

            for plot in self.current_exp.plots:
                plot.changetype(self.current_exp)
            
            self.data_view.clear_exps()
            self.info_page.clear()
            
            dstat.state.ser.start_exp(self.current_exp)

            # Flush data pipe
            dstat.state.ser.flush_data()

            self.plot_proc = GObject.timeout_add(200,
                                                self.experiment_running_plot)
            self.experiment_proc = (
                    GObject.idle_add(self.experiment_running_data),
                    GObject.idle_add(self.experiment_running_proc)
                    )
                    
            return experiment_id

        except ValueError as i:
            logger.info("ValueError: %s",i)
            self.statusbar.push(self.error_context_id,
                                "Experiment parameters must be integers.")
            exceptions()
            raise

        except KeyError as i:
            import traceback
            traceback.print_exc()
            logger.info("KeyError: %s", i)
            self.statusbar.push(self.error_context_id,
                                "Experiment parameters must be integers.")
            exceptions()
            raise

        except InputError as err:
            logger.info("InputError: %s", err)
            self.statusbar.push(self.error_context_id, err.msg)
            exceptions()
            raise

        except SerialException as err:
            logger.info("SerialException: %s", err)
            self.statusbar.push(self.error_context_id,
                                "Could not establish serial connection.")
            exceptions()
            raise

        except AssertionError as err:
            logger.info("AssertionError: %s", err)
            self.statusbar.push(self.error_context_id, str(err))
            exceptions()
            raise

    def experiment_running_data(self):
        """Receive data from experiment process and add to
        current_exp.data['data].
        Run in GTK main loop.

        Returns:
        True -- when experiment is continuing to keep function in GTK's queue.
        False -- when experiment process signals EOFError or IOError to remove
            function from GTK's queue.
        """
        try:
            incoming = dstat.state.ser.get_data()
            while incoming is not None:
                try:
                    self.line, data = incoming
                    if self.line > self.lastdataline:
                        newline = True
                        try:
                            logger.info("running scan_process()")
                            self.current_exp.scan_process(self.lastdataline)
                        except AttributeError:
                            pass
                        self.lastdataline = self.line
                    else:
                        newline = False
                    self.current_exp.store_data(incoming, newline)
                    
                    if newline:
                        self.experiment_running_plot()
                except TypeError:
                    pass
                incoming = dstat.state.ser.get_data()
            return True

        except EOFError as err:
            logger.error(err)
            self.experiment_done()
            return False
        except IOError as err:
            logger.error(err)
            self.experiment_done()
            return False

    def experiment_running_proc(self):
        """Receive proc signals from experiment process.
        Run in GTK main loop.

        Returns:
        True -- when experiment is continuing to keep function in GTK's queue.
        False -- when experiment process signals EOFError or IOError to remove
            function from GTK's queue.
        """
        try:
            proc_buffer = dstat.state.ser.get_proc()
            if proc_buffer is not None:
                if proc_buffer in ["DONE", "SERIAL_ERROR", "ABORT"]:
                    self.experiment_done()
                    if proc_buffer == "SERIAL_ERROR":
                        self.on_serial_disconnect_clicked()

                else:
                    logger.warning("Unrecognized experiment return code: %s",
                                   proc_buffer)
                return False
            return True

        except EOFError as err:
            logger.warning("EOFError: %s", err)
            self.experiment_done()
            return False
        except IOError as err:
            logger.warning("IOError: %s", err)
            self.experiment_done()
            return False

    def experiment_running_plot(self, force_refresh=False):
        """Plot all data in current_exp.data.
        Run in GTK main loop. Always returns True so must be manually
        removed from GTK's queue.
        """
        for plot in self.current_exp.plots:
            if (plot.scan_refresh and self.line > self.lastline):
                while self.line > self.lastline:
                    # make sure all of last line is added
                    plot.updateline(self.current_exp, self.lastline)
                    self.lastline += 1
                plot.updateline(self.current_exp, self.line)
                plot.redraw()
            else:
                while self.line > self.lastline:
                    # make sure all of last line is added
                    plot.updateline(self.current_exp, self.lastline)
                    self.lastline += 1
                plot.updateline(self.current_exp, self.line)
            
            if plot.continuous_refresh is True or force_refresh is True:
                plot.redraw()
        return True

    def experiment_done(self):
        """Clean up after data acquisition is complete. Update plot and
        copy data to raw data tab. Saves data if autosave enabled.
        """
        try:
            self.current_exp.scan_process(self.lastdataline)
            self.current_exp.experiment_done()
            GObject.source_remove(self.experiment_proc[0])
            GObject.source_remove(self.plot_proc)  # stop automatic plot update
            self.experiment_running_plot(force_refresh=True)
            

            # # Shutter stuff
            # if (self.current_exp.parameters['shutter_true'] and
            #     self.current_exp.parameters['sync_true']):
            #     self.ft_plot.updateline(self.current_exp, 0)
            #     self.ft_plot.redraw()
            #
            #     line_buffer = []
            #
            #     for scan in self.current_exp.data['ft']:
            #         for dimension in scan:
            #             for i in range(len(dimension)):
            #                 try:
            #                     line_buffer[i] += "%s     " % dimension[i]
            #                 except IndexError:
            #                     line_buffer.append("")
            #                     line_buffer[i] += "%s     " % dimension[i]
            #
            #     for i in line_buffer:
            #         self.databuffer.insert_at_cursor("%s\n" % i)

            # Run Analysis
            analysis.do_analysis(self.current_exp)
            
            self.current_exp.experiment_done()
            
            # Write DStat commands
            self.info_page.set_text(self.current_exp.get_info_text())
            
            try:
                self.statusbar.push(
                    self.message_context_id,
                    "Integral: %s A" % self.current_exp.analysis['FT Integral'][0][1]
                )
            except KeyError:
                pass

            # Data Output
            analysis_buffer = []

            if self.current_exp.analysis != {}:
                analysis_buffer.append("# ANALYSIS")
                for key, value in self.current_exp.analysis.iteritems():
                    analysis_buffer.append("#  %s:" % key)
                    for scan in value:
                        number, result = scan
                        analysis_buffer.append(
                            "#    Scan %s -- %s" % (number, result)
                            )

            for i in analysis_buffer:
                self.info_page.add_line(i)

            self.data_view.add_exp(self.current_exp)

            # Autosaving
            if self.autosave_checkbox.get_active():
                save.autoSave(self.current_exp,
                              self.autosavedir_button.get_filename().decode('utf-8'),
                              self.autosavename.get_text()
                              )

                save.autoPlot(self.current_exp,
                              self.autosavedir_button.get_filename().decode('utf-8'),
                              self.autosavename.get_text()
                              )
        
        # uDrop
        # UI stuff
        finally:
            self.metadata = None # Reset metadata
            
            self.spinner.stop()
            self.stopbutton.set_sensitive(False)

            self.start_ocp()
            self.completed_experiment_ids[self.active_experiment_id] =\
                datetime.utcnow()

            # Temporary fix for weird drawing bug on windows Gtk+3
            if platform.system() == 'Windows':
                position = self.window.get_position()
                self.window.hide()
                self.window.show()
                self.window.move(*position)

    def on_pot_stop_clicked(self, data=None):
        """Stop current experiment. Signals experiment process to stop."""
        try:
            dstat.state.ser.stop_exp()

        except AttributeError:
            pass
        except:
            logger.warning(sys.exc_info())

    def on_file_save_exp_activate(self, menuitem, data=None):
        """Activate dialogue to save current experiment data. """
        try:
            save.manSave(self.current_exp)
        except AttributeError:
            logger.warning("Tried to save with no experiment run")

    def on_file_save_plot_activate(self, menuitem, data=None):
        """Activate dialogue to save current plot."""
        try:
            save.plot_save_dialog(self.current_exp)
        except AttributeError:
            logger.warning("Tried to save with no experiment run")

    def on_file_save_params_activate(self, menuitem, data=None):
        """Activate dialogue to save current experiment parameters. """
        save.man_param_save(self)

    def on_file_load_params_activate(self, menuitem, data=None):
        """Activate dialogue to load experiment parameters from file. """
        save.man_param_load(self)

    def on_menu_dropbot_connect_activate(self, menuitem, data=None):
        """Listen for remote control connection from µDrop."""

        # Prompt user for 0MQ plugin hub URI.
        zmq_plugin_hub_uri = get_hub_uri(parent=self.window)

        self.dropbot_enabled = True
        self.menu_dropbot_connect.set_sensitive(False)
        self.menu_dropbot_disconnect.set_sensitive(True)
        self.statusbar.push(self.message_context_id,
                            "Waiting for µDrop to connect…")
        self.enable_plugin(zmq_plugin_hub_uri)

    def on_menu_dropbot_disconnect_activate(self, menuitem=None, data=None):
        """Disconnect µDrop connection and stop listening."""
        self.cleanup_plugin()
        self.dropbot_enabled = False
        self.menu_dropbot_connect.set_sensitive(True)
        self.menu_dropbot_disconnect.set_sensitive(False)
        self.statusbar.push(self.message_context_id, "µDrop disconnected.")

    def enable_plugin(self, hub_uri):
        '''
        Connect to 0MQ plugin hub to expose public D-Stat API.

        Args
        ----

            hub_uri (str) : URI for 0MQ plugin hub.
        '''
        self.cleanup_plugin()
        # Initialize 0MQ hub plugin and subscribe to hub messages.
        self.plugin = DstatPlugin(self, 'dstat-interface', hub_uri,
                                  subscribe_options={zmq.SUBSCRIBE: ''})
        # Initialize sockets.
        self.plugin.reset()

        # Periodically process outstanding message received on plugin sockets.
        self.plugin_timeout_id = Gtk.timeout_add(500,
                                                 self.plugin.check_sockets)

    def cleanup_plugin(self):
        if self.plugin_timeout_id is not None:
            GObject.source_remove(self.plugin_timeout_id)
        if self.plugin is not None:
            self.plugin = None


if __name__ == "__main__":
    multiprocessing.freeze_support()
    GObject.threads_init()
    MAIN = Main()
    mainloop = GObject.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        logger.info('Ctrl+C hit, quitting')
        MAIN.quit()
