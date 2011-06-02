import gtk
import gobject
import webkit

class Inspector (gtk.Window):
    __gsignals__ = {
        "close": (gobject.SIGNAL_RUN_FIRST,
                  gobject.TYPE_NONE,
                  ())
    }

    def __init__(self, inspector, view):
        super(Inspector, self).__init__()

        self.inspector = inspector

        self.inspector.connect("show-window", self.handle_show)
        self.inspector.connect("close-window", self.handle_close)
        self.inspector.connect("finished", self.handle_finished)
        self.connect("delete-event", self.handle_finished)

        self.set_default_size(600, 400)
        self.win = gtk.ScrolledWindow()
        self.win.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        self.win.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        self.webview = webkit.WebView()
        self.win.add(self.webview)
        self.win.show_all()
        self.set_title("SilverLining inspector")

        self.add(self.win)

    def handle_show(self, inspector):
        self.present()
        return True

    def handle_close(self, *a):
        self.hide()
        return True

    def handle_finished(self, *a):
        self.destroy()
        self.emit("close")
        return False
