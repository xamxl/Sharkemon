import wx
import os
import datetime
from pydantic import BaseModel
import wikipedia

class Card(BaseModel):
    name: str
    port: int
    dateFound: datetime.datetime
    description: str
    image_path: str

class CardLibrary:
    def __init__(self):
        self.cards = []
    def add_card(self, card):
        self.cards.append(card)
    def get_card(self, name):
        return next((c for c in self.cards if c.name == name), None)

class LibraryPanel(wx.Panel):
    def __init__(self, parent, library):
        super().__init__(parent)
        self.library = library
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, label="My Library"), 0, wx.ALL, 5)
        self.listctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.listctrl.InsertColumn(0, "Name")
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.img_list = wx.ImageList(32, 32)
        self.listctrl.AssignImageList(self.img_list, wx.IMAGE_LIST_SMALL)
        self.listctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open_card)
        sizer.Add(self.listctrl, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

    def on_size(self, event):
        event.Skip()  # Let the sizer handle the event first
        wx.CallAfter(self.resize_column_to_full_width)

    def resize_column_to_full_width(self):
        width, _ = self.listctrl.GetClientSize()
        self.listctrl.SetColumnWidth(0, width)

    def refresh(self):
        self.listctrl.DeleteAllItems()
        self.img_list.RemoveAll()
        for idx, card in enumerate(self.library.cards):
            bmp = wx.Bitmap(self.load_and_scale(card.image_path, 32, 32))
            img_index = self.img_list.Add(bmp)
            self.listctrl.InsertItem(idx, card.name, img_index)

    def load_and_scale(self, path, w, h):
        full_path = os.path.join(os.path.dirname(__file__), path)
        bmp = wx.Bitmap(full_path, wx.BITMAP_TYPE_ANY)
        return bmp.ConvertToImage().Scale(w, h, wx.IMAGE_QUALITY_HIGH)

    def on_open_card(self, event):
        idx = event.GetIndex()
        name = self.listctrl.GetItemText(idx)
        card = self.library.get_card(name)
        if card:
            CardViewerFrame(card).Show()

class DiscoveryPanel(wx.Panel):
    def __init__(self, parent, library, new_cards):
        super().__init__(parent)
        self.library = library
        self.new_cards = new_cards
        self.current_card = None
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(wx.StaticText(self, label="Discover (Queue)"), 0, wx.ALL, 5)

        self.image = wx.StaticBitmap(self, size=(120, 120))
        self.desc = wx.StaticText(self, label="")
        main_sizer.Add(self.image, 0, wx.ALL | wx.CENTER, 5)
        main_sizer.Add(self.desc, 0, wx.ALL | wx.CENTER, 5)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_accept = wx.Button(self, label="Accept")
        btn_skip = wx.Button(self, label="Skip")
        btn_accept.Bind(wx.EVT_BUTTON, self.on_accept)
        btn_skip.Bind(wx.EVT_BUTTON, self.on_skip)
        btn_sizer.Add(btn_accept, 0, wx.ALL, 5)
        btn_sizer.Add(btn_skip, 0, wx.ALL, 5)
        main_sizer.Add(btn_sizer, 0, wx.CENTER)
        self.SetSizer(main_sizer)
        self.load_next_card()

    def load_next_card(self):
        if self.new_cards:
            self.current_card = self.new_cards[0]
            self.update_ui(self.current_card)
        else:
            self.current_card = None
            self.image.SetBitmap(wx.NullBitmap)
            self.desc.SetLabel("No more cards to discover.")

    def update_ui(self, card):
        path = os.path.join(os.path.dirname(__file__), card.image_path)
        bmp = wx.Bitmap(path, wx.BITMAP_TYPE_ANY)
        scaled = bmp.ConvertToImage().Scale(120, 120, wx.IMAGE_QUALITY_HIGH)
        self.image.SetBitmap(wx.Bitmap(scaled))
        self.desc.SetLabel(f"{card.name}\nPort: {card.port}\n{card.description}")

    def on_accept(self, _):
        if self.current_card:
            self.library.add_card(self.current_card)
            self.new_cards.pop(0)
        self.load_next_card()
        self.GetTopLevelParent().library_panel.refresh()

    def on_skip(self, _):
        if self.current_card:
            self.new_cards.pop(0)
        self.load_next_card()

class CardViewerFrame(wx.Frame):
    def __init__(self, card):
        super().__init__(None, title=card.name, size=(300, 300))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        path = os.path.join(os.path.dirname(__file__), card.image_path)
        bmp = wx.Bitmap(path, wx.BITMAP_TYPE_ANY)
        scaled = bmp.ConvertToImage().Scale(120, 120, wx.IMAGE_QUALITY_HIGH)
        img = wx.StaticBitmap(panel, bitmap=wx.Bitmap(scaled))
        desc = wx.StaticText(panel, label=f"Name: {card.name}\nPort: {card.port}\n{card.description}")
        sizer.Add(img, 0, wx.ALL | wx.CENTER, 10)
        sizer.Add(desc, 0, wx.ALL | wx.CENTER, 10)
        panel.SetSizer(sizer)

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Card Game", size=(450, 350))
        self.library = CardLibrary()
        self.new_cards = [
            Card(name="TCP", port=443, dateFound=datetime.datetime.now(),
                 description=self.getWikiDescription("TCP"), image_path="images.png"),
            Card(name="UDP", port=20, dateFound=datetime.datetime.now(),
                 description=self.getWikiDescription("UDP"), image_path="images.png"),
            Card(name="DNS", port=80, dateFound=datetime.datetime.now(),
                 description=self.getWikiDescription("DNS"), image_path="images.png"),
        ]
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.notebook = wx.Notebook(panel)
        self.library_panel = LibraryPanel(self.notebook, self.library)
        self.discovery_panel = DiscoveryPanel(self.notebook, self.library, self.new_cards)
        self.notebook.AddPage(self.library_panel, "Library")
        self.notebook.AddPage(self.discovery_panel, "Discover")
        sizer.Add(self.notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)
    def getWikiDescription(self, name):
        #receives name, looks it up on wikipedia, and returns a description
        name = self.getFullFromAcronym(name)
        desc = wikipedia.summary(name, sentences=2)
        return desc
    def getFullFromAcronym(self, acronym):
        #recieves an acronym and looks it up in a .csv file from wikipedia, returns full name if it exists, otherwise returns acronym
        f = open("abiTranslations.csv")
        full = acronym
        for line in f:
            lineArr = line.split(",")
            if (lineArr[0] == acronym):
                full = lineArr[1]
        f.close()
        return full

    def refresh_all(self):
        self.library_panel.refresh()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    frame.refresh_all()
    app.MainLoop()