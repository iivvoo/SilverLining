#!/usr/bin/python

import os
import sys
import time
import gtk
import gobject
import webkit

from tablabel import TabLabel

class Browser(webkit.WebView):

    def __init__(self):
        super(Browser, self).__init__()

class NotebookPage(gobject.GObject):
    __gsignals__ = {
        "close": (gobject.SIGNAL_RUN_FIRST,
                  gobject.TYPE_NONE,
                  ())
        }

    def __init__(self, url, title="new"):
        super(NotebookPage, self).__init__()
        self.browser = Browser()
        self.browser.open(url)
        self.browser.connect("load-finished", self.load_finished)

        self.label = TabLabel(title)
        self.label.connect("close", self.close)

    def add_to_notebook(self, notebook):
        notebook.append_page(self.browser, self.label)

    def close(self, widget):
        self.emit("close")

    def load_finished(self, widget, frame, *a, **b):
        title = frame.get_title() or frame.get_uri() or ""
        self.label.text = title 

    def show(self):
        self.browser.show_all()
        self.label.show_all()

    def destroy(self):
        self.browser.destroy()
        self.label.destroy()

    show_all = show

    def grab_focus(self):
        self.browser.grab_focus()

class Session(gtk.Notebook):
    def __init__(self):
        super(Session, self).__init__()
        self.set_tab_pos(gtk.POS_TOP)
        self.show()

    def add_tab(self, url, title):
        p = NotebookPage(url, title)
        p.add_to_notebook(self)
        p.show()
        p.connect("close", self.close_tab)
        p.grab_focus()
        p.browser.connect("create-web-view", self.new_window)
        return p.browser

    def new_window(self, webview, webframe):
        return self.add_tab("", "new")

    def close_tab(self, tab):
        num = self.page_num(tab.browser)
        self.remove_page(num)
        tab.destroy()

        ## if all tabs are closed, report cleanup to parent process

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
