import tkinter as tk
from collections import namedtuple

__all__ = ["CellCanvas"]

CellCoord = namedtuple('CellCoord', ['row', 'col'])
CanvasCoord = namedtuple('CanvasCoord', ['x', 'y'])

class Cell(tk.Frame):

    default_height = 20
    default_width = 50

    def __init__(self, master=None, cnf={}, **kw):

        tk.Frame.__init__(self, master, cnf, **kw)
        self.grid_propagate(0)
        self.widget = tk.Entry(self, readonlybackground="#ffffff",
                               relief="flat")

        self.widget.grid(row=0, column=0, sticky='nsew')
        self.grid_rowconfigure(0, weight=1)

    def clear(self):
        self.widget.delete(0, tk.END)


class CellCanvas(tk.Canvas):

    def __init__(self, master=None, cnf={}, **kw):

        tk.Canvas.__init__(self, master, cnf, **kw)

        self.master = master
        self.below_these = []
        self.cells = CellFrame(self.master, row_count=0, col_count=0)
        self.item = self.create_window((0, 0), anchor='nw', window=self.cells)
        self.vtcells = VirtualCells()
        self.offset_col = 0
        self.offset_row = 0

        self.bind("<Configure>", self.on_configure)
        self.resize_cells(force=True)

    def on_configure(self, event):
        self.resize_cells()

    def xview(self, *arg):
        tk.Canvas.xview(self, *arg)
        self.on_move_view()
        
    def yview(self, *arg):
        tk.Canvas.yview(self, *arg)
        self.on_move_view()

    def get_view(self):
        view_from = self.canvasx(0), self.canvasy(0)
        w, h = self.winfo_width(), self.winfo_height()
        view_to = self.canvasx(w), self.canvasy(h)

        return view_from, view_to

    def get_visible_cellframe(self):
        view_from, view_to = self.get_view()

        x_to = min(view_to[0], self.vtcells.get_width())
        y_to = min(view_to[1], self.vtcells.get_height())

        return view_from, (x_to, y_to)
        
    def on_move_view(self):        
        # On scroll or jump
        if not self.reposition_cells():
            self.resize_cells()

    def check_reposition(self):

        cell_from, cell_to = self.get_visible_cells()

        row_diff = self.offset_row - cell_from.row
        col_diff = self.offset_col - cell_from.col

        if row_diff > 0 or col_diff > 0:
            return True
        else:
            visible_cell_size = (cell_to.row - cell_from.row) * \
                                (cell_to.col - cell_from.col)
            
            drawn_size = (cell_to.row - self.offset_row) * \
                         (cell_to.col - self.offset_col)
                         
            if drawn_size > 3 * visible_cell_size:
                return True
        
        return False

    def reposition_cells(self, force=False):
        # Reposition cells with margins of 10 rows and cols.
        
        if not force:
            if not self.check_reposition():
                return False
        
        cell_from, cell_to = self.get_visible_cells()
       
        cell_from = CellCoord(max(0, cell_from.row - 10), 
                              max(0, cell_from.col - 10))

        self.cells.clear_all()
        prev_offset = CanvasCoord(self.vtcells.col2x(self.offset_col),
                                  self.vtcells.row2y(self.offset_row))
        
        self.offset_row, self.offset_col = cell_from

        offset = CanvasCoord(self.vtcells.col2x(cell_from.col),
                             self.vtcells.row2y(cell_from.row))
        
        self.move(self.item, 
                  offset.x - prev_offset.x,
                  offset.y - prev_offset.y)

        row_diff = cell_to.row - cell_from.row - self.cells.row_count
        col_diff = cell_to.col - cell_from.col - self.cells.col_count

        if row_diff > 0:
            self.cells.insert_rows(self.cells.row_count, row_diff)
        elif row_diff < 0:
            self.cells.delete_rows(self.cells.row_count + row_diff, -row_diff)
        
        if col_diff > 0:
            self.cells.insert_cols(self.cells.col_count, col_diff)
        elif col_diff < 0:
            self.cells.delete_cols(self.cells.col_count + col_diff, -col_diff)
            
        for row in range(self.cells.row_count):
            for col in range(self.cells.col_count):
                value = self.vtcells.get_value(row + self.offset_row, col + self.offset_col)
                self.cells.set_value(row, col, value)
                
        return True
        
    def resize_cells(self, force=False):

        if not force:
            if not self.check_redraw():
                return False

        cell_from, cell_to = self.get_visible_cells()
        # print("resize", cell_from.row, cell_from.col, cell_to.row, cell_to.col) # debug
        
        prev_row_count = self.cells.row_count
        prev_col_count = self.cells.col_count
        
        rows = cell_to.row - self.cells.row_count - self.offset_row
        cols = cell_to.col - self.cells.col_count - self.offset_col
        # print("rows:", cell_to.row, self.cells.row_count, self.offset_row) # debug
        
        if rows > 0:    # Extend rows
            self.cells.insert_rows(self.cells.row_count, rows)
            for row in range(prev_row_count, self.cells.row_count):
                for col in range(self.cells.col_count):
                    value = self.vtcells.get_value(row + self.offset_row, col + self.offset_col)
                    self.cells.set_value(row, col, value)
            
        elif rows < 0: # Delete rows
            self.cells.delete_rows(self.cells.row_count + rows, -rows)
        
        if cols > 0:
            self.cells.insert_cols(self.cells.col_count, cols)
            for col in range(prev_col_count, self.cells.col_count):
                for row in range(self.cells.row_count):
                    value = self.vtcells.get_value(row + self.offset_row, col + self.offset_col)
                    self.cells.set_value(row, col, value)
        
        elif cols < 0:
            self.cells.delete_cols(self.cells.col_count + cols, -cols)
            
        return True


    def update_scrollregion(self):

        width = self.vtcells.get_width()
        height = self.vtcells.get_height()

        scrollregion = (0, 0, width, height)
        self.config(scrollregion=scrollregion)

    def get_visible_cells(self):
        """Get top-left & bottom-right positions to place CellFrame."""
        view_from, view_to = self.get_visible_cellframe()
        # print("view_to:", view_to[0], view_to[1])  # debug
        view_from_x, view_from_y = view_from
        view_to_x, view_to_y = view_to

        cell_from = CellCoord(self.vtcells.y2row(view_from_y),
                              self.vtcells.x2col(view_from_x))
        
        cell_to_y = self.vtcells.y2row(view_to_y)
        cell_to_x = self.vtcells.x2col(view_to_x)        
        
        # if view_to_y != view_from_y:
        #     cell_to_y += 1
        #
        # if view_to_x != view_from_x:
        #     cell_to_x += 1

        cell_to = CellCoord(cell_to_y, cell_to_x)

        return cell_from, cell_to

    def check_redraw(self):
        """Return true if redraw needed.

        Take intersection of virtual cells and visible area
        if the visible cells are smaller than the intersection,
        expand the area.

        if virtual cells is smaller than view, no need to redraw.
        """
        view_from, view_to = self.get_visible_cellframe()
        view_from_x, view_from_y = view_from
        view_to_x, view_to_y = view_to

        if view_from_x < self.vtcells.col2x(self.offset_col):
            return True
        if view_from_y < self.vtcells.row2y(self.offset_row):
            return True
        # print('check x:' + str(view_to_x) + ', ' + str(self.offset_col + self.cells.get_width()))   #debug
        if view_to_x > self.vtcells.col2x(self.offset_col) + self.cells.get_width():
            return True
        #print('check y:' + str(view_to_y) + ', ' + str(self.offset_row + self.cells.get_height()))  # debug
        if view_to_y > self.vtcells.row2y(self.offset_row) + self.cells.get_height():
            return True

        return False

    def insert_row(self, pos, count=1):

        if pos < self.offset_row:
            prev_y = self.vtcells.row2y(self.offset_row)
            self.offset_row += count
            y = self.vtcells.row2y(self.offset_row)
            self.move(self.item, 0, y - prev_y)
            self.vtcells.insert_row(pos, count)
            if not self.reposition_cells():
                self.resize_cells()
            
        elif pos < self.offset_row + self.cells.row_count:
            self.cells.insert_rows(pos - self.offset_row, count)
            self.vtcells.insert_row(pos, count)
            self.resize_cells()
        
        else:
            self.vtcells.insert_row(pos, count)
            self.resize_cells()
        
        self.update_scrollregion()

    def insert_col(self, pos, count=1):
        
        if pos < self.offset_col:
            prev_x = self.vtcells.col2x(self.offset_col)
            self.offset_col += count
            x = self.vtcells.col2x(self.offset_col)
            self.move(self.item, x - prev_x, 0)
            self.vtcells.insert_col(pos, count)
            if not self.reposition_cells():
                self.resize_cells()
            
        elif pos < self.offset_col + self.cells.col_count:
            self.cells.insert_cols(pos - self.offset_col, count)
            self.vtcells.insert_col(pos, count)
            self.resize_cells()
        
        else:
            self.vtcells.insert_col(pos, count)
            self.resize_cells()
        
        self.update_scrollregion()

    def delete_row(self, pos, count=1):

        if pos + count <= self.offset_row:
            prev_y = self.vtcells.row2y(self.offset_row)
            self.offset_row -= count
            y = self.vtcells.row2y(self.offset_row)
            self.move(self.item, 0, y - prev_y)
            self.vtcells.delete_row(pos, count)
            self.resize_cells()
            
        elif pos + count < self.offset_row + self.cells.row_count:
            if pos <= self.offset_row:
                self.cells.delete_rows(self.offset_row, pos + count - self.offset_row)
                self.offset_row = pos
                self.vtcells.delete_row(pos, count)
                self.resize_cells()
            else:
                self.cells.delete_rows(pos, count)
                self.vtcells.delete_row(pos, count)
                self.resize_cells()
        else:
            if pos <= self.offset_row:
                self.cells.delete_rows(self.offset_row, self.cells.row_count)
                self.offset_row = pos
                self.vtcells.delete_row(pos, count)
                self.resize_cells()
            elif pos < self.offset_row + self.cells.row_count:
                self.cells.delete_rows(pos, self.offset_row + self.cells.row_count - pos)
                self.vtcells.delete_row(pos, count)
                self.resize_cells()
            else:
                self.vtcells.delete_row(pos, count)        
                
        self.update_scrollregion()

    def delete_col(self, pos, count=1):
        
        if pos + count <= self.offset_col:
            prev_x = self.vtcells.col2x(self.offset_col)
            self.offset_col -= count
            x = self.vtcells.col2x(self.offset_col)
            self.move(self.item, x - prev_x, 0)
            self.vtcells.delete_col(pos, count)
            self.resize_cells()
            
        elif pos + count < self.offset_col + self.cells.col_count:
            if pos <= self.offset_col:
                self.cells.delete_cols(self.offset_col, pos + count - self.offset_col)
                self.offset_col = pos
                self.vtcells.delete_col(pos, count)
                self.resize_cells()
            else:
                self.cells.delete_cols(pos, count)
                self.vtcells.delete_col(pos, count)
                self.resize_cells()
        else:
            if pos <= self.offset_col:
                self.cells.delete_cols(self.offset_col, self.cells.col_count)
                self.offset_col = pos
                self.vtcells.delete_col(pos, count)
                self.resize_cells()
            elif pos < self.offset_col + self.cells.col_count:
                self.cells.delete_cols(pos, self.offset_col + self.cells.col_count - pos)
                self.vtcells.delete_col(pos, count)
                self.resize_cells()
            else:
                self.vtcells.delete_col(pos, count)        
                
        self.update_scrollregion()

    def set_value(self, row, col, value):
        self.vtcells.set_value(row, col, value)
        if self.has_cell(row, col):
            self.cells.set_value(row - self.offset_row,
                                 col - self.offset_col,
                                 value)
        
        #self.resize_cells()
        #self.cells.update_cells()
        
    def has_cell(self, row, col):
        
        if row < self.offset_row:
            return False
        
        if row >= self.offset_row + self.cells.row_count:
            return False
            
        if col < self.offset_col:
            return False
            
        if col >= self.offset_col + self.cells.col_count:
            return False
            
        return True

    @property
    def row_count(self):
        return self.vtcells.row_count

    @property
    def col_count(self):
        return self.vtcells.col_count


class CellFrame(tk.Frame):

    def __init__(self, master=None, cnf={}, **kw):

        row_count = kw.pop('row_count')
        col_count = kw.pop('col_count')

        tk.Frame.__init__(self, master, cnf={}, **kw)

        self.cells = []
        self.insert_rows(0, row_count)
        self.insert_cols(0, col_count)


    def create_cell(self):
        return Cell(self, width=50, height=20, bg='#dfdfdf')

    def insert_rows(self, pos, count):

        for i in range(count):
            row = [self.create_cell() for j in range(self.col_count)]
            self.cells.insert(pos, row)

        for i in range(pos, self.row_count):
            for j in range(self.col_count):
                self.cells[i][j].grid(row=i, column=j,
                                      padx=(0, 1), pady=(0, 1), sticky='nsew')

    def insert_cols(self, pos, count):

        for i in range(count):
            for row in self.cells:
                row.insert(pos, self.create_cell())

        for c in range(pos, self.col_count):
            for r in range(self.row_count):
                self.cells[r][c].grid(row=r, column=c,
                                      padx=(0, 1), pady=(0, 1), sticky='nsew')

    def delete_rows(self, pos, count):

        for i in range(count):
            row2del = self.cells.pop(pos)
            for j in range(self.col_count):
                cell = row2del.pop()
                cell.grid_remove()
                self.after(10000, self.destroy_cell, cell)
                # cell.update_idletasks()
                # cell.destroy()
                
        for row in range(pos, self.row_count):
            row2move = self.cells[row]
            for col in range(len(row2move)):
                self.cells[row][col].grid(row=row, column=col,
                                          padx=(0, 1), pady=(0, 1), sticky='nsew')

    def delete_cols(self, pos, count):

        for row in self.cells:
            for i in range(count):
                cell = row.pop(pos)
                cell.grid_remove()
                self.after(10000, self.destroy_cell, cell)
                # cell.update_idletasks()
                # cell.destroy()
        
        for row in range(len(self.cells)):
            for col in range(pos, len(self.cells[row])):
                self.cells[row][col].grid(row=row, column=col,
                                          padx=(0, 1), pady=(0, 1), sticky='nsew')

    def destroy_cell(self, cell):
        cell.destroy()
        #print('cell destroyed')


    def delete_all(self):

        # Delete all cells.
        self.delete_rows(0, self.row_count)

#        row_count = self.row_count
#        col_count = self.col_count
#        for i in range(row_count):
#            row2del = self.cells.pop()
#            for j in range(col_count):
#                cell = row2del.pop()
#                cell.grid_remove()
#                # cell.destroy()

    def resize_cells(self, row_count, col_count):
        """Resize cells by appending/deleting rows/cols."""

        if row_count < self.row_count:
            self.delete_rows(row_count, self.row_count - row_count)
        elif row_count > self.row_count:
            self.insert_rows(self.row_count, row_count - self.row_count)
        else:
            pass

        if col_count < self.col_count:
            self.delete_cols(col_count, self.col_count - col_count)
        elif col_count > self.col_count:
            self.insert_cols(self.col_count, col_count - self.col_count)
        else:
            pass

    def set_value(self, row, col, value):
        
        if value is None:
            return

        try:
            cell = self.cells[row][col].widget
            last_state = cell.cget("state")
            cell.config(state="normal")
            cell.delete(0, tk.END)
            cell.insert(0, value)
            cell.config(state=last_state)
        except IndexError:
            print("IndexError:", row, col)


    @property
    def row_count(self):
        return len(self.cells)

    @property
    def col_count(self):
        if self.cells:
            return len(self.cells[0])
        else:
            return 0

    @property
    def cell_count(self):
        return self.row_count * self.col_count

    def get_height(self):
        height = 0
        for row in self.cells:
            height += row[0].winfo_reqheight() + 1

        return height

    def get_width(self):
        width = 0
        if self.cells:
            for cell in self.cells[0]:
                width += cell.winfo_reqwidth() + 1

        return width

    def clear_all(self):
        for row in self.cells:
            for col in row:
                col.clear()

class VirtualCells:

    def __init__(self):

        self.default_height = Cell.default_height + 1
        self.default_width = Cell.default_width + 1

        self.row_count = 0
        self.col_count = 0
        self.data = {}          #{(row, col): str}
        self.row_height = {}    #{row: height}
        self.col_width = {}     #{col: width}

    def row2y(self, row):
        return row * self.default_height

    def y2row(self, y):

        quotient, remainder = divmod(y, self.default_height)
        if remainder == 0:
            return int(quotient)
        else:
            return int(quotient + 1)


    def col2x(self, col):
        return col * self.default_width

    def x2col(self, x):

        quotient, remainder = divmod(x, self.default_width)
        if remainder == 0:
            return int(quotient)
        else:
            return int(quotient + 1)


    def get_height(self):
        return self.default_height * self.row_count

    def get_width(self):
        return self.default_width * self.col_count

    def set_value(self, row, col, value):
        if self.has_cell(row, col):
            self.data[(row, col)] = value
        else:
            raise RuntimeError

    def get_value(self, row, col):
        if self.has_cell(row, col):
            if (row, col) in self.data:
                return self.data[(row, col)]
        else:
            return None

    def has_cell(self, row, col):
        if row < self.row_count \
                and col < self.col_count:
            return True
        return False

    def insert_row(self, pos, count=1):

        pos_move = [other for other in self.data.keys()
                    if other[0] >= pos]

        pos_move = sorted(pos_move, key=lambda other_pos: other_pos[0],
                          reverse=True)

        for other_pos in pos_move:
            row, col = other_pos
            value = self.data.pop(other_pos)
            self.data[row + count, col] = value

        self.row_count += count

    def insert_col(self, pos, count=1):
        pos_move = [other for other in self.data.keys()
                    if other[1] >= pos]

        pos_move = sorted(pos_move, key=lambda other_pos: other_pos[1],
                          reverse=True)

        for other_pos in pos_move:
            row, col = other_pos
            value = self.data.pop(other_pos)
            self.data[row, col + count] = value

        self.col_count += count

    def delete_row(self, pos, count=1):

        count = min(count, self.row_count - pos)

        pos_move = [other for other in self.data.keys()
                    if other[0] >= pos]

        pos_move = sorted(pos_move, key=lambda other_pos: other_pos[0])

        for other_pos in pos_move:
            row, col = other_pos
            if row < pos + count:
                del self.data[other_pos]
            else:
                value = self.data.pop(other_pos)
                self.data[row - count, col] = value

        self.row_count -= count

    def delete_col(self, pos, count=1):

        count = min(count, self.col_count - pos)

        pos_move = [other for other in self.data.keys()
                    if other[1] >= pos]

        pos_move = sorted(pos_move, key=lambda other_pos: other_pos[1])

        for other_pos in pos_move:
            row, col = other_pos
            if col < pos + count:
                del self.data[other_pos]
            else:
                value = self.data.pop(other_pos)
                self.data[row, col - count] = value

        self.col_count -= count
        


def test():

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_propagate(0)
    root.config(width=400, height=600)

    ## Create the canvas
    cnv = CellCanvas(root, borderwidth=0, background="#000000")
    cnv.grid(row=0, column=0, sticky='nsew')
    # cnv.pack()

    row_size = col_size = 100
    cnv.insert_row(0, row_size)
    cnv.insert_col(0, col_size)

    for i in range(row_size):
        for j in range(col_size):
            cnv.set_value(i, j, i * 1000 + j)


    def test_row():
        if test_row.ins:
            cnv.insert_row(5, 3)
        else:
            cnv.delete_row(5, 3)

        test_row.ins = not test_row.ins

    test_row.ins = True

    def test_col():
        if test_col.ins:
            cnv.insert_col(5, 3)
        else:
            cnv.delete_col(5, 3)

        test_col.ins = not test_col.ins

    test_col.ins = True
    
    def output_info():
        print("cells:", cnv.cells.row_count, cnv.vtcells.row_count, cnv.cells_y)
        

    ## Create the scrollbars
    hs = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=cnv.xview)
    vs = tk.Scrollbar(root, orient=tk.VERTICAL, command=cnv.yview)

    # cnv.upper_widgets = [hs, vs]

    cnv.configure(xscrollcommand=hs.set, yscrollcommand=vs.set)
    hs.grid(row=1, column=0, sticky='we')
    vs.grid(row=0, column=1, sticky='ns')

    ## This is the function you want:

    b = tk.Button(root, text='Info', command=output_info)
    b.grid(row=2, column=0, columnspan=2)
    # cnv.upper_widgets.append(b)

    c = tk.Button(root, text='RowOp', command=test_row)
    d = tk.Button(root, text='ColOp', command=test_col)
    c.grid(row=3, column=0, columnspan=2)
    d.grid(row=4, column=0, columnspan=2)

    root.mainloop()


if __name__ == '__main__':
    root = tk.Tk()
    test()