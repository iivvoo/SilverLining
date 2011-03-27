#!/usr/bin/python

import os
import sys
import time
import gtk
import gobject
import webkit

class Browser(webkit.WebView):
    def __init__(self):
        super(Browser, self).__init__()


class Session(gtk.Notebook):
    def __init__(self):
        super(Session, self).__init__()
        self.set_tab_pos(gtk.POS_TOP)
        self.show()

    def add_tab(self, url, label):
        #moz = gtkmozembed.MozEmbed()
        #moz.connect("new-window", self.new_window)
        #moz.load_url(url)
        #self.append_page(moz, gtk.Label(label))
        #moz.show()
        #moz.grab_focus()
        #return moz
        b = Browser()
        b.open(url)
        self.append_page(b, gtk.Label(label))
        b.show()
        b.grab_focus()
        b.connect("create-web-view", self.new_window)
        return b

    def new_window(self, webview, webframe):
        print "new_window", webview, webframe
        return self.add_tab("", "new")


def mkprofile():
    if not os.path.exists("/tmp/visel"):
        os.mkdir("/tmp/visel")
    path = "/tmp/visel/profile%f" % time.time()
    os.mkdir(path)
    return path

if __name__ == '__main__':
    # gtkmozembed.set_profile_path(mkprofile(), "browser")
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
