import wx
from card_library import CardLibrary
from discovery import DiscoveryFrame
from card_view import CardViewFrame

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Card Game", size=(600,400))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        library_btn = wx.Button(panel, label="Open Library")
        discovery_btn = wx.Button(panel, label="Discover Cards")
        sizer.Add(library_btn, 0, wx.ALL, 5)
        sizer.Add(discovery_btn, 0, wx.ALL, 5)
        panel.SetSizer(sizer)

        library_btn.Bind(wx.EVT_BUTTON, self.on_library)
        discovery_btn.Bind(wx.EVT_BUTTON, self.on_discovery)

        self.library_frame = None
        self.discovery_frame = None
        self.card_library = CardLibrary()

    def on_library(self, event):
        if not self.library_frame:
            self.library_frame = wx.Frame(self, title="My Card Library", size=(400,300))
            p = wx.Panel(self.library_frame)
            box = wx.BoxSizer(wx.VERTICAL)
            self.card_list = wx.ListBox(p)
            self.view_button = wx.Button(p, label="View Card")
            box.Add(self.card_list, 1, wx.ALL|wx.EXPAND, 5)
            box.Add(self.view_button, 0, wx.ALL, 5)
            p.SetSizer(box)

            self.view_button.Bind(wx.EVT_BUTTON, self.on_view_library_card)
            self.refresh_library()
        self.library_frame.Show()

    def refresh_library(self):
        self.card_list.Clear()
        for c in self.card_library.cards:
            self.card_list.Append(c.name)

    def on_view_library_card(self, event):
        i = self.card_list.GetSelection()
        if i != wx.NOT_FOUND:
            name = self.card_list.GetString(i)
            card = self.card_library.get_card(name)
            if card:
                view = CardViewFrame(self.library_frame, card)
                view.Show()

    def on_discovery(self, event):
        if not self.discovery_frame:
            self.discovery_frame = DiscoveryFrame(self, self.card_library)
        self.discovery_frame.Show()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()