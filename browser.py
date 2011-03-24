import gtkmozembed

class Browser(object):
    def __init__(self):
        self.moz = gtkmozembed.MozEmbed()
        self.moz.connect("new-window", self.new_window)

    def load_url(self, url):
        self.moz.load_url(url)

    @property
    def widget(self):
        return self.moz

    def new_window(self, *a, **b):
        print "new_window", a, b
