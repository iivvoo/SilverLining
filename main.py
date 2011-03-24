import pygtk  
#pygtk.require("2.0")  
import gtk  
import gtk.glade  

from browser import Browser

tree = gtk.Builder()
tree.add_from_file("visel.glade")

moz1 = Browser()
moz2 = Browser()

window = tree.get_object("window1")
print "0"
notebook = tree.get_object("notebook1")

notebook.append_page(moz1.widget, gtk.Label("m3r.nl"))
notebook.append_page(moz2.widget, gtk.Label("gmail"))

moz1.load_url("http://mail.google.com/a/m3r.nl")
moz2.load_url("http://mail.google.com")
if window:
    window.connect("destroy", gtk.main_quit)

window.show_all()

gtk.main()

