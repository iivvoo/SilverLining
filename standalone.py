#!/usr/bin/python

import sys
from browser import Session
import gobject
import pygtk
pygtk.require('2.0')
import gtk,sys

if __name__ == '__main__':
    if len(sys.argv) == 2:
        url = sys.argv[1]
    else:
        url = "http://docs.google.com"
    gobject.threads_init()
    window = gtk.Window()
    window.show()
    
    s = Session()
    window.add(s)
    
    s.add_tab(url, url)
    s.show()
    
    gtk.main()
