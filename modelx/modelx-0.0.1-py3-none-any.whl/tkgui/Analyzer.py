"""Analyzer window."""
import tkinter as tk
from tkinter import ttk
import inspect

from modelx.gunxpace import fxpsys, CellSet
from modelx.tkgui.TableWidget import TableFrame
from modelx.tkgui.TextList import TextList


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
#----- End For Table -----#

def autoscroll(sbar, first, last):
    """Hide and show scrollbar as needed."""
    first, last = float(first), float(last)
    if first <= 0 and last >= 1:
        sbar.grid_remove()
    else:
        sbar.grid()
    sbar.set(first, last)


class AnalyzerWindow:
    """Ananlyzer Window"""
    def __init__(self, root):

        #tk.Toplevel.__init__(root)

        self.root = root

        pane = tk.PanedWindow(root, orient='vertical', sashwidth=4)
        pane.pack(expand=True, fill=tk.BOTH)

        top_pane = tk.PanedWindow(pane, orient='horizontal', sashwidth=4)

        #self.top = tk.Toplevel(root)
        #self.top.protocol("WM_DELETE_WINDOW", self.close_event)
        #pane.protocol("WM_DELETE_WINDOW", self.close_event)

        tree_frame = ModelTree(top_pane) #, bg='white')
        table_frame = ModelTable(pane, tree_frame) #, bg='white')
        tree_frame.set_linked_table(table_frame)

        src_list = SrcList(top_pane, tree_frame)

        tree_frame.event_listeners['<<TreeviewOpen>>'] = [table_frame, src_list]
        tree_frame.event_listeners['<<TreeviewClose>>'] = [table_frame, src_list]


        top_pane.add(tree_frame)
        top_pane.add(src_list)
        pane.add(top_pane)
        pane.add(table_frame)

        self.cellsets = tree_frame.cellsets


        # def print_node(event):
        #     tree = tree_container.tree
        #     children = tree.get_children(tree.focus())
        #     print(children)
        #
        #
        # root.bind('<<TreeviewOpen>>', print_node)

        # tree_container.pack(fill='both', expand=True)
        # grid_container.pack(fill='both', expand=True)





class ModelTree(tk.Frame):

    def __init__(self, master):
        """
        Args:
            master: Parent tk widget

        Attributes:
            cellsets (dict): map node id (str) of ttk.Treeview to a TreeNode
        """
        tk.Frame.__init__(self, master)
        self.master = master
        self.cellsets = {}     # TreeView ids to cellsets
        self._build_tree()
        self.populate_roots()
        self.linked_table = None
        self.event_listeners = {}      # events to listener widgets


    def _build_tree(self):
        vsb = ttk.Scrollbar(master=self, orient="vertical")
        hsb = ttk.Scrollbar(master=self, orient="horizontal")

        self.tree = tree = ttk.Treeview(master=self,
                                        columns=("module", "type"),
                                        displaycolumns=("module", "type"),
                                        yscrollcommand=lambda f, l: autoscroll(vsb, f, l),
                                        xscrollcommand=lambda f, l: autoscroll(hsb, f, l))

        vsb['command'] = tree.yview
        hsb['command'] = tree.xview

        tree.heading("#0", text="Object", anchor='w')
        tree.heading("type", text="Type", anchor='w')
        tree.heading("module", text="Module", anchor='w')
        #tree.heading("size", text="File Size", anchor='w')

        tree.column("type", stretch=0, width=100)

        # Arrange the tree and its scrollbars in the toplevel
        tree.grid(column=0, row=0, sticky='nswe')   #, in_=master)
        vsb.grid(column=1, row=0, sticky='ns')      #, in_=master)
        hsb.grid(column=0, row=1, sticky='ew')      #, in_=master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        tree.bind('<<TreeviewOpen>>', self.on_treeview_open)
        tree.bind('<<TreeviewClose>>', self.on_treeview_close)
        #tree.bind('<Double-Button-1>', change_dir)

        #self.populate_roots(tree)
        #self.populate_roots(tree)

    def set_linked_table(self, table):
        self.linked_table = table

    def on_treeview_open(self, event):
        #tree = event.widget
        parent_id = self.tree.focus()
        self.populate_subtree(parent_id)

        # parent = self.cellsets[parent_id]

        # if parent.type_ == 'funx':
        #     print(inspect.getsourcefile(parent.funx.func))
        #     print(inspect.getsource(parent.funx.func))

        # print(parent.funx.func.__code__)
        # import inspect as isp
        # print(isp.getsource(parent.funx.func))

        # print(self.list_funxs())
        # print([self.tree.item(node_id, option='open')
        #        for node_id in self.list_funxs()])
        # parent_pos = self.list_funxs().index(parent_id)


        # children = self.tree.get_children(parent_id)
        # for child_id in children:
        #     child_node = self.cellsets[child_id]
        #     if child_node.type_ == 'funx':
        #         pos = self.list_all_funxs().index(child_id)
        #         self.linked_table.insert_node(pos, self.cellsets[child_id])

        for listener in self.event_listeners['<<TreeviewOpen>>']:
            listener.event_generate('<<TreeviewOpen>>', when='tail')

    def on_treeview_close(self, event):
        # tree = event.widget
        node = self.tree.focus()
        self.delete_subtree(node)

        for listener in self.event_listeners['<<TreeviewClose>>']:
            listener.event_generate('<<TreeviewClose>>', when='tail')

    def populate_roots(self):

        for space in fxpsys.extract_spaces():
            node = self.tree.insert('', 'end', text=space.name, values=["", "Space"])
            self.cellsets[node] = CellSet('space', space, None)
            self.populate_subtree(node)

        #self.populate_tree(tree, node)

    def populate_subtree(self, node_id):

        tree = self.tree
        tree.delete(*tree.get_children(node_id))
        parent = self.cellsets[node_id]

        children = parent.get_children()
        for child in children:
            obj = child.get_obj()
            child_id = tree.insert(node_id, 'end', text=obj.name,
                                   values=[obj.id.module, type(obj).__name__])
            self.cellsets[child_id] = child
            if child.get_children():
                tree.insert(child_id, 0, text="__dummy__")

    def delete_subtree(self, parent):
        # delete node from self.tree
        # self.tree.delete(parent)
        # delete node from self.cellsets
        # for node in self.cellsets:
        #     if not self.tree.exists(node):
        #         del self.cellsets[node]

        nodes_to_delete = self.tree.get_children(parent)

        for node in nodes_to_delete:
            self.tree.delete(node)

        self.cellsets = {node: self.cellsets[node] for node in self.cellsets
                         if self.tree.exists(node)}


        self.tree.insert(parent, 0, text="__dummy__")
        # update_table


    def list_all_nodes(self):
        """List ids of all visible cellsets in ModelTree from top to bottom."""
        parent_list = list(self.tree.get_children())
        #print(node_list)
        node_list = []
        for parent in parent_list:
            subnodes = [parent]
            self._list_children(0, subnodes)
            node_list += subnodes

        return node_list

    def list_all_funxs(self):
        """List ids of all visible funxs cellsets shown in ModelTree from top to bottom."""
        node_list = self.list_all_nodes()
        return [node for node in node_list
                if self.cellsets[node].type_ == 'funx']

    def list_children(self, node):
        node_list = [node]
        self._list_children(0, node_list)
        return node_list

    def _list_children(self, idx, node_list):
        """Populate node_list with all descendants of the node at idx.
            node_list ([str,]): list of node_ids to be filled.
            idx (int): index of parent node in node_list.
        """

        node = node_list[idx]
        # Cannot just use parent's open option as called from event handler.
        children = [item for item in self.tree.get_children(node)
                    if self.tree.item(item, option='text') != "__dummy__"]

        node_list[idx + 1:idx + 1] = children
        descs_len = len(children)
        idx_beg, idx_end = idx + 1, idx + 1 + descs_len
        idx = idx_beg
        while idx < idx_end:
            descs_len_each = self._list_children(idx, node_list)
            idx += descs_len_each
            idx_end += descs_len_each
            descs_len += descs_len_each
            idx += 1
        return descs_len


class TableIndex:
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

class ModelColumn:

    def __init__(self):
        self.col_text = None
        self.cell_data = {}     # row idx to value


class TableColumn:
    def __init__(self, node):
        self.node = node

class SrcList(TextList):

    def __init__(self, master, model_tree):

        TextList.__init__(self, master)
        self.bind('<<TreeviewOpen>>', self.on_treeview_open)
        self.model_tree = model_tree


    def on_treeview_open(self, event):
        updated_nodes = self.model_tree.list_all_funxs()

        for node in updated_nodes:
            src = inspect.getsource(self.model_tree.cellsets[node].funx.func)
            self.append_row(src)


class ModelTable(TableFrame):

    def __init__(self, master, model_tree):
        """
        Args:
            master:
            tree:

        Attributes:
            row_idx (str): name of the funxion parameter for the row.
        """
        TableFrame.__init__(self, master)
        self.master = master
        self.model_tree = model_tree
        self.row_param = 'x'
        self.col_params = ['n']
        self.idx_to_row = {} # idx to row pos must be incremental

        self.bind('<<TreeviewOpen>>', self.on_treeview_open)
        self.bind('<<TreeviewClose>>', self.on_treeview_close)

        self.nodes = []         # Funx nodes in the order of their column positions
        self.col_idxs = []   # Node lengths in the order of their column positions
        self.col_lengths = []

    def on_treeview_open(self, event):
        updated_nodes = self.model_tree.list_all_funxs()
        inserted_nodes = [node for node in updated_nodes
                          if node not in self.nodes]

        if not inserted_nodes:
            return

        first_inserted_node = updated_nodes.index(inserted_nodes[0])
        inserted_node_count = len(inserted_nodes)

        self.nodes[first_inserted_node:first_inserted_node] = inserted_nodes
        self.col_idxs[first_inserted_node:first_inserted_node] = [None] * inserted_node_count
        self.col_lengths[first_inserted_node:first_inserted_node] = [None] * inserted_node_count

        for offset, node in enumerate(inserted_nodes):
            node_pos = first_inserted_node + offset
            cellset = self.model_tree.cellsets[node]
            self.col_idxs[node_pos] = tuple(cellset.generate_idx(params=self.col_params))
            self.col_lengths[node_pos] = len(self.col_idxs[node_pos])
            col_pos = sum(self.col_lengths[:node_pos])
            self.insert_node(col_pos, cellset)

        # self.nodes += inserted_nodes
        # self.col_lengths += [self.master(node)
        #                       for node in inserted_nodes]
        # print(inserted_nodes)


    def on_treeview_close(self, event):

        updated_nodes = self.model_tree.list_all_funxs()
        deleted_nodes = [node for node in self.nodes
                         if node not in updated_nodes]

        for node in deleted_nodes:
            pos = self.nodes.index(node)
            self.delete_col(pos, self.col_lengths[pos])
            del self.nodes[pos]
            del self.col_idxs[pos]
            del self.col_lengths[pos]



        # print(deleted_nodes)

        # print(nodes[0], True == self.model_tree.tree.item(nodes[0], option='open'))

    def get_new_row_pos(self, row_idx):
        # Return row position for a new row index.
        # TODO: Find preceding
        prec_idx = max([idx for idx in self.idx_to_row if idx < row_idx])
        return self.idx_to_row[prec_idx] + 1

    def insert_row_idx(self, row_idx):

        if not self.idx_to_row: # No row exists
            row_pos = 0
        elif row_idx in self.idx_to_row:
            return
        else:
            leading_idxs = [idx for idx in self.idx_to_row if idx < row_idx]

            if not leading_idxs: # row_idx is the first
                row_pos = 0
            else:
                row_pos = self.idx_to_row[max(leading_idxs)] + 1

                # Shit rows by one
                following_idxs = [idx for idx in self.idx_to_row
                                  if self.idx_to_row[idx] >= row_pos]

                for idx in following_idxs:
                    self.idx_to_row[idx] += 1

        self._insert_row_idx_at(row_idx, row_pos)

    def _insert_row_idx_at(self, row_idx, row_pos):
        self.insert_row(row_pos)
        self.set_row_header(row_pos, row_idx)
        self.idx_to_row[row_idx] = row_pos

    def insert_node(self, col_pos, cellset):

        col_params = self.col_params
        row_param = self.row_param

        col_idxes = tuple(cellset.generate_idx(col_params))
        row_idxes = tuple(cellset.generate_idx(row_param))
        self.insert_col(col_pos, len(col_idxes))

        # Set values
        for offset, col_idx in enumerate(col_idxes):
            col_header_text = cellset.funx.name + str(col_idx)
            self.set_col_header(col_pos + offset, col_header_text)
            for row_idx in row_idxes:
                self.insert_row_idx(row_idx)
                row_pos = self.idx_to_row[row_idx]
                self.set_value(row_pos, col_pos + offset, cellset.get_value(row_idx + col_idx))


    def _node_to_cols(self, node):
        pass

    def delete_node(self, pos, node):
        pass

    def get_node_pos(self, node):
        pass

    def get_celldata(self):
        """ Return dictionary of (space, funx) -> [(idx, value), ..] """

        cells = fxpsys.extract_cells()
        celldata = {}
        for cell in cells:
            key = (cell.sapce, cell.funx)
            if key not in celldata:
                celldata[key] = (cell.idx, cell.value)
        return celldata


def test_generate_idx():
    # from itertools import product

    class Foo:
        pass
    Foo.params = ['x', 'y']
    Foo.idx = {'x':[0, 1, 2], 'y':['m', 'f']}
    Foo.values = [Foo.idx['x'], Foo.idx['y']]
    gen = CellSet.generate_idx(Foo, ('y', 'x'))

    while True:
        try:
            print(next(gen))
        except StopIteration:
            print('Iterator exausted')
            break



def main():

    root = tk.Tk()
    #root.withdraw()
    app = AnalyzerWindow(root)

    root.mainloop()


if __name__ == '__main__':
    main()
    #test_generate_idx()
