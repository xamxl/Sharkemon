import wx
from sharkemon.gui import MainFrame


def main():
	app = wx.App()
	frame = MainFrame()
	frame.Show()
	app.MainLoop()


if __name__ == '__main__':
	main()
