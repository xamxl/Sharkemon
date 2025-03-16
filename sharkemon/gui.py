from __future__ import annotations

import sys
import threading
import urllib.parse

import webbrowser
from pathlib import Path

import wx
import wx.html
import os
import datetime
from pydantic import BaseModel
import wikipedia
from wx import Font

from .config import load_config, save_config, load_discoveries, save_discoveries, DiscoveredProtocol, \
	DiscoveredProtocolStatistics, discoveries_path
from .packet_monitor.macos import get_active_network_interfaces
from .packet_monitor.match_sniffer import MatchSniffer
from .packet_monitor.protocol_descriptors import load_protocol_descriptors, ProtocolDescriptor


def get_wikipedia_summary(article_name: str):
	# receives name, looks it up on wikipedia, and returns a description
	return wikipedia.summary(article_name, sentences=2, auto_suggest=False)


class SettingsDialog(wx.Dialog):
	def __init__(self, parent, network_interface: str, on_network_interface_chosen):
		size = (400, 300)
		super().__init__(parent, title="Sharkemon Settings", size=size)
		sizer = wx.BoxSizer(wx.VERTICAL)

		self.on_network_interface_chosen = on_network_interface_chosen

		grid = wx.GridSizer(2, 16, 8)
		grid.Add(wx.StaticText(self, label="Network interface to monitor"))
		self.choice = wx.Choice(self, choices=get_active_network_interfaces())
		self.choice.SetStringSelection(network_interface)
		self.choice.Bind(wx.EVT_CHOICE, self.choice_evt)
		grid.Add(self.choice)
		kill_button = wx.Button(self, label="Reset")
		kill_button.Bind(wx.EVT_BUTTON, self.kill)
		grid.Add(kill_button)

		sizer.Add(grid, border=18, flag=wx.ALL | wx.EXPAND, proportion=1)

		done_button = wx.Button(self, id=wx.ID_OK)
		done_button.SetDefault()
		sizer.Add(done_button, flag=wx.ALIGN_RIGHT | wx.ALL, border=18)
		done_button.Bind(wx.EVT_BUTTON, self.done_button_clicked)

		self.SetSizer(sizer)
		self.Fit()
		self.SetMinSize(self.GetSize())
		self.SetSize(size)

	def kill(self, evt):
		discoveries_path.unlink()
		self.GetParent().discoveries.discoveries = []
		self.GetParent().Close()


	def choice_evt(self, evt):
		self.on_network_interface_chosen(self.choice.GetStringSelection())

	def done_button_clicked(self, evt):
		self.EndModal(0)


class DescriptorPanel(wx.Panel):
	def __init__(self, parent: wx.Treebook, descriptor: ProtocolDescriptor):
		super().__init__(parent)
		self.descriptor = descriptor
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.inner_sizer = wx.BoxSizer(wx.VERTICAL)

		top = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label=descriptor.name, style=wx.TEXT_ALIGNMENT_CENTER | wx.ST_ELLIPSIZE_END)
		title.SetFont(title.GetFont().Scale(1.5))
		top.Add(title, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=4)

		subtitle = wx.StaticText(self, label=descriptor.full_name, style=wx.TEXT_ALIGNMENT_CENTER | wx.ST_ELLIPSIZE_END)
		top.Add(subtitle, flag=wx.ALIGN_CENTER)

		self.sizer.Add(self.inner_sizer, flag=wx.ALL | wx.EXPAND, border=8, proportion=1)
		self.inner_sizer.Add(top, flag=wx.EXPAND)
		self.SetSizer(self.sizer)
		self.html_loaded = False

	def ensure_loaded(self):
		if not self.html_loaded:
			self.load_html()

	def load_html(self):
		html = wx.html.HtmlWindow(parent=self)
		self.html_loaded = True
		summary = get_wikipedia_summary(self.descriptor.wikipedia_title)
		url_title = urllib.parse.quote(self.descriptor.wikipedia_title)
		url = "https://en.wikipedia.org/wiki/" + url_title
		html.SetPage(f"""<p>{summary}</p><hr /><a href="{url}">Read more on Wikipedia</a>""")
		html.Bind(wx.html.EVT_HTML_LINK_CLICKED, lambda _: webbrowser.open(url))

		self.inner_sizer.Add(html, flag=wx.EXPAND | wx.TOP, proportion=1, border=15)
		self.Layout()


class UndiscoveredPanel(wx.Panel):
	def __init__(self, parent):
		super().__init__(parent)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		label = wx.StaticText(self, label="You haven't seen this protocol yet!")
		self.SetSizer(self.sizer)

class CollectionPanel(wx.Panel):
	def __init__(self, parent: wx.Notebook, main_frame: MainFrame):
		super().__init__(parent)
		self.parent = parent
		self.frame = main_frame

		descriptors = self.frame.descriptors
		discovered_ids = [dis.id for dis in self.frame.discoveries.discoveries]

		sizer = wx.BoxSizer(wx.VERTICAL)
		self.treebook = wx.Treebook(self)
		self.treebook.Bind(wx.EVT_TREEBOOK_PAGE_CHANGED, self.treebook_page_changed)

		i = 0
		for descriptor in descriptors:
			discovered = descriptor.id in discovered_ids
			if discovered:
				self.treebook.AddPage(
					page=DescriptorPanel(self.treebook, descriptor),
					text=descriptor.name,
					imageId=i
				)
			else:
				self.treebook.AddPage(
					page=UndiscoveredPanel(self.treebook),
					text="???",
					imageId=i
				)
			i += 1

		images_path = Path(__file__).parent.parent / "images"
		images = []

		for descriptor in descriptors:
			discovered = descriptor.id in discovered_ids
			if discovered:
				image_path = images_path / f"{descriptor.id}.png"
				if not image_path.exists():
					image_path = images_path / "default.png"
			else:
				image_path = images_path / "undiscovered.png"

			image = wx.Image(str(image_path)).Rescale(48, 48, quality=wx.IMAGE_QUALITY_HIGH)
			images.append(image)

		self.treebook.SetImages(images)

		sizer.Add(self.treebook, flag=wx.EXPAND, proportion=1)
		self.SetSizer(sizer)

	def treebook_page_changed(self, evt):
		page = self.treebook.GetCurrentPage()

		if isinstance(page, DescriptorPanel):
			self.thread = threading.Thread(target=page.ensure_loaded)
			self.thread.start()


class MainFrame(wx.Frame):
	def __init__(self):
		super().__init__(None, title="Sharkemon", size=(500, 350))

		self.config = load_config()
		self.descriptors = load_protocol_descriptors()
		self.discoveries = load_discoveries()

		sizer = wx.BoxSizer(wx.VERTICAL)
		self.notebook = wx.Notebook(self)

		# self.notebook.AddPage(wx.Panel(self.notebook), "Library")
		self.notebook.AddPage(CollectionPanel(self.notebook, self), "Collection")
		sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 10)
		self.SetSizer(sizer)

		self.settings_dialog = SettingsDialog(self, self.config.network_interface, self.on_network_interface_chosen)
		self.Bind(wx.EVT_MENU, self.on_preferences_clicked, id=wx.ID_PREFERENCES)

		menubar = wx.MenuBar()
		menu = wx.Menu()
		menu.Append(wx.ID_PREFERENCES, "&Preferences\tCtrl-,")
		menubar.Append(menu, "@")
		self.SetMenuBar(menubar)

		self.thread = threading.Thread(target=self.main_thread)
		self.thread.start()

	def callback(self, descriptor: ProtocolDescriptor):
		for discovery in self.discoveries.discoveries:
			if discovery.id == descriptor.id:
				discovery.date_last_seen = datetime.datetime.utcnow()
				discovery.statistics.packet_count += 1
				save_discoveries(self.discoveries)
				return

		# it's new
		new_discovery = DiscoveredProtocol(
			id=descriptor.id,
			date_found=datetime.datetime.utcnow(),
			date_last_seen=datetime.datetime.utcnow(),
			statistics=DiscoveredProtocolStatistics(
				packet_count=1
			)
		)
		print(f"You just discovered {descriptor.full_name}")
		self.discoveries.discoveries.append(new_discovery)
		save_discoveries(self.discoveries)

		thread = threading.Thread(target=lambda: wx.MessageBox(
			caption=f"You just discovered {descriptor.name}!!",
			message="Check it out in your Sharkemon Collection.",
			parent=self
		))
		thread.start()

	def main_thread(self):
		with MatchSniffer(self.callback, self.config.network_interface) as sniffer:
			sniffer.sniff()

	def on_network_interface_chosen(self, network_interface: str):
		self.config.network_interface = network_interface
		save_config(self.config)
		print(f"{network_interface=}")

	def on_preferences_clicked(self, evt):
		self.settings_dialog.ShowWindowModal()
