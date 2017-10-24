"""
A simple TKinter GUI to edit the model table in a database.
"""
import sqlite3
import tkinter as tk
from tkinter import N, S, E, W
from tkinter import TOP, BOTTOM, LEFT, RIGHT, END, ALL


def edit_model(outDB):
    """Main function."""
    db = outDB
    tbl = 'model'

    root = tk.Tk()
    w=root.winfo_screenwidth()
    h=root.winfo_screenheight()
    root.geometry("600x600+%d+%d" % ( (w-400)/2, (h-300)/2 ) )
    
    model_window = EntryWindow(root, *[db, tbl])
    root.mainloop()
    root.destroy()


class EntryWindow(tk.Frame):

    """
    Provides a simple data edit window for the model table in given database.
    """

    def __init__(self, master=None, *args):
        tk.Frame.__init__(self, master)
        self.master = master
        self.database = args[0]
        self.table = args[1]
        self.init_window()

    def init_window(self):
        """Build the entry window."""
        self.master.title('Edit the Model Metadata')
        self.grid(column=0, row=0, sticky=(N, W, E, S), padx=10, pady=5)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        with sqlite3.connect(self.database) as conn:
            c = conn.cursor()
            c.execute('SELECT min(rowid) FROM model')
            self.row_id = c.fetchone()[0]            
            c.execute("SELECT * FROM model")
            self.metadata = list(c.fetchone())

        # Add a label and entry box for each column in table.
        self.title = tk.StringVar(value=self.metadata[0])
        self.description = tk.StringVar(value=self.metadata[1])
        self.copyright = tk.StringVar(value=self.metadata[2])
        self.author = tk.StringVar(value=self.metadata[3])
        self.definition_url = tk.StringVar(value=self.metadata[4])
        self.dmid = tk.StringVar(value=self.metadata[5])
        self.entryid = tk.StringVar(value=self.metadata[6])
        self.dataid = tk.StringVar(value=self.metadata[7])
        
        tk.Label(self, text='Title').grid(row=0, column=0, pady=1, sticky=E)
        title_entry = tk.Entry(self, textvariable=self.title, width=50).grid(row=0, column=1, pady=1, padx=5)

        tk.Label(self, text='Description').grid(row=1, column=0, pady=1, sticky=E)
        description_entry = tk.Text(self, height=5, width=50)
        description_entry.insert(END, self.description.get())
        description_entry.grid(row=1, column=1, pady=1, padx=5)

        tk.Label(self, text='Copyright').grid(row=2, column=0, pady=1, sticky=E)
        copyright_entry = tk.Entry(self, textvariable=self.copyright, width=50).grid(row=2, column=1, pady=1, padx=5)

        tk.Label(self, text='Author').grid(row=3, column=0, pady=1, sticky=E)
        author_entry = tk.Entry(self, textvariable=self.author, width=50).grid(row=3, column=1, pady=1, padx=5)

        tk.Label(self, text='Defining URL').grid(row=4, column=0, pady=1, sticky=E)
        definition_url_entry = tk.Entry(self, textvariable=self.definition_url, width=50).grid(row=4, column=1, pady=1, padx=5)


        def save(self):
            """Get entries from input fields and insert into database table."""
            self.metadata[0] = self.title.get()
            self.metadata[1] = description_entry.get("1.0",'end-1c')
            self.metadata[2] = self.copyright.get()
            self.metadata[3] = self.author.get()
            self.metadata[4] = self.definition_url.get()

            # Build the SQL statement
            stmnt = ('update model SET title = ?, description = ?, copyright = ?, author = ?, definition_url = ?, dmid = ?, entryid = ?, dataid = ? WHERE rowid = {0}'.format(self.row_id))
            with sqlite3.connect(self.database) as conn:
                c = conn.cursor()
                c.execute(stmnt, self.metadata)
                conn.commit()
            
            self.quit()

        # Add button to save changes to database.
        submit_button = tk.Button(self, text='Save & Close', width=20, command=lambda: save(self))
        submit_button.grid(row= 7, column=0, sticky=E, pady=10, padx=1)
