import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.abspath("../.."))
from specdal.spectrum import Spectrum
from specdal.collection import Collection
from specdal import readers as r
from collections import OrderedDict
import re

class CollectionManager(tk.Frame):
    def __init__(self, parent, data=None):
        """ Displays collection and its children in Treeview """
        tk.Frame.__init__(self, parent)
        self.collections = OrderedDict()
        self.create_gui(parent)

        if isinstance(data, Collection):
            self.add_collection(data)

        # for testing
        # tk.Button(self, text="test", command=lambda : print(self.get_selection())).pack()

    def add_collection(self, collection):
        """ Add a collection to the manager """
        
        if not isinstance(collection, Collection):
            return
        if collection.name in self.collections:
            return
        self.collections[collection.name] = collection
        self.treeview.insert("", tk.END, collection.name, text=collection.name,
                             values=(len(collection.spectrums), ))
        self.update(collection.name)

    def remove_collection(self, coll_name=None):
        """ Remove an entire collection """
        if coll_name in self.treeview.get_children():
            self.treeview.delete(coll_name)
    
    def update(self, coll_name):
        """ Update the children of a collection 
        
        Notes
        -----
        Must be called when collection is modified in order to update 
        the treeview.
        
        i.e. when a spectrum has been added or removed from a collection
        """
        if coll_name not in self.collections:
            return
        collection = self.collections[coll_name]
        # delete all spectrums in collection
        self.treeview.delete(*self.treeview.get_children(coll_name))
        # add all spectrums in collection
        for spectrum in collection.spectrums:
            key = "{" + coll_name + "} " + spectrum.name
            self.treeview.insert(coll_name, tk.END,
                                 key, # unique within coll
                                 text=spectrum.name,
                                 values=("", False))

    def get_selection(self):
        """ 
        Get the selected collection and spectra.

        Returns
        -------
        list of tuples (collection.name, spectrum.name)

        Notes
        -----
        id of collection: collection.name
        id of spectrum: {collection.name} spectrum.name
        """
        result = []
        selections = self.treeview.selection()
        for selection in selections:
            match = re.match("\{(.*)\} (.*)", selection)
            if match:
                # spectrum
                collection, spectrum = match.groups()
            else:
                # collection
                collection, spectrum = selection, None
            result.append((collection, spectrum))
        return result
    
    def create_gui(self, parent):
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.treeview = ttk.Treeview(self, columns=("one", "two"),
                                     yscrollcommand=self.scrollbar.set)
        self.treeview.column("#0", width=200)
        self.treeview.column("one", width=50, anchor=tk.CENTER)
        self.treeview.column("two", width=50, anchor=tk.CENTER)
        self.treeview.heading("#0", text="Name")
        self.treeview.heading("one", text="count")
        self.treeview.heading("two", text="mask")
        
        self.scrollbar.config(command=self.treeview.yview)
        
        self.treeview.pack(fill=tk.BOTH, expand=1)
        self.pack(fill=tk.BOTH, expand=1)


def main():
    c = Collection("Test Collection")
    c.read("../../data/asd/")
    root = tk.Tk()
    CollectionManager(root, c)
    root.mainloop()


if __name__ == "__main__":
    main()
