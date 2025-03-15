import wx
import os
from pydantic import BaseModel
import datetime

class Card(BaseModel):
    name: str #this is the protocol
    port: int
    dateFound: datetime.datetime
    description: str
    image_path: str
    #def __init__(self, name, image_path, description):
    #    self.name = name
    #    self.image_path = image_path
    #    self.description = description
        

class CardLibrary:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_card(self, name):
        for c in self.cards:
            if c.name == name:
                return c
        return None

class LibraryPanel(wx.Panel):
    def __init__(self, parent, library, on_view_callback):
        super().__init__(parent)
        self.library = library
        self.on_view = on_view_callback

        sizer = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(self, label="My Library")
        self.listbox = wx.ListBox(self, style=wx.LB_SINGLE)
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(self.listbox, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)

        self.listbox.Bind(wx.EVT_LISTBOX, self.on_select)

    def refresh(self):
        self.listbox.Clear()
        for c in self.library.cards:
            self.listbox.Append(c.name)

    def on_select(self, event):
        selection = event.GetString()
        card = self.library.get_card(selection)
        if card:
            self.on_view(card)

class DiscoveryPanel(wx.Panel):
    def __init__(self, parent, library, new_cards, on_view_callback):
        super().__init__(parent)
        self.library = library
        self.new_cards = new_cards
        self.on_view = on_view_callback

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(self, label="Discover New Cards")
        self.listbox = wx.ListBox(self, style=wx.LB_SINGLE)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_accept = wx.Button(self, label="Accept")
        self.btn_skip = wx.Button(self, label="Skip")
        btn_sizer.Add(self.btn_accept, 0, wx.ALL, 5)
        btn_sizer.Add(self.btn_skip, 0, wx.ALL, 5)

        main_sizer.Add(lbl, 0, wx.ALL, 5)
        main_sizer.Add(self.listbox, 1, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(btn_sizer, 0, wx.CENTER)
        self.SetSizer(main_sizer)

        self.listbox.Bind(wx.EVT_LISTBOX, self.on_select)
        self.btn_accept.Bind(wx.EVT_BUTTON, self.on_accept)
        self.btn_skip.Bind(wx.EVT_BUTTON, self.on_skip)

    def refresh(self):
        self.listbox.Clear()
        for c in self.new_cards:
            self.listbox.Append(c.name)

    def on_select(self, event):
        idx = self.listbox.GetSelection()
        if idx != wx.NOT_FOUND:
            card = self.new_cards[idx]
            self.on_view(card)

    def on_accept(self, event):
        idx = self.listbox.GetSelection()
        if idx != wx.NOT_FOUND:
            card = self.new_cards.pop(idx)
            self.library.add_card(card)
            self.refresh()
            self.GetTopLevelParent().refresh_all()

    def on_skip(self, event):
        idx = self.listbox.GetSelection()
        if idx != wx.NOT_FOUND:
            self.new_cards.pop(idx)
            self.refresh()
            self.GetTopLevelParent().refresh_all()

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Card Game - Single Window", size=(800, 400))
        self.library = CardLibrary()
        self.new_cards = [
            Card(name="TCP", port=443, dateFound=datetime.datetime.now(), description="I love secure communication!", image_path="images.png"),
            Card(name="UDP", port=20, dateFound=datetime.datetime.now(), description="I'm stateless!", image_path="images.png"),
            Card(name="DNS", port=80, dateFound=datetime.datetime.now(), description="I find things", image_path="images.png"),
        ]

        self.main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.notebook = wx.Notebook(self.main_panel)
        self.library_panel = LibraryPanel(self.notebook, self.library, self.show_card)
        self.discovery_panel = DiscoveryPanel(self.notebook, self.library, self.new_cards, self.show_card)
        self.notebook.AddPage(self.library_panel, "Library")
        self.notebook.AddPage(self.discovery_panel, "Discover")
        main_sizer.Add(self.notebook, 1, wx.EXPAND|wx.ALL, 5)

        self.viewer_panel = wx.Panel(self.main_panel, size=(-1, 140))
        box = wx.StaticBox(self.viewer_panel, label="Card Viewer")
        viewer_sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        self.img_ctrl = wx.StaticBitmap(self.viewer_panel)
        self.desc_text = wx.StaticText(self.viewer_panel, label="")
        viewer_sizer.Add(self.img_ctrl, 0, wx.ALL|wx.CENTER, 10)
        viewer_sizer.Add(self.desc_text, 0, wx.ALL|wx.CENTER, 10)
        self.viewer_panel.SetSizer(viewer_sizer)
        main_sizer.Add(self.viewer_panel, 0, wx.EXPAND|wx.ALL, 5)

        self.main_panel.SetSizer(main_sizer)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_changed)
        self.viewer_panel.Hide()
        self.refresh_all()

    def refresh_all(self):
        self.library_panel.refresh()
        self.discovery_panel.refresh()

    def show_card(self, card):
        full_path = os.path.join(os.path.dirname(__file__), card.image_path)
        if not os.path.exists(full_path):
            self.img_ctrl.SetBitmap(wx.NullBitmap)
        else:
            img = wx.Image(full_path, wx.BITMAP_TYPE_ANY)
            bmp = img.Scale(120, 120).ConvertToBitmap()
            self.img_ctrl.SetBitmap(bmp)
        self.desc_text.SetLabel(card.description)
        self.viewer_panel.Show()
        # Important to lay out the entire frame so the panel becomes visible
        self.Layout()

    def on_page_changed(self, event):
        self.library_panel.listbox.SetSelection(wx.NOT_FOUND)
        self.discovery_panel.listbox.SetSelection(wx.NOT_FOUND)
        self.img_ctrl.SetBitmap(wx.NullBitmap)
        self.desc_text.SetLabel("")
        self.viewer_panel.Hide()
        self.Layout()
        event.Skip()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()