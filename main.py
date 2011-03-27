import os
import sys
import time

import gobject
import pygtk  
import gtk  
import gtk.glade  

import subprocess

from browser import Browser
from tablabel import TabLabel

class SessionTab(gobject.GObject):
    PROCNAME = "browser.py"

    __gsignals__ = {
        "close": (gobject.SIGNAL_RUN_FIRST,
                  gobject.TYPE_NONE,
                  ())
        }

    def __init__(self, url, title="new"):
        super(SessionTab, self).__init__()
        self.socket = gtk.Socket()
        self.label = TabLabel(title)
        self.label.connect("close", self.close)

        self.wid = -1

    def show(self):
        self.socket.show()
        self.label.show_all()
        self.wid = self.socket.get_id()

    show_all = show

    def destroy(self):
        self.socket.destroy()
        self.label.destroy()

    def add_to_notebook(self, notebook):
        notebook.append_page(self.socket, self.label)

    def start(self, url, title):
        basedir = os.path.dirname(__file__)
        sessionproc = os.path.join(basedir, self.PROCNAME)
        cmd = [sys.executable, sessionproc,  str(self.wid), url, title]
        proc = subprocess.Popen(cmd,
               stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def close(self, label):
        self.emit("close")

class SilverLining(object):
    apps = (("gmail", "http://mail.google.com"),
            ("google docs", "http://docs.google.com"),
            ("twitter", "http://www.twitter.com"),
            ("android market", "http://market.android.com/publish"))
    
    def __init__(self):
        self.tree = gtk.Builder()
        self.tree.add_from_file("silverlining.glade")
        self.window = self.tree.get_object("window1")
        self.notebook = self.tree.get_object("notebook1")
        self.menu = self.tree.get_object("appmenu")
        for a in self.apps:
            item = gtk.MenuItem(a[0])
            self.menu.append(item)
            item.connect("activate", self.app_selected, a)

        self.window.connect("destroy", gtk.main_quit)

        self.browsers = []
        self.window.show_all()

    def add_tab(self, app):
        tab = SessionTab(app[1], app[0])
        tab.add_to_notebook(self.notebook)
        tab.connect("close", self.close)
        tab.show_all()
        tab.start(app[1], app[0])

    def app_selected(self, widget, app):
        print "SELECT", app
        self.add_tab(app)
    
    def close(self, tab):
        num = self.notebook.page_num(tab.socket)
        self.notebook.remove_page(num)
        tab.destroy()

if __name__ == '__main__':
    sl = SilverLining()
    sl.add_tab(sl.apps[0])
    sl.add_tab(sl.apps[0])
    gtk.main()
    
