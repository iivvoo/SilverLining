#!/usr/bin/python

import os
import sys
import time
import gtk
import gobject
import webkit

import webbrowser

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

        self.hover = None

        self.browser = Browser()
        self.browser.open(url)
        self.browser.connect("load-finished", self.load_finished)
        self.browser.connect("hovering-over-link", self.hovering_over_link)
        self.browser.connect_after("populate-popup", self.populate_popup)

        self.win = gtk.ScrolledWindow()
        self.win.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        self.win.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        self.win.add(self.browser)
        self.win.show_all()

        self.label = TabLabel(title)
        self.label.connect("close", self.close)

    def add_to_notebook(self, notebook):
        notebook.append_page(self.win, self.label)

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

    ## handlers

    def load_finished(self, widget, frame, *a, **b):
        title = frame.get_title() or frame.get_uri() or ""
        self.label.text = title 

    def hovering_over_link(self, view, title, uri):
        print "Hovering", uri
        self.hover = uri

    def populate_popup(self, view, menu):
        open_in_browser = gtk.MenuItem("Open in default browser")
        open_in_browser.connect('activate', self.open_in_browser)
        menu.append(open_in_browser)
        menu.show_all()
        return False

    def open_in_browser(self, menu_item):
        print "OIB", self.hover
        if self.hover:
            webbrowser.open(self.hover)

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
        num = self.page_num(tab.win)
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
