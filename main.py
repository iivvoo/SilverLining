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
        self.proc = None
        self.source_id = None

        self.wid = -1

    def show(self):
        self.socket.show()
        self.label.show_all()
        self.wid = self.socket.get_id()

    show_all = show

    def destroy(self):
        if self.source_id is not None:
            gobject.source_remove(self.source_id)
        self.proc.kill()
        self.socket.destroy()
        self.label.destroy()

    def add_to_notebook(self, notebook):
        return notebook.append_page(self.socket, self.label)

    def start(self, url, title):
        basedir = os.path.dirname(__file__)
        sessionproc = os.path.join(basedir, self.PROCNAME)
        cmd = [sys.executable, sessionproc,  str(self.wid), url, title]
        self.proc = subprocess.Popen(cmd,
               stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        self.source_id = gobject.io_add_watch(self.proc.stdout, gobject.IO_IN, self.handle_child)

    def close(self, label):
        self.emit("close")

    def send(self, cmd):
        self.proc.stdin.write("%s\n%s" % (len(cmd), cmd))
        self.proc.stdin.flush()

    def handle_child(self, source, condition):
        """ the child wrote something to stdout """
        print "handle_child", source, condition
        try:
            s = int(source.readline())
        except ValueError, e:
            print "Noise"
            return

        data = source.read(s)
        ##
        ## Types of commands:
        ## CURRENT <url> - url for currently selected tab (to show in location)
        ## HOVER <url> - url for currently selected item
        ## TITLE <title> - title update for current tab
        print "CHILD wrote", data
        return True

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

        self.back = self.tree.get_object("back")
        self.forward = self.tree.get_object("forward")
        self.reload = self.tree.get_object("reload")
        self.location = self.tree.get_object("location")

        self.back.connect("clicked", self.handle_back)
        self.forward.connect("clicked", self.handle_forward)
        self.reload.connect("clicked", self.handle_reload)
        self.location.connect("activate", self.handle_location)

        self.window.connect("destroy", gtk.main_quit)

        self.window.show_all()
        self.tabs = {}

    def add_tab(self, app):
        tab = SessionTab(app[1], app[0])
        index = tab.add_to_notebook(self.notebook)
        self.tabs[index] = tab

        tab.connect("close", self.close)
        tab.show_all()
        tab.start(app[1], app[0])

    def current(self):
        return self.tabs[self.notebook.get_current_page()]

    ## handlers
    def handle_back(self, widget):
        self.current().send("back")

    def handle_forward(self, widget):
        self.current().send("forward")

    def handle_reload(self, widget):
        self.current().send("reload")

    def handle_location(self, widget):
        self.current().send("open " + self.location.get_text())

    def app_selected(self, widget, app):
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
    
