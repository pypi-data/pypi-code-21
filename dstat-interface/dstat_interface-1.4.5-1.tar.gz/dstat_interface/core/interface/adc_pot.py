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
import os.path
from pkg_resources import parse_version

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
except ImportError:
    print "ERR: GTK not available"
    sys.exit(1)

from ..errors import InputError, VarError
from ..dstat import state

mod_dir = os.path.dirname(os.path.abspath(__file__))

class adc_pot(object):
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(mod_dir,'adc_pot.glade'))
        self.builder.connect_signals(self)
        self.cell = Gtk.CellRendererText()
        
        ui_keys = ['buffer_true',
                   'short_true',
                   'pga_index',
                   'srate_index',
                   'gain_index'
                   ]
        ui_cont = map(self.builder.get_object, ['buffer_checkbutton',
                                                'short_checkbutton',
                                                'pga_combobox',
                                                'srate_combobox',
                                                'gain_combobox'
                                                ]
                      )
        self.ui = dict(zip(ui_keys, ui_cont))
        
        #initialize comboboxes
        self.ui['pga_index'].pack_start(self.cell, True)
        self.ui['pga_index'].add_attribute(self.cell, 'text', 1)
        self.ui['pga_index'].set_active(1)

        self.ui['srate_index'].pack_start(self.cell, True)
        self.ui['srate_index'].add_attribute(self.cell, 'text', 1)
        self.ui['srate_index'].set_active(7)
        
        self.gain_liststore = self.builder.get_object('gain_liststore')
        self.ui['gain_index'].pack_start(self.cell, True)
        self.ui['gain_index'].add_attribute(self.cell, 'text', 1)
        # self.ui['gain_index'].set_active(2)
        
        self._params = {}
    
    @property
    def params(self):
        """Dict of parameters."""
        try:
            self._get_params()
        except InputError as e:
            raise e
        finally:
            return self._params
    
    def _get_params(self):
        """Updates self._params from UI."""
        for i in self.ui:
            self._params[i] = self.ui[i].get_active()
        
        srate_model = self.ui['srate_index'].get_model()
        self._params['adc_rate'] = srate_model[self._params['srate_index']][2]
        srate = srate_model[self._params['srate_index']][1]
        
        if srate.endswith("kHz"):
            sample_rate = float(srate.rstrip(" kHz"))*1000
        else:
            sample_rate = float(srate.rstrip(" Hz"))
        
        self._params['adc_rate_hz'] = sample_rate
        
        pga_model = self.ui['pga_index'].get_model()
        self._params['adc_pga'] = pga_model[self._params['pga_index']][2]
        
        gain_model = self.ui['gain_index'].get_model()
        self._params['gain'] = gain_model[self._params['gain_index']][2]
        if self._params['gain_index'] not in range(len(gain_model)):
            raise InputError(self._params['gain_index'],
                             "Select a potentiostat gain.")
        
    @params.setter
    def params(self, params):
        if self._params is {}:
            self._params = dict.fromkeys(self.ui.keys())
        
        for i in self._params:
            if i in params:
                self._params[i] = params[i]
        self._set_params()

    def _set_params(self):
        """Updates UI with new parameters."""
        for i in self.ui:
            self.ui[i].set_active(self._params[i])
            
    def set_version(self, boost=None):
        """ Sets menus for DStat version. """
        try:
            if self.version == state.board_instance:
                return
        except AttributeError:
            pass
            
        self.version = state.board_instance
        
        self.gain_liststore.clear()
        
        for n, i in enumerate(self.version.gain_labels):
            self.gain_liststore.append((n, i, str(n)))
            
        self.ui['gain_index'].set_active(self.version.gain_default_index)