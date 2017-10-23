import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
sys.path.insert(0, os.path.abspath("../../"))
from viewer import Viewer
from collections import OrderedDict
from specdal.spectrum import Spectrum
from specdal.collection import Collection

debug = True

class Session(tk.Tk):
    def __init__(self, parent):
        self.collections = OrderedDict()
        self.mw = parent
        self.viewer = Viewer(parent, collection=None)
        self.create_gui(self.mw)
        self.head = None # name of selected collection
    def create_gui(self, parent):
        h = self.mw.winfo_screenheight()
        w = self.mw.winfo_screenwidth()
        self.mw.geometry("%dx%d+0+0" % (w, h))
        self.read_directory_button = ttk.Button(self.mw, text='Read Directory',
                                                command=lambda:
                                                self.read_collection()).pack()
        self.stitch_button = ttk.Button(self.mw, text='Overlap Stitch',
                                                command=lambda:
                                                self.stitch()).pack()
    def read_collection(self):
        if debug:
            path = '~/data/specdal/aidan_data2/ASD/'
            c = Collection("Test Collection", directory=path)
        else:
            pass
        self.collections[c.name] = c
        self.viewer.collection = c
        self.head = c.name
        self.viewer.update(new_lim=True)
    def read_spectrum(self):
        pass
    def remove_selection(self):
        pass
    def resample(self):
        pass
    def stitch(self):
        if self.head is None:
            return
        # TODO: get params of stitch()
        self.collections[self.head].stitch()
        self.viewer.update()
    def jump_correct(self):
        pass
    def groupby(self):
        pass
    def plot(self):
        pass
    def read_dir(self):
        pass
    def read_files(self):
        pass
    @property
    def collections(self):
        return self._collections
    @collections.setter
    def collections(self, value):
        self._collections = OrderedDict()
    def add_collection(self, collection):
        if isinstance(collection, Collection):
            self._collections[collection.name] = collection
            self.collection_manager.add_collection(collection)

def main():
    root = tk.Tk()
    session = Session(root)
    root.mainloop()

if __name__ == '__main__':
    main()
