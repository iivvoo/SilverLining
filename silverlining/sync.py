import gobject

from silverlining.ui import loader
from silversync.client import Sync as SyncLib

class Sync(gobject.GObject):
    """
        Sync or overall setup? Should show configuration dialog
        on demand and update whenever necessary
    """
    __gsignals__ = {
        "accepted": (gobject.SIGNAL_RUN_FIRST,
                     gobject.TYPE_NONE,
                     ()),
    }

    def __init__(self):
        super(Sync, self).__init__()
        self.window = loader("startup")
        self.startup = loader("startup")
        self.startup.show_all()

        self.username = loader("username")
        self.password = loader("password")
        self.passphrase = loader("passphrase")

        loader("ok").connect("clicked", self.handle_config)
        loader("skip").connect("clicked", self.skip_config)

    def show(self):
        self.window.show_all()

    def close(self):
        self.window.destroy()

    def handle_config(self, widget):
        username = self.username.get_text().strip()
        password = self.password.get_text().strip()
        passphrase = self.passphrase.get_text().strip()
        self.startup.destroy()
        print username, password, passphrase
        ## initialize sync lib, fetch passwords
        self.sync = SyncLib(username, password, passphrase)
        self.passwords = self.sync.passwords()
        self.emit("accepted") ## only on success

    def skip_config(self, widget):
        self.startup.destroy()


