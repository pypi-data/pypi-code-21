import tkinter as tk


class ReadonlyText(tk.Text):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self['state'] = 'disabled'

    def output(self, s):
        self['state'] = 'normal'
        self.insert(tk.END, s + '\n')
        self.see(tk.END)
        self['state'] = 'disabled'
