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

from __future__ import division, absolute_import, print_function, unicode_literals

import io
import os
import logging
logger = logging.getLogger(__name__)


try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
except ImportError:
    print("ERR: GTK not available")
    sys.exit(1)
import numpy as np

from ..errors import InputError, VarError
from ..params import save_params, load_params

def manSave(current_exp):
    fcd = Gtk.FileChooserDialog("Save…", None, Gtk.FileChooserAction.SAVE,
                                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
    
    filters = [Gtk.FileFilter()]
    filters[0].set_name("Tab-separated Text (.txt)")
    filters[0].add_pattern("*.txt")

    fcd.set_do_overwrite_confirmation(True)
    for i in filters:
        fcd.add_filter(i)

    response = fcd.run()

    if response == Gtk.ResponseType.OK:
        path = fcd.get_filename().decode("utf-8")
        logger.info("Selected filepath: %s", path)
        filter_selection = fcd.get_filter().get_name().decode("utf-8")

        if filter_selection.endswith("(.txt)"):
            save_text(current_exp, path)
            
        fcd.destroy()

    elif response == Gtk.ResponseType.CANCEL:
        fcd.destroy()

def plot_save_dialog(plots):
    fcd = Gtk.FileChooserDialog("Save Plot…", None,
                                Gtk.FileChooserAction.SAVE,
                                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

    filters = [Gtk.FileFilter()]
    filters[0].set_name("Portable Document Format (.pdf)")
    filters[0].add_pattern("*.pdf")
    filters.append(Gtk.FileFilter())
    filters[1].set_name("Portable Network Graphics (.png)")
    filters[1].add_pattern("*.png")

    fcd.set_do_overwrite_confirmation(True)
    for i in filters:
        fcd.add_filter(i)

    response = fcd.run()

    if response == Gtk.ResponseType.OK:
        path = fcd.get_filename().decode("utf-8")
        logger.info("Selected filepath: %r", path)
        filter_selection = fcd.get_filter().get_name().decode("utf-8")
        
        if filter_selection.endswith("(.pdf)"):
            if not path.endswith(".pdf"):
                path += ".pdf"

        elif filter_selection.endswith("(.png)"):
            if not path.endswith(".png"):
                path += ".png"
        
        save_plot(plots, path)

        fcd.destroy()

    elif response == Gtk.ResponseType.CANCEL:
        fcd.destroy()


def man_param_save(window):
    fcd = Gtk.FileChooserDialog("Save Parameters…",
                                None,
                                Gtk.FileChooserAction.SAVE,
                                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

    filters = [Gtk.FileFilter()]
    filters[0].set_name("Parameter File (.yml)")
    filters[0].add_pattern("*.yml")

    fcd.set_do_overwrite_confirmation(True)
    for i in filters:
        fcd.add_filter(i)

    response = fcd.run()

    if response == Gtk.ResponseType.OK:
        path = fcd.get_filename().decode("utf-8")
        logger.info("Selected filepath: %s", path)

        if not path.endswith(".yml"):
            path += '.yml'

        save_params(window, path)

        fcd.destroy()

    elif response == Gtk.ResponseType.CANCEL:
        fcd.destroy()

def man_param_load(window):
    fcd = Gtk.FileChooserDialog("Load Parameters…",
                                None,
                                Gtk.FileChooserAction.OPEN,
                                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

    filters = [Gtk.FileFilter()]
    filters[0].set_name("Parameter File (.yml)")
    filters[0].add_pattern("*.yml")

    for i in filters:
        fcd.add_filter(i)

    response = fcd.run()

    if response == Gtk.ResponseType.OK:
        path = fcd.get_filename().decode("utf-8")
        logger.info("Selected filepath: %s", path)

        load_params(window, path)

        fcd.destroy()

    elif response == Gtk.ResponseType.CANCEL:
        fcd.destroy()

def autoSave(exp, path, name):
    if name == "":
        name = "file"

    path += '/'
    path += name
     
    save_text(exp, path)

def autoPlot(exp, path, name):
    if name == "":
        name = "file"
        
    path += '/'
    path += name

    if not (path.endswith(".pdf") or path.endswith(".png")):
        path += ".pdf"

    save_plot(exp, path)

def save_text(exp, path):
    savestrings = exp.get_save_strings()
    path = path.rstrip('.txt')
    
    num = ''
    j = 0
    
    for key, text in savestrings.items(): # Test for existing files of any kind
        while os.path.exists("{}{}-{}.txt".format(path, num, key)):
            j += 1
            num = j
            
    save_path = "{}{}".format(path, num)
    
    for key, text in savestrings.items():   
        with open('{}-{}.txt'.format(save_path, key), 'w') as f:
            f.write(text)
        
def save_plot(exp, path):
    """Saves everything in exp.plots to path. Appends a number for duplicates.
    If no file extension or unknown, uses pdf.
    """
    name, _sep, ext = path.rpartition('.')
    if _sep == '':
        name = ext
        ext = 'pdf'
    
    num = ''
    j = 0
    
    for i in exp.plots: # Test for any existing files
        plot_type = '_'.join(i.name.lower().split())
        while os.path.exists("{}{}-{}.{}".format(name, num, plot_type, ext)):
            j += 1
            num = j
    
    for i in exp.plots: # save data
        plot_type = '_'.join(i.name.lower().split())
        i.figure.savefig("{}{}-{}.{}".format(name, num, plot_type, ext))