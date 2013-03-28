# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Open/Save file dialog box

Customized dialog boxes derrived from the standard Tkinter
Dialog class.

Author -- James A. Mazer (james.mazer@yale.edu)

"""

"""Revision History

Wed Aug 14 13:05:27 2002 mazer

- made set_selection() method place cursor at the end of the line

"""


from Tkinter import *
from Dialog import Dialog

import os
import fnmatch
import string

dialogstates = {}

def _comparedatafiles(a, b):
    """Compare two datafile names for sorting

    Try to sort pype datafiles in descending order by file number..
    This is highly PYPE-SPECIFIC and is activated by passing keyword
    argument datafiles=1 to the Open() and SaveAs() functions below

    Pype data file names are of the form::

      <animal_id><cell_number>.<taskname><taskversion>.<filenumber>

    eg, m0037.hmap7.002, where,

    - animal is "m"

    - task was hmap (version 7)

    - and this is the 3rd (0,1,2) datafile collected for cell m0037

    """
    try:
        if int(string.split(a, '.')[2]) > int(string.split(b, '.')[2]):
            return -1
        else:
            return 1
    except (IndexError, ValueError):
        if a > b:
            return 1
        else:
            return -1
    except:
        # [[effort to remove all unnamed exceptions:
        import pypedebug
        pypedebug.get_traceback(1)
        # effort to remove all unnamed exceptions:]]
        if a > b:
            return 1
        else:
            return -1

class FileDialog(object):

    """Standard file selection dialog -- no checks on selected file.

    Usage:

        d = FileDialog(master)
        file = d.go(initialdir, pattern, initialfile, key)
        if file is None: ...canceled...
        else: ...open file...

    All arguments to go() are optional.

    The 'key' argument specifies a key in the global dictionary
    'dialogstates', which keeps track of the values for the directory
    and pattern arguments, overriding the values passed in (it does
    not keep track of the initialfile argument!).  If no key is specified,
    the dialog keeps no memory of previous state.  Note that memory is
    kept even when the dialog is canceled.  (All this emulates the
    behavior of the Macintosh file selection dialogs.)

    """

    title = "File Selection"

    def __init__(self, master=None, title=None, sortfn=None):
        if title is None:
            title = self.title
        self.master = master
        self.directory = None
        self.mode = None
        self.sortfn = sortfn

        self.top = Toplevel(master)
        self.top.title(title)
        self.top.iconname(title)

        self.botframe = Frame(self.top)
        self.botframe.pack(side=BOTTOM, fill=X)

        # this one's the actual filename box..
        self.selection = Entry(self.top, fg='red')
        self.selection.pack(side=BOTTOM, fill=X)
        self.selection.bind('<Return>', self.ok_event)

        # directory/pattern box
        self.filter = Entry(self.top)
        self.filter.pack(side=TOP, fill=X)
        self.filter.bind('<Return>', self.filter_command)

        self.midframe = Frame(self.top)
        self.midframe.pack(expand=YES, fill=BOTH)

        self.filesbar = Scrollbar(self.midframe)
        self.filesbar.pack(side=RIGHT, fill=Y)
        self.files = Listbox(self.midframe, exportselection=0,
                             yscrollcommand=(self.filesbar, 'set'))
        self.files.pack(side=RIGHT, expand=YES, fill=BOTH)
        btags = self.files.bindtags()
        self.files.bindtags(btags[1:] + btags[:1])
        self.files.bind('<ButtonRelease-1>', self.files_select_event)
        self.files.bind('<Double-ButtonRelease-1>', self.files_double_event)
        self.filesbar.config(command=(self.files, 'yview'))

        self.dirsbar = Scrollbar(self.midframe)
        self.dirsbar.pack(side=LEFT, fill=Y)
        self.dirs = Listbox(self.midframe, exportselection=0,
                            yscrollcommand=(self.dirsbar, 'set'))
        self.dirs.pack(side=LEFT, expand=YES, fill=BOTH)
        self.dirsbar.config(command=(self.dirs, 'yview'))
        btags = self.dirs.bindtags()
        self.dirs.bindtags(btags[1:] + btags[:1])
        self.dirs.bind('<ButtonRelease-1>', self.dirs_select_event)
        self.dirs.bind('<Double-ButtonRelease-1>', self.dirs_double_event)

        self.ok_button = Button(self.botframe,
                                 text="OK",
                                 command=self.ok_command)
        self.ok_button.pack(side=LEFT)
        self.filter_button = Button(self.botframe,
                                    text="Filter",
                                    command=self.filter_command)
        self.filter_button.pack(side=LEFT, expand=YES)
        self.cancel_button = Button(self.botframe,
                                    text="Cancel",
                                    command=self.cancel_command)
        self.cancel_button.pack(side=RIGHT)

        self.top.protocol('WM_DELETE_WINDOW', self.cancel_command)
        # XXX Are the following okay for a general audience?
        self.top.bind('<Alt-w>', self.cancel_command)
        self.top.bind('<Alt-W>', self.cancel_command)

    def go(self, initialdir=os.curdir, pattern="*", initialfile="", key=None):
        if key and dialogstates.has_key(key):
            self.directory, pattern = dialogstates[key]
        else:
            initialdir = os.path.expanduser(initialdir)
            if os.path.isdir(initialdir):
                self.directory = initialdir
            else:
                self.directory, initialfile = os.path.split(initialdir)
        self.set_filter(self.directory, pattern)
        self.set_selection(initialfile)
        self.filter_command()
        self.selection.focus_set()
        self.top.grab_set()
        self.how = None
        self.top.mainloop()          # Exited by self.quit(how)
        if key:
            directory, pattern = self.get_filter()
            if self.how:
                directory = os.path.dirname(self.how)
            dialogstates[key] = directory, pattern
        self.top.destroy()
        return (self.how, self.mode)

    def quit(self, how=None):
        self.how = how
        self.top.quit()              # Exit mainloop()

    def dirs_double_event(self, event):
        self.filter_command()

    def dirs_select_event(self, event):
        dir, pat = self.get_filter()
        subdir = self.dirs.get('active')
        dir = os.path.normpath(os.path.join(self.directory, subdir))
        self.set_filter(dir, pat)

    def files_double_event(self, event):
        self.ok_command()

    def files_select_event(self, event):
        file = self.files.get('active')
        self.set_selection(file)

    def ok_event(self, event):
        self.ok_command()

    def ok_command(self):
        self.quit(self.get_selection())

    def filter_command(self, event=None):
        dir, pat = self.get_filter()
        try:
            names = os.listdir(dir)
        except os.error:
            self.top.bell()
            return
        self.directory = dir
        self.set_filter(dir, pat)
        if self.sortfn:
            names.sort(self.sortfn)
        else:
            names.sort()
        subdirs = [os.pardir]
        matchingfiles = []
        for name in names:
            fullname = os.path.join(dir, name)
            if os.path.isdir(fullname):
                subdirs.append(name)
            elif fnmatch.fnmatch(name, pat):
                matchingfiles.append(name)
        self.dirs.delete(0, END)
        for name in subdirs:
            self.dirs.insert(END, name)
        self.files.delete(0, END)
        for name in matchingfiles:
            self.files.insert(END, name)
        head, tail = os.path.split(self.get_selection())
        if tail == os.curdir: tail = ''
        self.set_selection(tail)

    def get_filter(self):
        filter = self.filter.get()
        filter = os.path.expanduser(filter)
        if filter[-1:] == os.sep or os.path.isdir(filter):
            filter = os.path.join(filter, "*")
        return os.path.split(filter)

    def get_selection(self):
        file = self.selection.get()
        file = os.path.expanduser(file)
        return file

    def cancel_command(self, event=None):
        self.quit()

    def set_filter(self, dir, pat):
        if not os.path.isabs(dir):
            try:
                pwd = os.getcwd()
            except os.error:
                pwd = None
            if pwd:
                dir = os.path.join(pwd, dir)
                dir = os.path.normpath(dir)
        self.filter.delete(0, END)
        self.filter.insert(END, os.path.join(dir or os.curdir, pat or "*"))

    def set_selection(self, file):
        self.selection.delete(0, END)
        self.selection.insert(END, os.path.join(self.directory, file))
        self.selection.icursor(END)
        self.selection.xview(END)


class LoadFileDialog(FileDialog):

    """File selection dialog which checks that the file exists."""

    title = "Load File ..."

    def ok_command(self):
        file = self.get_selection()
        if not os.path.isfile(file):
            self.top.bell()
        else:
            self.mode = 'r'
            self.quit(file)


class SaveFileDialog_noapp(FileDialog):

    """File selection dialog which checks that the file may be created."""

    title = "Save file as ..."

    def ok_command(self):
        file = self.get_selection()
        if os.path.exists(file):
            if os.path.isdir(file):
                self.top.bell()
                return
            d = Dialog(self.top,
                       title="File Exists",
                       text="Overwrite existing file %s?" % `file`,
                       bitmap='questhead',
                       default=1,
                       strings=("Yes", "Cancel"))
            if d.num != 0:
                return
        else:
            head, tail = os.path.split(file)
            if not os.path.isdir(head):
                self.top.bell()
                return
        self.mode = 'w'
        self.quit(file)


class SaveFileDialog(FileDialog):

    """File selection dialog which checks that the file may be created."""

    title = "Save file as ..."

    def ok_command(self):
        file = self.get_selection()
        if os.path.exists(file):
            if os.path.isdir(file):
                self.top.bell()
                return
            d = Dialog(self.top,
                       title="File Exists",
                       text="Overwrite existing file %s?" % `file`,
                       bitmap='questhead',
                       default=1,
                       strings=("Overwrite", "Append", "Cancel"))
            if d.num == 2:
                return
            elif d.num == 0:
                self.mode = 'w'
            elif d.num == 1:
                self.mode = 'a'
        else:
            head, tail = os.path.split(file)
            if not os.path.isdir(head):
                self.top.bell()
                return
            self.mode = 'w'
        self.quit(file)

def Open(initialdir=os.curdir, initialfile='', pattern='*',
         datafiles=None):
    if datafiles:
        sortfn = _comparedatafiles
    else:
        sortfn = None

    return LoadFileDialog(sortfn=sortfn).go(initialdir=initialdir,
                                            initialfile=initialfile,
                                            pattern=pattern)

def SaveAs(initialdir=os.curdir, initialfile='', pattern='*',
           append=1, datafiles=None):
    if datafiles:
        sortfn = _comparedatafiles
    else:
        sortfn = None

    if append:
        return SaveFileDialog(sortfn=sortfn).go(initialdir=initialdir,
                                                initialfile=initialfile,
                                                pattern=pattern)
    else:
        return SaveFileDialog_noapp(sortfn=sortfn).go(initialdir=initialdir,
                                                      initialfile=initialfile,
                                                      pattern=pattern)


if __name__ == '__main__':
    print Open(initialdir=sys.argv[1], pattern='*')
