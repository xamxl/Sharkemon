import wx
from card import Card
from card_view import CardViewFrame

class DiscoveryFrame(wx.Frame):
    def __init__(self, parent, card_library):
        super().__init__(parent, title="Discover Cards", size=(400,300))
        self.card_library = card_library
        self.new_cards = [
            Card("Fire Card", "images.png", "Burn foes."),
            Card("Water Card", "images.png", "Douse flames."),
            Card("Earth Card", "images.png", "Solid defense."),
        ]
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.card_list = wx.ListBox(panel, choices=[c.name for c in self.new_cards])
        btn_view = wx.Button(panel, label="View")
        btn_accept = wx.Button(panel, label="Accept")
        btn_skip = wx.Button(panel, label="Skip")

        sizer.Add(self.card_list, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(btn_view, 0, wx.ALL, 5)
        sizer.Add(btn_accept, 0, wx.ALL, 5)
        sizer.Add(btn_skip, 0, wx.ALL, 5)
        panel.SetSizer(sizer)

        btn_view.Bind(wx.EVT_BUTTON, self.on_view)
        btn_accept.Bind(wx.EVT_BUTTON, self.on_accept)
        btn_skip.Bind(wx.EVT_BUTTON, self.on_skip)

    def on_view(self, event):
        i = self.card_list.GetSelection()
        if i != wx.NOT_FOUND:
            card = self.new_cards[i]
            view = CardViewFrame(self, card)
            view.Show()

    def on_accept(self, event):
        i = self.card_list.GetSelection()
        if i != wx.NOT_FOUND:
            card = self.new_cards.pop(i)
            self.card_library.add_card(card)
            self.card_list.Delete(i)

    def on_skip(self, event):
        i = self.card_list.GetSelection()
        if i != wx.NOT_FOUND:
            self.new_cards.pop(i)
            self.card_list.Delete(i)