import os
import wx

class CardViewFrame(wx.Frame):
    def __init__(self, parent, card):
        super().__init__(parent, title=card.name, size=(300,300))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        img_path = card.image_path
        if not os.path.exists(img_path):
            img_path = "fallback.png"  # or any known valid path

        img = wx.Image(img_path, wx.BITMAP_TYPE_ANY).Scale(120,120)
        image_ctrl = wx.StaticBitmap(panel, bitmap=wx.Bitmap(img))
        desc_ctrl = wx.StaticText(panel, label=card.description)

        sizer.Add(image_ctrl, 0, wx.ALL|wx.CENTER, 5)
        sizer.Add(desc_ctrl, 0, wx.ALL|wx.CENTER, 5)
        panel.SetSizer(sizer)