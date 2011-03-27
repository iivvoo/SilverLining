import os
import time

import pygtk  
import gtk  
import gtk.glade  

from browser import Browser

class Visel(object):
    apps = (("gmail", "http://mail.google.com"),
            ("google docs", "http://docs.google.com"),
            ("twitter", "http://www.twitter.com"),
            ("android market", "http://market.android.com/publish"))
    
    def __init__(self):
        self.tree = gtk.Builder()
        self.tree.add_from_file("visel.glade")
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
        socket = gtk.Socket()
        self.notebook.append_page(socket, gtk.Label(app[0]))
        socket.show()
        Wid = socket.get_id()
        print "WID", Wid


        # self.browsers.append(b)
        # b.widget.show()

        cmd = ["/usr/bin/python", "/home/ivo/m3r/projects/Visel/browser.py", str(Wid), app[1], app[0]]
        import subprocess
        proc = subprocess.Popen(cmd,
               stdin=subprocess.PIPE, stdout=subprocess.PIPE)# , cwd="/home/ivo/m3r/projects/Visel")

    def app_selected(self, widget, app):
        print "SELECT", app
        self.add_tab(app)
    
v = Visel()
#v.add_tab(v.apps[0])
#v.add_tab(v.apps[0])
gtk.main()

