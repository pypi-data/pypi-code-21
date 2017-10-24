"""
A simple TKinter GUI to edit the model table in a database.
"""
import sqlite3
import tkinter as tk
from tkinter import N, S, E, W
from tkinter import TOP, BOTTOM, LEFT, RIGHT, END, ALL
from tkinter import messagebox

def edit_record(outDB):
    """Main function."""
    db = outDB
    tbl = 'record'

    root = tk.Tk()
    w=root.winfo_screenwidth()
    h=root.winfo_screenheight()
    root.geometry("600x600+%d+%d" % ( (w-400)/2, (h-300)/2 ) )
    
    model_window = EntryWindow(root, *[db, tbl])
    root.mainloop()

class EntryWindow(tk.Frame):

    """
    Provides a simple data edit window for the model table in given database.
    """

    def __init__(self, master=None, *args):
        tk.Frame.__init__(self, master)
        self.master = master
        self.database = args[0]
        self.table = args[1]
        with sqlite3.connect(self.database) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM record")
            tmp = c.fetchall()
        
        #  convert the tuples to lists so they can be updated.
        self.records = []
        for t in tmp:
            self.records.append(list(t))
            
        self.numrecs = len(self.records)
        self.recndx = 0
        self.init_window()

    def init_window(self):
        """Build the entry window."""
        self.master.title('Edit each Record')            
        self.grid(column=0, row=0, sticky=(N, W, E, S), padx=10, pady=5)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.draw_form()
        
     
    def validnum(self, value):
        "Check for numeric entries and return them as a string or return an empty string. "
        if str(value).isnumeric():
            return(str(value))
        elif str(value).find('.') == -1:  # check that there is not a decimal point
            return('')
        elif str(value).find('.') > -1:  # check that there is decimal point
            val_list = []
            val_list = str(value).split('.')
            if len(val_list) > 2:
                return('')
            if str(val_list[0]).isnumeric() and str(val_list[1]).isnumeric():
                return(str(val_list[0])+'.'+str(val_list[1]))
        else:
            return('')
            
     
    def draw_form(self):        
        self.header = self.records[self.recndx][0]
        self.label = tk.StringVar(value=self.records[self.recndx][1])
        self.datatype = tk.StringVar(value=self.records[self.recndx][2])
        self.min_len = tk.StringVar(value=self.validnum(self.records[self.recndx][3]))
        self.max_len =tk.StringVar(value=self.validnum(self.records[self.recndx][4]))
        self.choices = tk.StringVar(value=self.records[self.recndx][5])
        self.regex = tk.StringVar(value=self.records[self.recndx][6])
        self.min_inc_val = tk.StringVar(value=self.validnum(self.records[self.recndx][7]))
        self.max_inc_val = tk.StringVar(value=self.validnum(self.records[self.recndx][8]))
        self.description = tk.StringVar(value=self.records[self.recndx][9])
        self.definition_url = tk.StringVar(value=self.records[self.recndx][10])
        self.pred_obj_list = tk.StringVar(value=self.records[self.recndx][11])
        self.def_txt_value = tk.StringVar(value=self.records[self.recndx][12])
        self.def_num_value = tk.StringVar(value=self.validnum(self.records[self.recndx][13]))
        self.units = tk.StringVar(value=self.records[self.recndx][14])
        self.min_exc_val = tk.StringVar(value=self.validnum(self.records[self.recndx][17]))
        self.max_exc_val = tk.StringVar(value=self.validnum(self.records[self.recndx][18]))

        # Add a label and entry box for each column in table.
        
        tk.Label(self, text='Label').grid(row=0, column=0, pady=1, sticky=E)
        self.label_entry = tk.Entry(self, textvariable=self.label, width=50).grid(row=0, column=1, pady=1, padx=5)

        tk.Label(self, text='Datatype').grid(row=1, column=0, pady=1, sticky=E)
        self.datatype_entry = tk.OptionMenu(self, self.datatype, 'String', 'Integer', 'Decimal', 'Float', 'Date', 'Time', 'Datetime')
        self.datatype_entry.grid(row=1, column=1, pady=1, padx=5)
        
        tk.Label(self, text='Minimum Length').grid(row=2, column=0, pady=1, sticky=E)
        self.min_len_entry = tk.Entry(self, textvariable=self.min_len, width=50).grid(row=2, column=1, pady=1, padx=5)

        tk.Label(self, text='Maximum Length').grid(row=3, column=0, pady=1, sticky=E)
        self.max_len_entry = tk.Entry(self, textvariable=self.max_len, width=50).grid(row=3, column=1, pady=1, padx=5)

        tk.Label(self, text='Choices').grid(row=4, column=0, pady=1, sticky=E)
        self.choices_entry = tk.Entry(self, textvariable=self.choices, width=50).grid(row=4, column=1, pady=1, padx=5)

        tk.Label(self, text='Regular Expression').grid(row=5, column=0, pady=1, sticky=E)
        self.regex_entry = tk.Entry(self, textvariable=self.regex, width=50).grid(row=5, column=1, pady=1, padx=5)

        tk.Label(self, text='Minimum Inclusive Value').grid(row=6, column=0, pady=1, sticky=E)
        self.min_inc_val_entry = tk.Entry(self, textvariable=self.min_inc_val, width=50).grid(row=6, column=1, pady=1, padx=5)
        
        tk.Label(self, text='Maximum Inclusive Value').grid(row=7, column=0, pady=1, sticky=E)
        self.max_inc_val_entry = tk.Entry(self, textvariable=self.max_inc_val, width=50).grid(row=7, column=1, pady=1, padx=5)
        
        tk.Label(self, text='Minimum Exclusive Value').grid(row=8, column=0, pady=1, sticky=E)
        self.min_exc_val_entry = tk.Entry(self, textvariable=self.min_exc_val, width=50).grid(row=8, column=1, pady=1, padx=5)
    
        tk.Label(self, text='Maximum Exclusive Value').grid(row=9, column=0, pady=1, sticky=E)
        self.max_exc_val_entry = tk.Entry(self, textvariable=self.max_exc_val, width=50).grid(row=9, column=1, pady=1, padx=5)

        tk.Label(self, text='Description').grid(row=10, column=0, pady=1, sticky=E)
        self.description_entry = tk.Text(self, height=5, width=50)
        self.description_entry.insert(END, self.description.get())
        self.description_entry.grid(row=10, column=1, pady=1, padx=5)
        
        tk.Label(self, text='Defining URL').grid(row=11, column=0, pady=1, sticky=E)
        self.definition_url_entry = tk.Entry(self, textvariable=self.definition_url, width=50).grid(row=11, column=1, pady=1, padx=5)
        
        tk.Label(self, text='Predicates & Objects').grid(row=12, column=0, pady=1, sticky=E)
        self.pred_obj_list_entry = tk.Text(self, height=5, width=50)
        self.pred_obj_list_entry.insert(END, self.pred_obj_list.get())
        self.pred_obj_list_entry.grid(row=12, column=1, pady=1, padx=5)
        
        tk.Label(self, text='Default Text Value').grid(row=13, column=0, pady=1, sticky=E)
        self.def_txt_value_entry = tk.Entry(self, textvariable=self.def_txt_value, width=50).grid(row=13, column=1, pady=1, padx=5)
        
        tk.Label(self, text='Default Numeric Value').grid(row=14, column=0, pady=1, sticky=E)
        self.def_num_value_entry = tk.Entry(self, textvariable=self.def_num_value, width=50).grid(row=14, column=1, pady=1, padx=5)
        
        tk.Label(self, text='Units').grid(row=15, column=0, pady=1, sticky=E)
        self.units_entry = tk.Entry(self, textvariable=self.units, width=50).grid(row=15, column=1, pady=1, padx=5)
        
        # Add buttons to navigate database.(
        previous_button = tk.Button(self, text='Previous', width=8, command=self.prev_rec)
        previous_button.grid(row= 25, column=0, sticky=E, pady=10, padx=1)
        next_button = tk.Button(self, text='Next', width=8, command=self.next_rec)
        next_button.grid(row= 25, column=40, sticky=E, pady=10, padx=1)
        save_button = tk.Button(self, text='Save', width=8, command=self.save_rec)
        save_button.grid(row= 27, column=0, sticky=E, pady=10, padx=1)
        exit_button = tk.Button(self, text='Exit', width=8, command=self.quit)
        exit_button.grid(row= 27, column=40, sticky=E, pady=10, padx=1)
        
    def update_values(self):
        self.header = self.records[self.recndx][0]
        self.label.set(self.records[self.recndx][1])
        self.datatype.set(self.records[self.recndx][2])
        self.min_len.set(self.validnum(self.records[self.recndx][3]))
        self.max_len.set(self.validnum(self.records[self.recndx][4]))
        self.choices.set(self.records[self.recndx][5])
        self.regex.set(self.records[self.recndx][6])
        self.min_inc_val.set(self.validnum(self.records[self.recndx][7]))
        self.max_inc_val.set(self.validnum(self.records[self.recndx][8]))
        self.description_entry.delete(1.0, END)  # clear the display
        self.description.set(self.records[self.recndx][9])
        self.definition_url.set(self.records[self.recndx][10])
        self.pred_obj_list_entry.delete(1.0, END)  # clear the display
        self.pred_obj_list.set(self.records[self.recndx][11])
        self.def_txt_value.set(self.records[self.recndx][12])
        self.def_num_value.set(self.validnum(self.records[self.recndx][13]))
        self.units.set(self.records[self.recndx][14])
        self.min_exc_val.set(self.validnum(self.records[self.recndx][17]))
        self.max_exc_val.set(self.validnum(self.records[self.recndx][18]))
        

    def prev_rec(self):
        if self.recndx > 0:
            self.recndx -= 1
        elif self.recndx == 0:
            self.recndx = self.numrecs - 1
        
        self.update_values()

    def next_rec(self):
        if self.recndx < self.numrecs - 1:
            self.recndx += 1
        elif self.recndx == self.numrecs - 1:
            self.recndx = 0
    
        self.update_values()
        
    def save_rec(self):        
        "Create a list for execution in SQL"
        updates = []
        updates.append(self.label.get())
        updates.append(self.datatype.get())
        updates.append(self.min_len.get())
        updates.append(self.max_len.get())
        updates.append(self.choices.get())
        updates.append(self.regex.get())
        updates.append(self.min_inc_val.get())
        updates.append(self.max_inc_val.get())
        updates.append(self.description_entry.get("1.0",'end-1c'))
        updates.append(self.definition_url.get())
        updates.append(self.pred_obj_list_entry.get("1.0",'end-1c'))
        updates.append(self.def_txt_value.get())
        updates.append(self.def_num_value.get())
        updates.append(self.units.get())
        updates.append(self.min_exc_val.get())
        updates.append(self.max_exc_val.get())
        
        # Build the SQL statement
        stmnt = ('UPDATE record SET label = ?, datatype = ?, min_len = ?, max_len = ?, choices = ?, regex = ?, min_inc_val = ?, max_inc_val = ?, description = ?, definition_url = ?, pred_obj_list = ?, def_txt_value = ?, def_num_value =?, units = ?, min_exc_val = ?, max_exc_val = ? WHERE header = "{0}"'.format(self.header))
        with sqlite3.connect(self.database) as conn:
            c = conn.cursor()
            c.execute(stmnt, updates)
            conn.commit()
            
            "Update the records list in the context of the DB update"
            self.records[self.recndx][1] = self.label.get()
            self.records[self.recndx][2] = self.datatype.get()
            self.records[self.recndx][3] = self.min_len.get()
            self.records[self.recndx][4] = self.max_len.get()
            self.records[self.recndx][5] = self.choices.get()
            self.records[self.recndx][6] = self.regex.get()
            self.records[self.recndx][7] = self.min_inc_val.get()
            self.records[self.recndx][8] = self.max_inc_val.get()
            self.records[self.recndx][9] = self.description.get()
            self.records[self.recndx][10] = self.definition_url.get()
            self.records[self.recndx][11] = self.pred_obj_list.get()
            self.records[self.recndx][12] = self.def_txt_value.get()
            self.records[self.recndx][13] = self.def_num_value.get()
            self.records[self.recndx][14] = self.units.get()
            self.records[self.recndx][7] = self.min_exc_val.get()
            self.records[self.recndx][8] = self.max_exc_val.get()
            
            messagebox.showinfo(self.database, "Record Saved")
