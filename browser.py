#!/usr/bin/python

import os
import sys
import time
import gtk
import gobject
import webkit

import webbrowser

from tablabel import TabLabel

VERSION = "0.1"

ABOUT_PAGE="""<html>
 <head>
   <title>SilverLining - the cloud browser</title>
 </head>
 <body>
 Welcome to SilverLining version %s
 </body>
</html>""" % VERSION

# http://webkitgtk.org/reference/webkitgtk-webkitwebview.html
class Browser(webkit.WebView):

    def __init__(self):
        super(Browser, self).__init__()

class NotebookPage(gobject.GObject):
    __gsignals__ = {
        "close": (gobject.SIGNAL_RUN_FIRST,
                  gobject.TYPE_NONE,
                  ()),
        "status": (gobject.SIGNAL_RUN_FIRST,
                  gobject.TYPE_NONE,
                  ()),
        "title": (gobject.SIGNAL_RUN_FIRST,
                  gobject.TYPE_NONE,
                  ())
        }

    def __init__(self, url, title="new"):
        super(NotebookPage, self).__init__()

        self.hover = None

        self.browser = Browser()
        self.browser.connect("load-finished", self.load_finished)
        self.browser.connect("hovering-over-link", self.hovering_over_link)
        self.browser.connect("title-changed", self.handle_title_changed)
        self.browser.connect_after("populate-popup", self.populate_popup)
        self.open(url)

        self.win = gtk.ScrolledWindow()
        self.win.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        self.win.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        self.win.add(self.browser)
        self.win.show_all()

        self.label = TabLabel(title)
        self.label.connect("close", self.close)
        self.status = ""
        self.title = ""
        self.hover = None

    def add_to_notebook(self, notebook):
        return notebook.append_page(self.win, self.label)

    def close(self, widget):
        self.emit("close")

    def show(self):
        self.win.show_all()
        self.label.show_all()

    def destroy(self):
        self.win.destroy()
        self.label.destroy()

    show_all = show

    def grab_focus(self):
        self.browser.grab_focus()

    def open(self, url):
        if url == "about:blank":
            self.browser.load_string(ABOUT_PAGE, "text/html", "utf-8", "about")
        else:
            self.browser.open(url)

    def back(self):
        self.browser.go_back()

    def forward(self):
        self.browser.go_forward()

    def reload(self):
        self.browser.reload()
    ## handlers

    def load_finished(self, widget, frame, *a, **b):
        self.title = frame.get_title() or frame.get_uri() or ""
        self.label.text = self.title 
        self.emit("title")

    def hovering_over_link(self, view, title, uri):
        self.status = uri or ""
        self.hover = uri
        self.emit("status")

    def handle_title_changed(self, view, frame, title):
        self.title = title
        self.emit("title")

    def populate_popup(self, view, menu):
        open_in_browser = gtk.MenuItem("Open in default browser")
        open_in_browser.connect('activate', self.open_in_browser)
        menu.append(open_in_browser)
        menu.show_all()
        return False

    def open_in_browser(self, menu_item):
        if self.hover:
            webbrowser.open(self.hover)

class Session(gtk.Notebook):
    def __init__(self):
        super(Session, self).__init__()
        self.set_tab_pos(gtk.POS_TOP)
        self.show()
        self.tabs = {}
        gobject.io_add_watch(sys.stdin, gobject.IO_IN, self.handle_stdin)

        self.connect("switch-page", self.handle_switch_page)

    def add_tab(self, url, title):
        p = NotebookPage(url, title)
        index = p.add_to_notebook(self)
        self.tabs[index] = p

        p.show()
        p.connect("close", self.close_tab)
        p.connect("status", self.handle_status)
        p.connect("title", self.handle_title)
        p.grab_focus()
        p.browser.connect("create-web-view", self.new_window)
        return p.browser

    def current(self):
        return self.tabs[self.get_current_page()]

    def new_window(self, webview, webframe):
        return self.add_tab("", "new")

    def close_tab(self, tab):
        num = self.page_num(tab.win)
        self.remove_page(num)
        tab.destroy()

        ## if all tabs are closed, report cleanup to parent process

    def handle_switch_page(self, widget, page, num):
        if num in self.tabs:
            p = self.tabs[num]
            self.send("title " + p.title)

    def handle_status(self, tab):
        self.send("status " + tab.status)

    def handle_title(self, tab):
        if tab == self.current():
            self.send("title " + tab.title)

    def handle_stdin(self, source, condition):
        size = int(source.readline())
        data = source.read(size)

        if ' ' in data:
            cmd, rest = data.split(" ", 1)
        else:
            cmd, rest = data.strip(), ''
        if cmd == "new":
            self.add_tab(rest.strip(), rest.strip())
        elif cmd == "open":
            self.current().open(rest.strip())
        elif cmd == "back":
            self.current().back()
        elif cmd == "forward":
            self.current().forward()
        elif cmd == "reload":
            self.current().reload()
        elif cmd == "debug":
            import pdb
            pdb.Pdb(stdin=getattr(sys,'__stdin__'),stdout=getattr(sys,'__stderr__')).set_trace(sys._getframe().f_back)

        return True

    def send(self, msg):
        sys.stdout.write("%s\n%s" % (len(msg), msg))
        sys.stdout.flush()

if __name__ == '__main__':
    gobject.threads_init()
    Wid = int(sys.argv[1])
    url = sys.argv[2]
    label = sys.argv[2]
    s = Session()
    s.add_tab(url, label)

    plug = gtk.Plug(Wid)
    plug.add(s)
    plug.show_all()

    gtk.main()
