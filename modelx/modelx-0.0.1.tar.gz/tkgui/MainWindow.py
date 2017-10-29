"""
Code illustration: 2.12.py
Features Added:
	Add context/ Pop-up Menu
    Set focus on launch

@Tkinter GUI Application Development Blueprints
"""
import sys
import os
import tkinter as tk
from tkinter import Tk, \
    Toplevel, Frame, Label, Text, \
    Entry, Checkbutton, Button, Menu, Scrollbar, \
    PhotoImage, IntVar, StringVar, BooleanVar
import tkinter.filedialog
import tkinter.messagebox
import tkinter.font as tkfont
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk

### From here: WIS added for Syntax Highlighting
from modelx.tkgui.idlesub.configHandler import idleConf
from modelx.tkgui.idlesub.ColorDelegator import ColorDelegator
from modelx.tkgui.idlesub.Percolator import Percolator

""" by default, imports settings from ~/.idlerc. See idleConf docstring for more details.
Change cfgDir attribute to alter the settings folder.
Percolator class is used to manage filters (e.g., ColorDelegator) and send commands
to them. """
### End here: WIS added for Syntax Highlighting

import modelx.tkgui.Analyzer as Analyzer

PROGRAM_NAME = "Funxapce"
file_name = None

color_schemes = {
    'Default': '#000000.#FFFFFF',
    'Greygarious': '#83406A.#D1D4D1',
    'Aquamarine': '#5B8340.#D1E7E0',
    'Bold Beige': '#4B4620.#FFF0E1',
    'Cobalt Blue': '#ffffBB.#3333aa',
    'Olive Green': '#D1E7E0.#5B8340',
    'Night Mode': '#FFFFFF.#000000',
}

def autoscroll(sbar, first, last):
    """Hide and show scrollbar as needed."""
    first, last = float(first), float(last)
    # if first <= 0 and last >= 1:
    #     sbar.grid_remove()
    # else:
    #     sbar.grid()
    sbar.set(first, last)




class MainWindow(Tk):

### From here: WIS added for Syntax Highlighting

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

    def __init__(self):

        Tk.__init__(self)

        new_file_icon = PhotoImage(file='icons/new_file.gif')
        open_file_icon = PhotoImage(file='icons/open_file.gif')
        save_file_icon = PhotoImage(file='icons/save.gif')
        cut_icon = PhotoImage(file='icons/cut.gif')
        copy_icon = PhotoImage(file='icons/copy.gif')
        paste_icon = PhotoImage(file='icons/paste.gif')
        undo_icon = PhotoImage(file='icons/undo.gif')
        redo_icon = PhotoImage(file='icons/redo.gif')

        # Set up Menu Bar
        menu_bar = Menu(self)
        
        #-File Menu
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='New', accelerator='Ctrl+N', compound='left',
                              image=new_file_icon, underline=0, command=self.new_file)
        file_menu.add_command(label='Open', accelerator='Ctrl+O', compound='left',
                              image=open_file_icon, underline=0, command=self.open_file)
        file_menu.add_command(label='Save', accelerator='Ctrl+S',
                              compound='left', image=save_file_icon, underline=0, command=self.save)
        file_menu.add_command(label='Save as', accelerator='Shift+Ctrl+S', command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', accelerator='Alt+F4', command=self.exit_editor)
        menu_bar.add_cascade(label='File', menu=file_menu)
        
        # Due to a bug in tkinter, hold references to the image objects to make them appear
        # http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm
        file_menu.new_file_icon = new_file_icon 
        

        #-Edit menu
        edit_menu = Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label='Undo', accelerator='Ctrl+Z',
                              compound='left', image=undo_icon, command=self.undo)
        edit_menu.add_command(label='Redo', accelerator='Ctrl+Y',
                              compound='left', image=redo_icon, command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label='Cut', accelerator='Ctrl+X',
                              compound='left', image=cut_icon, command=self.cut)
        edit_menu.add_command(label='Copy', accelerator='Ctrl+C',
                              compound='left', image=copy_icon, command=self.copy)
        edit_menu.add_command(label='Paste', accelerator='Ctrl+V',
                              compound='left', image=paste_icon, command=self.paste)
        edit_menu.add_separator()
        edit_menu.add_command(label='Find', underline=0,
                              accelerator='Ctrl+F', command=self.find_text)
        edit_menu.add_separator()
        edit_menu.add_command(label='Select All', underline=7,
                              accelerator='Ctrl+A', command=self.select_all)
        menu_bar.add_cascade(label='Edit', menu=edit_menu)
        
        #-Run menu
        run_menu = Menu(menu_bar, tearoff=0)
        run_menu.add_command(label='Run', accelerator='F5', command=self.run)
        menu_bar.add_cascade(label='Run', menu=run_menu)

        #-View Menu
        view_menu = Menu(menu_bar, tearoff=0)
        self.show_line_number = IntVar()
        self.show_line_number.set(1)
        view_menu.add_checkbutton(label='Show Line Number', variable=self.show_line_number,
                                  command=self.update_line_numbers)
        self.show_cursor_info = IntVar()
        self.show_cursor_info.set(1)
        view_menu.add_checkbutton(
            label='Show Cursor Location at Bottom', variable=self.show_cursor_info, command=self.show_cursor_info_bar)
        to_highlight_line = BooleanVar()
        view_menu.add_checkbutton(label='Highlight Current Line', onvalue=1,
                                  offvalue=0, variable=to_highlight_line, command=self.toggle_highlight)
        themes_menu = Menu(menu_bar, tearoff=0)
        view_menu.add_cascade(label='Themes', menu=themes_menu)

        theme_choice = StringVar()
        theme_choice.set('Default')
        for k in sorted(color_schemes):
            themes_menu.add_radiobutton(
                label=k, variable=theme_choice, command=self.change_theme)
        menu_bar.add_cascade(label='View', menu=view_menu)

        #-About Menu
        about_menu = Menu(menu_bar, tearoff=0)
        about_menu.add_command(label='About', command=self.display_about_messagebox)
        about_menu.add_command(label='Help', command=self.display_help_messagebox)
        menu_bar.add_cascade(label='About', menu=about_menu)
        self.config(menu=menu_bar)

        shortcut_bar = Frame(self, height=25)
        shortcut_bar.pack(expand='no', fill='x')

        icons = ('new_file', 'open_file', 'save', 'cut', 'copy', 'paste',
                 'undo', 'redo', 'find_text')

        for i, icon in enumerate(icons):
            tool_bar_icon = PhotoImage(file='icons/{}.gif'.format(icon))
            cmd = eval('self.' + icon)
            tool_bar = Button(shortcut_bar, image=tool_bar_icon, command=cmd)
            tool_bar.image = tool_bar_icon
            tool_bar.pack(side='left')

        # pane
        pane = tk.PanedWindow(self, orient='vertical', sashwidth=4)
        pane.pack(expand=True, fill=tk.BOTH)
        
        #Frame inside Top Pane
        top_frame = Frame(pane)
        #top_frame.pack(expand=True, fill=tk.BOTH)
        pane.add(top_frame)

        content_font = tkfont.Font(family="consolas", size=10)

        self.line_number_bar = Text(top_frame, width=4, padx=3, takefocus=0, border=0,
                               background='khaki', state='disabled', wrap='none')

        self.line_number_bar.configure(font=content_font)

        self.line_number_bar.pack(side='left', fill='y')

        self.content_text = content_text = Text(top_frame, font=content_font, wrap='word', undo=1)
        content_text.pack(expand='yes', fill='both')
        self.scroll_bar = scroll_bar = Scrollbar(content_text)
        # content_text.configure(yscrollcommand=scroll_bar.set)
        # self.line_number_bar.configure(yscrollcommand=scroll_bar.set)
        # content_text.configure(yscrollcommand=lambda f, l: autoscroll(scroll_bar, f, l))
        # self.line_number_bar.configure(yscrollcommand=lambda f, l: autoscroll(scroll_bar, f, l))
        content_text.configure(yscrollcommand=self.autoscroll)
        # self.line_number_bar.configure(yscrollcommand=self.autoscroll)

        scroll_bar.configure(command=self.on_content_scroll)
        scroll_bar.pack(side='right', fill='y')
        
        self.cursor_info_bar = Label(content_text, text='Line: 1 | Column: 1')
        self.cursor_info_bar.pack(expand='no', fill=None, side='right', anchor='se')

        content_text.bind('<KeyPress-F1>', self.display_help_messagebox)
        content_text.bind('<Control-N>', self.new_file)
        content_text.bind('<Control-n>', self.new_file)
        content_text.bind('<Control-O>', self.open_file)
        content_text.bind('<Control-o>', self.open_file)
        content_text.bind('<Control-S>', self.save)
        content_text.bind('<Control-s>', self.save)
        content_text.bind('<Control-f>', self.find_text)
        content_text.bind('<Control-F>', self.find_text)
        content_text.bind('<Control-A>', self.select_all)
        content_text.bind('<Control-a>', self.select_all)
        content_text.bind('<Control-y>', self.redo)
        content_text.bind('<Control-Y>', self.redo)
        content_text.bind('<Any-KeyPress>', self.on_content_changed)
        content_text.tag_configure('active_line', background='ivory2')

        # set up the pop-up menu
        popup_menu = Menu(content_text)
        for i in ('cut', 'copy', 'paste', 'undo', 'redo'):
            cmd = eval('self.' + i)
            popup_menu.add_command(label=i, compound='left', command=cmd)
        popup_menu.add_separator()
        popup_menu.add_command(label='Select All', underline=7, command=self.select_all)
        content_text.bind('<Button-3>', self.show_popup_menu)

        # bind right mouse click to show pop up and set focus to text widget on launch
        content_text.bind('<Button-3>', self.show_popup_menu)
        content_text.focus_set()

        # output Window
        self.output_text = output_text = OutputText(pane, wrap='word', undo=1)
        sys.stdout = output_text
        #output_text.pack(expand='yes', fill='both')
        pane.add(output_text)

### From here: WIS added for Syntax Highlighting

        self.per = per = Percolator(content_text)
        # initialized below in self.ResetColorizer
        self.color = None
        self.reset_colorizer()

### End here: WIS added for Syntax Highlighting

        #self.content_text.bind("<MouseWheel>", self.on_mouse_scroll)


    def on_mouse_scroll(self, event):
        if event.delta > 0:
            self.on_content_scroll("scroll", "-3", "units")
        else:
            self.on_content_scroll("scroll", "3", "units")

    def autoscroll(self, first, last):
        """Hide and show scrollbar as needed."""
        first, last = float(first), float(last)
        # if first <= 0 and last >= 1:
        #     sbar.remove()
        # else:
        #     sbar.pack()
        #print(first, last)
        self.scroll_bar.set(first, last)
        self.line_number_bar.yview('moveto', first)

        # show pop-up menu
    def on_content_scroll(self, *args):
        #print(params)
        self.content_text.yview(*args)
        self.line_number_bar.yview(*args)

    def show_popup_menu(self, event):
        self.popup_menu.tk_popup(event.x_root, event.y_root)

    def show_cursor_info_bar(self):
        show_cursor_info_checked = self.show_cursor_info.get()
        if show_cursor_info_checked:
            self.cursor_info_bar.pack(expand='no', fill=None, side='right', anchor='se')
        else:
            self.cursor_info_bar.pack_forget()

    def update_cursor_info_bar(self, event=None):
        row, col = self.content_text.index(tk.INSERT).split('.')
        line_num, col_num = str(int(row)), str(int(col) + 1)  # col starts at 0
        infotext = "Line: {0} | Column: {1}".format(line_num, col_num)
        self.cursor_info_bar.config(text=infotext)

    def change_theme(self, event=None):
        selected_theme = self.theme_choice.get()
        fg_bg_colors = color_schemes.get(selected_theme)
        foreground_color, background_color = fg_bg_colors.split('.')
        self.content_text.config(
            background=background_color, fg=foreground_color)

    def update_line_numbers(self, event=None):
        line_numbers = self.get_line_numbers()
        self.line_number_bar.config(state='normal')
        self.line_number_bar.delete('1.0', 'end')
        self.line_number_bar.insert('1.0', line_numbers)
        self.line_number_bar.config(state='disabled')

    def highlight_line(self, interval=100):
        self.content_text.tag_remove("active_line", 1.0, "end")
        self.content_text.tag_add(
            "active_line", "insert linestart", "insert lineend+1c")
        self.content_text.after(interval, self.toggle_highlight)

    def undo_highlight(self):
        self.content_text.tag_remove("active_line", 1.0, "end")

    def toggle_highlight(self, event=None):
        if self.to_highlight_line.get():
            self.highlight_line()
        else:
            self.undo_highlight()

    def on_content_changed(self, event=None):
        self.update_line_numbers()
        self.update_cursor_info_bar()

    def get_line_numbers(self):
        output = ''
        if self.show_line_number.get():
            row, col = self.content_text.index("end").split('.')
            for i in range(1, int(row)):
                output += str(i) + '\n'
        return output

    def display_about_messagebox(self, event=None):
        tkinter.messagebox.showinfo(
            "About", "{}{}".format(PROGRAM_NAME, "\nTkinter GUI Application\n Development Blueprints"))

    def display_help_messagebox(self, event=None):
        tkinter.messagebox.showinfo(
            "Help", "Help Book: \nTkinter GUI Application\n Development Blueprints",
            icon='question')

    def exit_editor(self, event=None):
        if tkinter.messagebox.askokcancel("Quit?", "Really quit?"):
            self.destroy()

    def new_file(self, event=None):
        self.title("Untitled")
        global file_name
        file_name = None
        self.content_text.delete(1.0, tk.END)
        self.on_content_changed()

    def open_file(self, event=None):
        input_file_name = tk.filedialog.askopenfilename(defaultextension=".txt",
                                                             filetypes=[("All Files", "*.*"),
                                                                        ("Text Documents", "*.txt")])
        if input_file_name:
            global file_name
            file_name = input_file_name
            self.title('{} - {}'.format(os.path.basename(file_name), PROGRAM_NAME))
            self.content_text.delete(1.0, tk.END)
            with open(file_name, "r", encoding="utf-8-sig") as _file:
                self.content_text.insert(1.0, _file.read())
            self.on_content_changed()

    def write_to_file(self, file_name):
        try:
            content = self.content_text.get(1.0, 'end')
            with open(file_name, 'w') as the_file:
                the_file.write(content)
        except IOError:
            tkinter.messagebox.showwarning("Save", "Could not save the file.")

    def save_as(self, event=None):
        input_file_name = tkinter.filedialog.asksaveasfilename(defaultextension=".txt",
                                                               filetypes=[("All Files", "*.*"),
                                                                          ("Text Documents", "*.txt")])
        if input_file_name:
            global file_name
            file_name = input_file_name
            self.write_to_file(file_name)
            self.title('{} - {}'.format(os.path.basename(file_name), PROGRAM_NAME))
        return "break"

    def save(self, event=None):
        global file_name
        if not file_name:
            self.save_as()
        else:
            self.write_to_file(file_name)
        return "break"

    def select_all(self, event=None):
        self.content_text.tag_add('sel', '1.0', 'end')
        return "break"

    def find_text(self, event=None):
        search_toplevel = Toplevel(self)
        search_toplevel.title('Find Text')
        search_toplevel.transient(self)

        Label(search_toplevel, text="Find All:").grid(row=0, column=0, sticky='e')

        search_entry_widget = Entry(
            search_toplevel, width=25)
        search_entry_widget.grid(row=0, column=1, padx=2, pady=2, sticky='we')
        search_entry_widget.focus_set()
        ignore_case_value = IntVar()
        Checkbutton(search_toplevel, text='Ignore Case', variable=ignore_case_value).grid(
            row=1, column=1, sticky='e', padx=2, pady=2)
        Button(search_toplevel, text="Find All", underline=0,
               command=lambda: self.search_output(
                   search_entry_widget.get(), ignore_case_value.get(),
                   self.content_text, search_toplevel, search_entry_widget)
               ).grid(row=0, column=2, sticky='e' + 'w', padx=2, pady=2)

    def close_search_window(self):
        self.content_text.tag_remove('match', '1.0', tk.END)
        self.search_toplevel.destroy()

        self.search_toplevel.protocol('WM_DELETE_WINDOW', self.close_search_window)
        return "break"

    def search_output(self, needle, if_ignore_case, content_text,
                      search_toplevel, search_box):
        content_text.tag_remove('match', '1.0', tk.END)
        matches_found = 0
        if needle:
            start_pos = '1.0'
            while True:
                start_pos = content_text.search(needle, start_pos,
                                                nocase=if_ignore_case, stopindex=tk.END)
                if not start_pos:
                    break
                end_pos = '{}+{}c'.format(start_pos, len(needle))
                content_text.tag_add('match', start_pos, end_pos)
                matches_found += 1
                start_pos = end_pos
            content_text.tag_config(
                'match', foreground='red', background='yellow')
        search_box.focus_set()
        search_toplevel.title('{} matches found'.format(matches_found))

    def cut(self):
        self.content_text.event_generate("<<Cut>>")
        self.on_content_changed()
        return "break"

    def copy(self):
        self.content_text.event_generate("<<Copy>>")
        return "break"

    def paste(self):
        self.content_text.event_generate("<<Paste>>")
        self.on_content_changed()
        return "break"

    def undo(self):
        self.content_text.event_generate("<<Undo>>")
        self.on_content_changed()
        return "break"

    def redo(self, event=None):
        self.content_text.event_generate("<<Redo>>")
        self.on_content_changed()
        return 'break'
        
    def run(self, event=None):
        from gunxpace import fxpsys
        content = self.content_text.get(1.0, 'end')
        #code = compile(content, '<string>', 'exec')
        #print(id(globals()))
        #exec(code, globals())
        fxpsys.run_script(content)
        self.open_analyzer()
        return 'break'

    def open_analyzer(self):
        analyzer = Toplevel(self)
        Analyzer.AnalyzerWindow(analyzer)

        #Analyzer.main()

class OutputText(Text):

    # Act as output file

    def write(self, s, tags=(), mark="insert"):
        if isinstance(s, (bytes, bytes)):
            s = s.decode("utf-8-sig", "replace")
        self.insert(mark, s, tags)
        self.see(mark)
        self.update()
        return len(s)

    def writelines(self, lines):
        for line in lines:
            self.write(line)

    def flush(self):
        pass



if __name__ == "__main__":
    #tkroot = Tk()    
    
    root = MainWindow()
    #root.geometry('350x350')
    root.title(PROGRAM_NAME)

    root.protocol('WM_DELETE_WINDOW', root.exit_editor)
    root.mainloop()