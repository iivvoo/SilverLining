#!/usr/bin/python

import os
import sys
import gtk
import gobject
import webkit
import urllib2

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

class FavCache(object):
    def __init__(self):
        self.cache = {}

    def get(self, uri):
        if uri not in self.cache:
            response = urllib2.urlopen(uri)
            loader = gtk.gdk.PixbufLoader()
            loader.write(response.read())
            loader.close()
            self.cache[uri] = loader.get_pixbuf()

        return self.cache[uri]

favcache = FavCache()

class Browser(webkit.WebView):
    # http://webkitgtk.org/reference/webkitgtk-webkitwebview.html
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
        self.throbbing = False

        self.label = TabLabel(title)
        self.label.connect("close", self.close)
        self.browser = Browser()
        self.browser.connect("load-started", self.load_started)
        self.browser.connect("load-finished", self.load_finished)
        self.browser.connect("hovering-over-link", self.hovering_over_link)
        self.browser.connect("title-changed", self.handle_title_changed)
        self.browser.connect("icon-loaded", self.handle_icon_loaded)
        self.browser.connect("download-requested", self.handle_download_requested)
        self.browser.connect_after("populate-popup", self.populate_popup)
        self.open(url)

        self.win = gtk.ScrolledWindow()
        self.win.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        self.win.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        self.win.add(self.browser)
        self.win.show_all()

        self.status = ""
        self.title = ""
        self.hover = None

    @property
    def child(self):
        return self.win

    @property
    def current_url(self):
        return self.browser.get_main_frame().get_uri() or ""

    def add_to_notebook(self, notebook):
        page = notebook.append_page(self.win, self.label)
        notebook.set_tab_reorderable(self.win, True)
        notebook.set_tab_detachable(self.win, True)
        return page

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

    def show_throbber(self):
        self.throbbing = True
        throbber = os.path.join(os.path.dirname(__file__), "throbber.gif")
        self.label.icon.set_from_file(throbber)

    def open(self, url):
        if url == "about:blank":
            self.browser.load_string(ABOUT_PAGE, "text/html", "utf-8", "about")
        else:
            self.browser.open(url)
        self.show_throbber()

    def back(self):
        self.browser.go_back()

    def forward(self):
        self.browser.go_forward()

    def reload(self):
        self.show_throbber()
        self.browser.reload()

    ## handlers

    def load_started(self, widget, frame, *a, **b):
        self.show_throbber()

    def load_finished(self, widget, frame, *a, **b):
        self.title = frame.get_title() or frame.get_uri() or ""
        self.label.text = self.title 
        self.emit("title")
        if self.throbbing:
            self.throbbing = False
            self.label.icon.set_from_stock(gtk.STOCK_ORIENTATION_PORTRAIT, gtk.ICON_SIZE_MENU)
            ## handle_icon_loaded may follow, setting the actual favicon
        ## widget.execute_script("alert('Hello')")

    def hovering_over_link(self, view, title, uri):
        self.status = uri or ""
        self.hover = uri
        self.emit("status")

    def handle_title_changed(self, view, frame, title):
        self.title = title
        self.emit("title")

    def handle_icon_loaded(self, view, uri, *a):
        ## This may block, which is bad!

        pixbuf = favcache.get(uri)
        self.label.icon.set_from_pixbuf(pixbuf)
        self.throbbing = False

    def handle_download_requested(self, widget, download, *a, **b):
        ## popup, etc XXX
        name = download.get_uri().rsplit('/')[-1]
        download.set_destination_uri("file:///tmp/" + name )
        return True

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
        self.set_scrollable(True)
        self.show()
        self.tabs = {}
        gobject.io_add_watch(sys.stdin, gobject.IO_IN|gobject.IO_ERR|gobject.IO_HUP, self.handle_stdin)
        gobject.io_add_watch(sys.stdout, gobject.IO_ERR|gobject.IO_HUP, self.handle_io_err)

        self.connect("switch-page", self.handle_switch_page)

        ## primitive logging, for now.
        if not os.path.exists("/tmp/sllog"):
            os.mkdir("/tmp/sllog")

        logfiles = os.listdir("/tmp/sllog")

        if logfiles:
            name = str(max([int(i) for i in logfiles]) + 1)
        else:
            name = "1"
        self._log = open("/tmp/sllog/" + name, "w")


    def add_tab(self, url, title):
        p = NotebookPage(url, title)
        ## order is important, add_to_notebook triggers tabswitch which
        ## depends on key being present in self.tabs
        self.tabs[p.child] = p
        index = p.add_to_notebook(self)

        p.show()
        p.connect("close", self.close_tab)
        p.connect("status", self.handle_status)
        p.connect("title", self.handle_title)
        p.grab_focus()
        p.browser.connect("create-web-view", self.new_window)
        self.set_current_page(index)
        return p.browser

    def current(self):
        return self.tabs[self.get_nth_page(self.get_current_page())]

    def update_status(self, tab):
        self.send("title " + tab.title)
        self.send("location " + tab.current_url)

    def new_window(self, webview, webframe):
        return self.add_tab("", "new")

    def close_tab(self, tab):
        num = self.page_num(tab.win)
        self.remove_page(num)
        tab.destroy()
        self.update_status(self.current())
        ## if all tabs are closed, report cleanup to parent process

    def handle_switch_page(self, widget, page, num):
        child = self.get_nth_page(num)
        p = self.tabs[child]
        self.update_status(p)

    def handle_status(self, tab):
        self.send("status " + tab.status)

    def handle_title(self, tab):
        if tab == self.current():
            self.send("title " + tab.title)

    def handle_io_err(self, source, condition):
        self.log("Error on %r: %d\n" % (source, condition))
        gtk.main_quit()
        return False

    def handle_stdin(self, source, condition):
        sizedata = source.readline()
        if not sizedata:
            self.log("Could not read from stdin\n")
            gtk.main_quit()
            return False

        size = int(sizedata)
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
        try:
            sys.stdout.write("%s\n%s" % (len(msg), msg))
            sys.stdout.flush()
        except IOError, e:
            self.log("IO Error out stdout: " + str(e) + "\n")
            sys.exit(0)

    def log(self, msg):
        self._log.write(msg + "\n")
        self._log.flush()

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
