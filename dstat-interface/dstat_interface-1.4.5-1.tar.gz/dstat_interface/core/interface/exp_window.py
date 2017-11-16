#!/usr/bin/env python
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

import inspect
import logging
from collections import OrderedDict

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GObject
except ImportError:
    print "ERR: GTK not available"
    sys.exit(1)

from . import exp_int

logger = logging.getLogger(__name__)

class Experiments(GObject.Object):
    __gsignals__ = {
        'run_utility': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'done_utility': (GObject.SIGNAL_RUN_FIRST, None, ())
    }
    def __init__(self, builder):
        super(Experiments,self).__init__()
        self.builder = builder
        self.builder.connect_signals(self)
        
        # (experiment index in UI, experiment)
            
        classes = {c.id : c()  # Make class instances
                        for _, c in inspect.getmembers(exp_int, inspect.isclass)
                        if issubclass(c, exp_int.ExpInterface) 
                            and c is not exp_int.ExpInterface
                        }
        
        self.classes = OrderedDict(sorted(classes.items()))
        #fill exp_section
        exp_section = self.builder.get_object('exp_section_box')
        self.containers = {}
        
        for key, c in self.classes.items():
            c.connect('run_utility', self.on_run_utility)
            c.connect('done_utility', self.on_done_utility)
            self.containers[key] = c.get_window()

        for key in self.containers:
            try:
                self.containers[key].get_parent().remove(self.containers[key])
            except AttributeError:
                pass
                
            exp_section.add(self.containers[key])
        
        self.expcombobox = self.builder.get_object('expcombobox')
        self.expcombobox.connect('changed', self.on_expcombobox_changed)
        
        for c in self.classes.values():
            self.expcombobox.append(id=c.id, text=c.name)

    def on_run_utility(self, data=None):
        self.emit('run_utility')
    
    def on_done_utility(self, data=None):
        self.emit('done_utility')

    def on_expcombobox_changed(self, data=None):
        """Change the experiment window when experiment box changed."""
        self.set_exp(self.expcombobox.get_active_id())
    
    def setup_exp(self, parameters):
        exp = self.classes[self.expcombobox.get_active_id()]
        try:
            exp.param_test(parameters)
        except AttributeError:
            logger.warning(
                "Experiment {} has no defined parameter test.".format(
                    exp.name)
                )
        return exp.experiment(parameters)
    
    def hide_exps(self):
        for key in self.containers:
            self.containers[key].hide()
    
    def set_exp(self, selection):
        """Changes parameter tab to selected experiment. Returns True if 
        successful, False if invalid selection received.
        
        Arguments:
        selection -- id string of experiment type
        """
        self.hide_exps()
        self.containers[selection].show()
        self.selected_exp = selection
        
        return True
        
    def get_params(self, experiment):
        return self.classes[experiment].params
    
    def set_params(self, experiment, parameters):
        try:
            self.classes[experiment].params = parameters
        except KeyError as e:
            logger.warning("Tried to load inavlid experiment with id %s", e.args)