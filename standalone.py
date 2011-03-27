from browser import Session
import gobject
import pygtk
pygtk.require('2.0')
import gtk,sys

gobject.threads_init()
window = gtk.Window()
window.show()

s = Session()
window.add(s)

s.add_tab("http://docs.google.com", "docs")
s.show()

gtk.main()
