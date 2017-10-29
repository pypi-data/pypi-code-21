import tkinter as tk

__all__ = ["TableFrame"]

from modelx.tkgui.CellCanvas import CellCanvas


def sortby(tree, col, descending):
    """Sort tree contents when a column is clicked on."""
    # grab values to sort
    data = [(tree.set(child, col), child) for child in tree.get_children('')]

    # reorder data
    data.sort(reverse=descending)
    for indx, item in enumerate(data):
        tree.move(item[1], '', indx)

    # switch the heading so that it will sort in the opposite direction
    tree.heading(col,
                 command=lambda col=col: sortby(tree, col, int(not descending)))


def autoscroll(sbar, first, last):
    """Hide and show scrollbar as needed."""
    first, last = float(first), float(last)
    if first <= 0 and last >= 1:
        sbar.grid_remove()
    else:
        sbar.grid()
    sbar.set(first, last)


class TableFrame(tk.Frame):
    """A spreadsheet-like widget having a row header, a column header and a cells.

    """

    def __init__(self, container):


        tk.Frame.__init__(self, container)
        self.container = container

        # Frame does not support ScrollBar but Canvas does.
        # So, embed frame in canvas to use ScrollBar.
        self.canvas = canvas = CellCanvas(master=self, borderwidth=0, background="#d4d4d4")
        self.rh_canvas = rh_canvas = CellCanvas(master=self, borderwidth=0,
                                                width=50, background="#d4d4d4")
        self.ch_canvas = ch_canvas = CellCanvas(master=self, borderwidth=0,
                                                height=20, background="#d4d4d4")

        self.row_header = row_header = rh_canvas
        self.col_header = col_header = ch_canvas
        self.table = canvas

        row_header.insert_col(0)
        col_header.insert_row(0)

        self.vsb = vsb = tk.Scrollbar(self, orient="vertical", command=self.on_vsb_scroll)
        self.hsb = hsb = tk.Scrollbar(self, orient="horizontal", command=self.on_hsb_scroll)

        canvas.config(yscrollcommand=vsb.set)
        canvas.config(xscrollcommand=hsb.set)

        rh_canvas.config(yscrollcommand=vsb.set)
        ch_canvas.config(xscrollcommand=hsb.set)

        rh_canvas.grid(column=0, row=1, sticky='nsew')
        ch_canvas.grid(column=1, row=0, sticky='nsew')

        canvas.grid(column=1, row=1, sticky='nsew')
        vsb.grid(column=2, row=1, sticky='ns')
        hsb.grid(column=1, row=2, sticky='ew')

        # canvas.create_window((0, 0), window=self.table, anchor="nw", tags="self.cells")
        # rh_canvas.create_window((0, 0), window=self.row_header, anchor="nw", tags="self.cells")
        # ch_canvas.create_window((0, 0), window=self.col_header, anchor="nw", tags="self.cells")

        self.rowconfigure(0, weight=0)      # row header
        self.columnconfigure(0, weight=0)   # col header
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        # self.canvas.bind("<Configure>", self.on_frame_configure)
        # self.canvas.bind("<MouseWheel>", self.on_mouse_scroll)
        #self.cells.bind("<MouseWheel>", self.on_mouse_scroll)

        # self.auto_extend = auto_extend

        # self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # self.rh_canvas.configure(scrollregion=self.rh_canvas.bbox("all"))
        # self.ch_canvas.configure(scrollregion=self.ch_canvas.bbox("all"))
        # self.table.lower(self.rh_canvas)
        # self.table.lower(self.ch_canvas)

    def set_value(self, row, col, value):
        self.table.set_value(row, col, value)

    def set_row_header(self, row, value):
        self.row_header.set_value(row, 0, value)

    def set_col_header(self, col, value):
        self.col_header.set_value(0, col, value)

    def on_vsb_scroll(self, *args):
        self.canvas.yview(*args)
        self.rh_canvas.yview(*args)

    def on_hsb_scroll(self, *args):
        self.canvas.xview(*args)
        self.ch_canvas.xview(*args)

    def on_mouse_scroll(self, event):
        if event.delta > 0:
            self.on_vsb_scroll("scroll", "-3", "units")
        else:
            self.on_vsb_scroll("scroll", "3", "units")

    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""

        # print('width:' + str(self.canvas.winfo_width()) + ',' + str(self.canvas.winfo_reqwidth()))

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.rh_canvas.configure(scrollregion=self.rh_canvas.bbox("all"))
        self.ch_canvas.configure(scrollregion=self.ch_canvas.bbox("all"))
        self.table.lower(self.rh_canvas)
        self.table.lower(self.ch_canvas)

    # def _create_first_cell(self):
    #
    #     if self.cells.count_row():
    #         return
    #     else:
    #         self.row_header.insert_row(0)
    #         self.col_header.insert_col(0)
    #         self.cells.insert_row(0)

    def insert_row(self, pos, count=1, text=None):

        if count <= 0:
            return

        # if not self.cells.count_row():  # No cell exists.
        #     self.col_header.insert_col(0)

        self.row_header.insert_row(pos, count)
        self.table.insert_row(pos, count)
        if not text:
            for row in range(pos, pos + count):
                for col in range(self.table.col_count):
                    self.table.set_value(row, col, text)


    def insert_col(self, pos, count=1, text=None):

        if count <= 0:
            return

        # if not self.cells.count_col():  # No cell exists.
        #     self.row_header.insert_row(0)

        self.col_header.insert_col(pos, count)
        self.table.insert_col(pos, count)
        if not text:
            for col in range(pos, pos + count):
                for row in range(self.table.row_count):
                    self.table.set_value(row, col, text)

    def delete_row(self, pos, count):
        self.row_header.delete_row(pos, count)
        self.table.delete_col(pos, count)

    def delete_col(self, pos, count):
        self.col_header.delete_col(pos, count)
        self.table.delete_col(pos, count)

    def resize_row(self, count):
        curr_count = self.count_row()

        if count > curr_count:
            self.insert_row(curr_count, count - curr_count)
        elif count < curr_count:
            self.delete_row(count, curr_count - count)
        else:   # count == curr_count
            pass    # Do nothing.

    def resize_col(self, count):
        curr_count = self.count_col()

        if count > curr_count:
            self.insert_col(curr_count, count - curr_count)
        elif count < curr_count:
            self.delete_col(count, curr_count - count)
        else:   # count == curr_count
            pass    # Do nothing.

    def count_row(self):
        # If self.cells has at least one cell,
        # Should be the same as self.cells.count_row().
        return self.row_header.row_count

    def count_col(self):
        return self.col_header.col_count


class Cells(tk.Frame):

    def __init__(self, master):

        tk.Frame.__init__(self, master)
        # self.row_headers = {}
        # self.col_headers = {}
        self.master = master
        self.cells = []  # list of rows of nodes
        self.configure(background="#d4d4d4")  # Boader color: slightly darker than default
        self._row_count = 0
        self._col_count = 0

        self.bind('<MouseWheel>', master.on_mouse_scroll)

    def count_row(self):
        """Count rows or nodes"""
        #return len(self.cells)
        return self._row_count

    def count_col(self):
        """Count rows or nodes"""
        # if self.cells:
        #     return len(self.cells[0])
        # else:
        #     return 0
        return self._col_count

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

    def insert_row(self, pos, count=1, text=None):
        """Insert empty rows or nodes"""
        if count < 1:
            raise ValueError

        # if not self.cells:
        #     col_count = 1
        # else:
        #     col_count = len(self.cells[0])

        pos = max(min(pos, self._row_count), 0)

        for i in range(count):
            col = []    # col is empty if self._col_count == 0
            for j in range(self._col_count):
                col.append(self._new_cell(text))

            self.cells.insert(pos, col)

        self._row_count += count

        self.redraw()

    def insert_col(self, pos, count=1, text=None):
        """Insert empty rows or nodes"""
        if count < 1:
            raise ValueError

        pos = max(min(pos, self._col_count), 0)

        if self._row_count == 0:
            pass
        else:
            for row in self.cells:
                for _ in range(count):
                    row.insert(pos, self._new_cell(text))

        self._col_count += count

        # if not self.cells:
        #     row_count = 1
        #     pos = 0
        #     new_row = []
        #     for col in range(count):
        #         new_row.insert(pos, self._new_cell(text))
        #
        #     self.cells.insert(pos, new_row)
        #
        # else:
        #     row_count = len(self.cells)
        #     pos = max(min(len(self.cells[0]), pos), 0)
        #
        #     for row in self.cells:
        #         for col in range(count):
        #             row.insert(pos, self._new_cell(text))

        self.redraw()


    def _new_cell(self, text=None):
        cell = tk.Entry(self,
                        readonlybackground="#ffffff",
                        width=5,
                        relief="flat")

        cell.grid(padx=(0, 1), pady=(0, 1))
        if text:
            cell.insert(0, text)
            # cell.config(text=text)

        cell.configure(state="readonly")

        cell.bind("<MouseWheel>", self.master.on_mouse_scroll)

        return cell

    def redraw(self):
        for row in range(self._row_count):
            for col in range(self._col_count):
                self.cells[row][col].grid(row=row, column=col)

    def delete_row(self, pos, count=1):

        if count <= 0:
            return

        row_count = self.count_row()

        if not pos < row_count:
                return  # Do nothing.

        count = min(count, row_count - pos)

        for _ in range(count):
            deleted_row = self.cells[pos]
            self.cells.pop(pos)

            for j in range(len(deleted_row)):
                deleted_row[j].grid_remove()
                deleted_row[j].destroy()

        self._row_count -= pos

        self.redraw()

    def delete_col(self, pos, count=1):

        if count <= 0:
            return

        col_count = self.count_col()

        if not pos < col_count:
            return  # Do nothing.

        count = min(count, col_count - pos)

        for row in self.cells:
            for _ in range(count):
                deleted_cell = row[pos]
                row.pop(pos)
                deleted_cell.grid_remove()
                deleted_cell.destroy()

        self._col_count -= count

        self.redraw()

    def clear_cell(self, row, col):
        self.cells[row][col].delete(0, tk.END)

    def clear_all(self):
        for row in range(self.count_row()):
            for col in range(self.count_col()):
                self.clear_cells(row, col)


def test_table_area():
    root = tk.Tk()
    # root.withdraw()
    root.on_mouse_scroll = lambda: 0
    table_area = Cells(root)
    table_area.pack()

    for j in range(10):
        table_area.insert_row(j, 1) #, text=str(j))

    for i in range(10):
        table_area.insert_col(i, 1) #, text=str(i))

    table_area.set_value(4, 4, 100)
    root.mainloop()

def test_table_frame(data_size='small'):

    root = tk.Tk()
    table_frame = TableFrame(root)
    table_frame.pack(side="top", fill="both", expand=True)

    # table_frame.cells.insert_col(0, 20, text="bar")
    # table_frame.cells.insert_row(0, 19, text="foo")
    # table_frame.row_header.insert_row(0, 20, text="row")
    # table_frame.col_header.insert_col(0, 20, text="col")

    table_frame.insert_row(0, 10 if data_size == 'small' else 100)
    table_frame.insert_col(0, 10 if data_size == 'small' else 100)
    for col in range(10 if data_size == 'small' else 100):
        for row in range(10 if data_size == 'small' else 100):
            table_frame.set_value(row, col, row * 100 + col)


    table_frame.set_value(4, 4, 10)
    # table_frame.delete_col(1, 2)
    # table_frame.delete_row(8, 2)

    root.mainloop()

if __name__ == '__main__':
    #test_table_area()
    test_table_frame('big')
