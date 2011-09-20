import gtk
import os

class UILoader(object):
    def __init__(self):
        self.tree = gtk.Builder()
        gladefile = os.path.join(os.path.dirname(__file__), 'silverlining.glade')
        self.tree.add_from_file(gladefile)

    def __call__(self, id):
        return self.tree.get_object(id)

loader = UILoader() ## make singleton
