

import tkinter as tk
import tkinter.font

from tkinter import scrolledtext

class TextList(tk.Frame):

    def __init__(self, container):

        tk.Frame.__init__(self, container)
        self.container = container

        # Frame does not support ScrollBar but Canvas does.
        # So, embed frame in canvas to use ScrollBar.
        self.canvas = canvas = tk.Canvas(master=self, borderwidth=0, background="#d4d4d4")
        self.table = Cells(master=self)
        #self.cells.grid(sticky='news')

        self.vsb = vsb = tk.Scrollbar(self, orient="vertical", command=self.on_vsb_scroll)
        self.hsb = hsb = tk.Scrollbar(self, orient="horizontal", command=self.on_hsb_scroll)

        canvas.config(yscrollcommand=vsb.set)
        canvas.config(xscrollcommand=hsb.set)

        canvas.grid(column=1, row=1, sticky='nsew')
        vsb.grid(column=2, row=1, sticky='ns')
        hsb.grid(column=1, row=2, sticky='ew')

        self.cells_id = canvas.create_window((0, 0), window=self.table, anchor="nw", tags="self.cells")


        self.rowconfigure(1, weight=1)      # row header
        self.columnconfigure(1, weight=1)   # col header
        # self.rowconfigure(1, weight=1)
        # self.columnconfigure(1, weight=1)

        self.canvas.bind("<MouseWheel>", self.on_mouse_scroll)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.table.bind("<Configure>", self.on_frame_configure)

    def set_value(self, row, col, value):
        self.table.set_value(row, col, value)

    def on_vsb_scroll(self, *args):
        self.canvas.yview(*args)

    def on_hsb_scroll(self, *args):
        self.canvas.xview(*args)

    def on_mouse_scroll(self, event):
        if event.delta > 0:
            self.on_vsb_scroll("scroll", "-3", "units")
        else:
            self.on_vsb_scroll("scroll", "3", "units")

    def on_canvas_configure(self, event):
        if event.width > self.table.min_width:
            self.canvas.itemconfig(self.cells_id, width=event.width-4)

    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def insert_row(self, pos, text=None):

        # if not self.cells.count_row():  # No cell exists.
        #     self.col_header.insert_col(0)
        self.table.insert_row(pos, text)


    def delete_row(self, pos, count):
        self.table.delete_col(pos, count)

    def clear_all(self):
        self.table.clear_all()

    def append_row(self, text=None):
        row_count = self.count_row()
        self.insert_row(self.count_row(), text)

    def resize_row(self, count):
        curr_count = self.count_row()

        if count > curr_count:
            self.insert_row(curr_count, count - curr_count)
        elif count < curr_count:
            self.delete_row(count, curr_count - count)
        else:   # count == curr_count
            pass    # Do nothing.

    def count_row(self):
        # If self.cells has at least one cell,
        # Should be the same as self.cells.count_row().
        return self.table.count_row()


class Cells(tk.Frame):

    def __init__(self, master, cnf={}, **kw):

        tk.Frame.__init__(self, master, cnf={}, **kw)

        self.text_font = tk.font.Font(family="consolas", size=10)
        # self.row_headers = {}
        # self.col_headers = {}
        self.master = master
        self.cells = []  # list of rows of nodes
        self.configure(background="#d4d4d4")  # Boader color: slightly darker than default
        #self.configure(background="#d4d4d4")  # Boader color: slightly darker than default
        self._row_count = 0
        #self.columnconfigure(0, weight=1)

        #self.bind('<MouseWheel>', master.on_mouse_scroll)
        self.min_width = 500


    def count_row(self):
        """Count rows or nodes"""
        #return len(self.cells)
        return self._row_count

    def set_value(self, row, col, value):
        """Set value to a cell"""

        if row < self.count_row()  \
            and col < self.count_col():

            cell = self.cells[row][col]
            last_state = cell.cget("state")
            cell.config(state="normal")
            cell.delete(0, tk.END)
            cell.insert(0, value)
            cell.config(state=last_state)

    def insert_row(self, pos, text=None):
        """Insert empty rows or nodes"""

        pos = max(min(pos, self._row_count), 0)

        self.cells.insert(pos, self._new_cell(text))

        self._row_count += 1

        self.redraw()

    def _new_cell(self, text=None):

        height = len(text.split('\n'))
        cell = PyText(self,
                        #readonlybackground="#ffffff",
                       height=height,
                        relief="flat")

        cell.grid(padx=(0, 1), pady=(0, 1), sticky='ew')
        self.columnconfigure(0, weight=1)

        if text:
            cell.insert(1.0, text)
            # cell.config(text=text)

        cell.config(font=self.text_font)
        cell.config(state=tk.DISABLED)

        #cell.bind("<MouseWheel>", self.master.on_mouse_scroll)

        #cell.pack(fill=tk.BOTH, expand='yes')

        return cell

    def redraw(self):
        pass
        # for row in range(self._row_count):
        #         self.cells[row].grid(row=row)

    def delete_row(self, pos, count=1):

        if count <= 0:
            return

        row_count = self.count_row()

        if not pos < row_count:
                return  # Do nothing.

        count = min(count, row_count - pos)

        for i in range(count):
            deleted_row = self.cells[pos]
            self.cells.pop(pos)

            for j in range(len(deleted_row)):
                deleted_row[j].grid_remove()
                deleted_row[j].destroy()

        self._row_count -= pos

        self.redraw()


    def clear_cell(self, row, col):
        self.cells[row].delete(0, tk.END)

    def clear_all(self):
        for row in range(self.count_row()):
            for col in range(self.count_col()):
                self.clear_cells(row, col)


from idlesub.ColorDelegator import ColorDelegator
from idlesub.Percolator import Percolator

class PyText(tk.Text):
    """Text widget with Python syntax highlighting"""

    def __init__(self, master=None, cnf={}, **kw):

        tk.Text.__init__(self, master, cnf, **kw)


### From here: WIS added for Syntax Highlighting

        self.per = per = Percolator(self)
        # initialized below in self.ResetColorizer
        self.color = None
        self.reset_colorizer()

    def _rmcolorizer(self):
        if not self.color:
            return
        self.color.removecolors()
        self.per.removefilter(self.color)
        self.color = None

    def _addcolorizer(self):
        """ Override of the OutputWindow._addcolorizer minus the following parts:
        * ``if self.ispythonsource(self.io.filename)`` check
        * ``self.per.removefilter(self.undo)`` for UndoDelegator
        """
        if self.color:
            return
        # can add more colorizers here...
        self.color = ColorDelegator()
        if self.color:
            self.per.insertfilter(self.color)

    def reset_colorizer(self):
        """Update the color theme"""
        # Called from self.filename_change_hook and from configDialog.py
        self._rmcolorizer()
        self._addcolorizer()
        # theme = idleConf.GetOption('main', 'Theme', 'name')
        # normal_colors = idleConf.GetHighlight(theme, 'normal')
        # cursor_color = idleConf.GetHighlight(theme, 'cursor', fgBg='fg')
        # select_colors = idleConf.GetHighlight(theme, 'hilite')
        #
        # self.content_text.config(
        #     foreground=normal_colors['foreground'],
        #     background=normal_colors['background'],
        #     insertbackground=cursor_color,
        #     selectforeground=select_colors['foreground'],
        #     selectbackground=select_colors['background'],
        # )

### End here: WIS added for Syntax Highlighting




test_script = \
"""def fibo2(x):
    if x == 0 or x == 1:
        return x
    else:
        return fibo2[x - 1] + fibo2[x - 2]"""


if __name__ == "__main__":

    root = tk.Tk()
    text_list = TextList(root)
    #text_list.insert_row(0, text=test_script)
    for i in range(9):
        text_list.insert_row(i, text=test_script)
    text_list.pack(fill=tk.BOTH, expand=1)
    #text_list.grid(sticky='ew')
    #text_list.columnconfigure(1, weight=1)

    tk.mainloop()

