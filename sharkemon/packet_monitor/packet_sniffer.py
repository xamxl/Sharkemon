import socket
import warnings
from typing import Literal, Callable
from ipaddress import IPv4Address, IPv6Address

import pyshark
from pyshark.packet.layers.xml_layer import XmlLayer
from pyshark.packet.packet import Packet

from .ip_utils import get_local_ipv4_address, get_local_ipv6_address
from .simple_packet import SimplePacket, SimplePacketDirection, SimplePacketIpProtocol, \
	SimplePacketTransportProtocol


def packet_to_simple_packet(packet: Packet, local_addresses: list[IPv4Address | IPv6Address]) -> SimplePacket | None:
	layers: list[XmlLayer] = packet.layers
	transport_layer_name: Literal["UDP", "TCP"] = str(packet.transport_layer)

	ip_layer: XmlLayer | None = None
	transport_layer: XmlLayer | None = None
	for layer in layers:
		layer_name = str(layer.layer_name).upper()
		if layer_name == "IP" or layer_name == "IPV6":
			ip_layer = layer
		elif layer_name == transport_layer_name.upper():
			transport_layer = layer
			break
	if transport_layer is None:
		# print(f"warning: no transport layer")
		return
	if ip_layer is None:
		# print(f"warning: no ip layer")
		return

	# transport-layer ports:
	src_port = int(transport_layer.get("srcport"))
	dst_port = int(transport_layer.get("dstport"))
	port = int(transport_layer.get("port"))

	# IP layer stuff:
	is_ipv6 = ip_layer.layer_name.upper() == "IPV6"
	raw_src_ip = ip_layer.get("src")
	raw_dst_ip = ip_layer.get("dst")

	src_ip: IPv4Address | IPv6Address
	dst_ip: IPv4Address | IPv6Address
	if is_ipv6:
		src_ip = IPv6Address(raw_src_ip)
		dst_ip = IPv6Address(raw_dst_ip)
	else:
		src_ip = IPv4Address(raw_src_ip)
		dst_ip = IPv4Address(raw_dst_ip)

	# figure out if inbound or outbound
	is_outbound = src_ip in local_addresses

	simple_packet = SimplePacket(
		ip_protocol=SimplePacketIpProtocol.IPV6 if is_ipv6 else SimplePacketIpProtocol.IPV4,
		transport_protocol=SimplePacketTransportProtocol(transport_layer.layer_name.upper()),
		direction=SimplePacketDirection.OUT if is_outbound else SimplePacketDirection.IN,
		src_ip=src_ip,
		src_port=src_port,
		dst_ip=dst_ip,
		dst_port=dst_port
	)
	return simple_packet


class PacketSniffer:
	def __init__(self, *, callback: Callable[[SimplePacket], None], interface: str):
		self._callback = callback
		self._local_addresses: list[IPv4Address | IPv6Address] | None = None
		self._capture = pyshark.LiveCapture(interface=interface)

	def _internal_callback(self, packet: Packet):
		try:
			simple_packet = packet_to_simple_packet(packet, local_addresses=self._local_addresses)
			if simple_packet is None:
				return
			self._callback(simple_packet)
		except Exception as e:
			warnings.warn(f"ERROR {type(e).__name__}: {e}")

	def sniff(self):
		self._local_addresses = [
			get_local_ipv4_address(),
			get_local_ipv6_address()
		]
		self._capture.apply_on_packets(callback=self._internal_callback)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self._capture.close()
