import os
import sys
import time

import gobject
import gtk  
import gtk.glade  

import subprocess

from tablabel import TabLabel

class SessionTab(gobject.GObject):
    PROCNAME = "browser.py"

    __gsignals__ = {
        "close": (gobject.SIGNAL_RUN_FIRST,
                  gobject.TYPE_NONE,
                  ()),
        "status":(gobject.SIGNAL_RUN_FIRST,
                  gobject.TYPE_NONE,
                  ()),
        "title":(gobject.SIGNAL_RUN_FIRST,
                  gobject.TYPE_NONE,
                  ()),
        "location":(gobject.SIGNAL_RUN_FIRST,
                  gobject.TYPE_NONE,
                  ())
        }

    def __init__(self, url, title="new"):
        super(SessionTab, self).__init__()
        self.socket = gtk.Socket()
        self.socket.connect("plug-removed", self.close)

        self.label = TabLabel(title)
        self.label.connect("close", self.close)
        self.proc = None
        self.source_id = None
        self.status = ""
        self.title = ""
        self.location = url

        self.wid = -1
        self.close_emitted = False

    @property
    def child(self):
        return self.socket

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
        notebook.append_page(self.socket, self.label)
        notebook.set_tab_reorderable(self.socket, True)
        notebook.set_tab_detachable(self.socket, True)
        return notebook.page_num(self.socket)

    def start(self, url, title):
        basedir = os.path.dirname(__file__)
        sessionproc = os.path.join(basedir, self.PROCNAME)
        cmd = [sys.executable, sessionproc,  str(self.wid), url, title]
        self.proc = subprocess.Popen(cmd,
               stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        ## force non-blocking
        ## import fcntl
        ## fl = fcntl.fcntl(self.proc.stdout, fcntl.F_GETFL)
        ## fcntl.fcntl(self.proc.stdout, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        self.source_id = gobject.io_add_watch(self.proc.stdout, gobject.IO_IN, self.handle_child)
        gobject.io_add_watch(self.proc.stdout, gobject.IO_HUP|gobject.IO_ERR, self.handle_child_closed)
        gobject.io_add_watch(self.proc.stdin, gobject.IO_HUP|gobject.IO_ERR, self.handle_child_closed)

    def close(self, *args):
        if not self.close_emitted:
            self.close_emitted = True
            self.emit("close")

    def send(self, cmd):
        self.proc.stdin.write("%s\n%s" % (len(cmd), cmd))
        self.proc.stdin.flush()

    def handle_child_closed(self, source, condition):
        print "Error on", self, "closing..."
        self.close()
        return False

    def handle_child(self, source, condition):
        """ the child wrote something to stdout """
        #print "handle_child", source, condition
        data = source.readline()
        if not data:
            print "No data from", self, "closing..."
            self.close()
            return False

        try:
            s = int(data)
        except ValueError, e:
            #print "Noise"
            return True

        data = source.read(s)
        if " " in data:
            cmd, rest = data.split(" ", 1)
        else:
            cmd, rest = data, ""
        if cmd == "status":
            self.status = rest
            self.emit("status")
        elif cmd == "title":
            self.title = rest
            self.emit("title")
        elif cmd == "location":
            self.location = rest
            self.emit("location")

        print "CHILD wrote", data
        return True

class SilverLining(object):
    apps = (("new..", ("about:blank")),
            ("gmail", "http://mail.google.com"),
            ("google docs", "http://docs.google.com"),
            ("twitter", "http://www.twitter.com"),
            ("android market", "http://market.android.com/publish"))
    
    def __init__(self):
        self.tree = gtk.Builder()
        self.tree.add_from_file("silverlining.glade")
        self.window = self.tree.get_object("window")
        self.notebook = self.tree.get_object("notebook1")
        self.menu = self.tree.get_object("appmenu")
        for a in self.apps:
            item = gtk.MenuItem(a[0])
            self.menu.append(item)
            item.connect("activate", self.app_selected, a)

        self.back = self.tree.get_object("back")
        self.forward = self.tree.get_object("forward")
        self.reload = self.tree.get_object("reload")
        self.new = self.tree.get_object("new")
        self.location = self.tree.get_object("location")
        self.status = self.tree.get_object("status")

        self.back.connect("clicked", self.handle_back)
        self.forward.connect("clicked", self.handle_forward)
        self.reload.connect("clicked", self.handle_reload)
        self.new.connect("clicked", self.handle_new)
        self.location.connect("activate", self.handle_location)
        self.notebook.connect("switch-page", self.handle_switch_page)

        self.window.connect("destroy", gtk.main_quit)

        self.window.show_all()
        self.tabs = {}

    def add_tab(self, app):
        tab = SessionTab(app[1], app[0])
        ## this will invoke a page switch event, which depends on self.tabs,
        ## so order is important
        self.tabs[tab.child] = tab
        index = tab.add_to_notebook(self.notebook)

        tab.connect("close", self.close)
        tab.connect("status", self.handle_session_status)
        tab.connect("title", self.handle_session_title)
        tab.connect("location", self.handle_session_location)

        tab.show_all()
        tab.start(app[1], app[0])
        self.notebook.set_current_page(index)
        self.update_status(tab)

    def current(self):
        return self.tabs[self.notebook.get_nth_page(self.notebook.get_current_page())]

    def update_status(self, tab):
        """ find the active tab and update the UI status widgets """
        self.status.set_text(tab.status)
        self.window.set_title("SilverLining: " + tab.title)
        self.location.set_text(tab.location)

    ## local handlers
    def handle_switch_page(self, widget, page, num):
        child = self.notebook.get_nth_page(num)
        self.update_status(self.tabs[child])

    def handle_back(self, widget):
        self.current().send("back")

    def handle_forward(self, widget):
        self.current().send("forward")

    def handle_reload(self, widget):
        self.current().send("reload")

    def handle_location(self, widget):
        url = self.location.get_text().strip()
        if not url:
            return
        if not url.startswith("http:"):
            url = "http://" + url
        self.location.set_text(url)
        self.current().send("open " + url)

    def handle_new(self, widget):
        self.current().send("new about:blank")

    def app_selected(self, widget, app):
        self.add_tab(app)
    
    def close(self, tab):
        num = self.notebook.page_num(tab.socket)
        self.notebook.remove_page(num)
        tab.destroy()
        self.update_status(self.current())
        print "COSE", tab, self.current()

    ## session handlers
    def handle_session_status(self, tab):
        if tab == self.current():
            self.status.set_text(tab.status)

    def handle_session_title(self, tab):
        if tab == self.current():
            self.window.set_title("SilverLining: " + tab.title)

    def handle_session_location(self, tab):
        if tab == self.current():
            self.location.set_text(tab.location)

if __name__ == '__main__':
    sl = SilverLining()
    sl.add_tab(("New..", "about:blank"))
    gtk.main()
    
