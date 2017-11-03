import os
from .core import Task, DownloadManager
from Tkinter import *
import ttk
import tkFont
import tkMessageBox
import tkFileDialog


class App(Frame):
    """
    The application

    Attributes:
      wuri -- URI entry
      woutdir -- output directory entry
      wbrowse -- output directory browse button
      wrow2 -- frame for the second widget row
      wstart -- start/stop button
      wquit -- quit button
      wstatus -- status label
      vuri -- StringVar for URI entry
      voutdir -- StringVar for output directory entry
      vstart -- StringVar for start/stop button
      vstatus -- StringVar for status label
      running -- True if a download is in progress, False otherwise
      dm -- DownloadManager instance (None until started)
      task -- Task instance (None until started)

    """

    status_update_delay = 2

    def __init__(self, master=None):
        self.running = False
        self.dm = None
        self.task = None

        master.title("pypldl")
        # change some default styling conf
        font = tkFont.nametofont("TkDefaultFont")
        font.configure(size=12)
        font = tkFont.nametofont("TkTextFont")
        font.configure(size=13)

        # create widgets (including self)
        # order is important, for tab-order
        Frame.__init__(self, master)
        self.pack(fill='x')

        self.vuri = StringVar()
        self.wuri = ttk.Entry(self, textvar=self.vuri, width=70)

        self.wrow2 = Frame(self)

        self.voutdir = StringVar(value=os.getcwd())
        self.woutdir = ttk.Entry(self.wrow2, textvar=self.voutdir)
        self.wbrowse = ttk.Button(self.wrow2, width=3, text='...', command=self.browse_outdir)

        self.vstart = StringVar(value='Start')
        self.wstart = ttk.Button(self.wrow2, width=5, textvar=self.vstart, command=self.start)

        self.wquit = ttk.Button(self.wrow2, width=5, text='Quit', command=self.quit)

        self.vstatus = StringVar()
        self.wstatus = ttk.Label(self, textvar=self.vstatus, anchor=W, justify=LEFT, padding=3)

        # pack everything
        self.wuri.pack(side=TOP, expand=True, fill='x')
        self.wrow2.pack(side=TOP, fill='x')
        self.woutdir.pack(side=LEFT, expand=True, fill='x')
        self.wquit.pack(side=RIGHT)
        self.wstart.pack(side=RIGHT)
        self.wbrowse.pack(side=RIGHT)
        self.wstatus.pack(side=BOTTOM, expand=True, fill='x')

        # set minsize based on default packed size
        master.update()
        master.minsize(200, master.winfo_height())

        # bindings
        master.bind("<Return>", lambda ev: self.start())
        master.bind("<Escape>", lambda ev: self.quit())

        # use URI from clipboard, if any
        try:
            clipboard = master.clipboard_get().strip()
        except TclError:
            clipboard = ''
        if '://' in clipboard:
            self.vuri.set(clipboard)
        self.vstatus.set("Enter a URI and press 'Start'.")

        self.wuri.focus()
        

    def set_status(self, msg, color=None):
        self.vstatus.set(msg)
        self.wstatus['foreground'] = color

    def browse_outdir(self):
        outdir = tkFileDialog.askdirectory(title="Output directory", initialdir=self.voutdir.get(), mustexist=True)
        self.voutdir.set(outdir)

    def quit(self):
        if self.running:
            if not tkMessageBox.askokcancel("Quit", "Download is running, quit anyway?"):
                return
        Frame.quit(self)

    def start(self):
        if self.task is not None:
            return  # already started, ignore
        uri = self.vuri.get()
        if not uri:
            return  # no URI, ignore
        task = Task.from_uri(uri)
        if task is None:
            self.set_status("Invalid URI or no handler found", 'red')
            return

        self.wuri['state'] = DISABLED
        self.wstart['state'] = DISABLED
        self.set_status("Starting...")
        self.task = task
        self.dm = DownloadManager()
        self.dm.outdir = self.voutdir.get()
        self.task.start(self.dm)
        self.after(self.status_update_delay, self.running_task)
        self.running = True

    def running_task(self):
        if self.task.join():
            self.running = False
            self.set_status('Download complete.')
        else:
            progress, status = self.task.progress()
            self.set_status("%3.f%% -- %s" % (progress * 100, status))
            self.after(self.status_update_delay, self.running_task)



def main():
    app = App(Tk())
    app.mainloop()


if __name__ == '__main__':
    main()

