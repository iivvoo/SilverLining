import gtk
import pango
import gobject

class TabLabel(gtk.HBox):
    __gsignals__ = {
        "close": (gobject.SIGNAL_RUN_FIRST,
                  gobject.TYPE_NONE,
                  ())
        }
    def __init__(self, title):
        super(TabLabel, self).__init__(homogeneous=False, spacing=4)
        self.title = title
        self.label = gtk.Label(title)
        self.label.props.max_width_chars = 30
        self.label.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        self.label.set_alignment(0.0, 0.5)

        close_img =  gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        close_button = gtk.Button()
        close_button.set_relief(gtk.RELIEF_NONE)
        close_button.connect("clicked", self.close_event)
        close_button.add(close_img)

        self.pack_start(self.label, expand=True, fill=True, padding=0)
        self.pack_start(close_button, expand=False, fill=False, padding=0)

    def set_text(self, text):
        self.label.set_label(text)

    def get_text(self):
        return self.label.get_label()

    text = property(get_text, set_text)

    def close_event(self, widget):
        self.emit("close")

