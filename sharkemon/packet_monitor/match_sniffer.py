from typing import Callable

from .simple_packet import SimplePacket, SimplePacketDirection
from .packet_sniffer import PacketSniffer
from .protocol_descriptors import load_protocol_descriptors, ProtocolDescriptorMatch, ProtocolDescriptor

descriptors = load_protocol_descriptors()
descriptor_index: dict[ProtocolDescriptorMatch, ProtocolDescriptor] = {}
for descriptor in descriptors:
	for match in descriptor.matches:
		descriptor_index[match] = descriptor


class MatchSniffer:
	def __init__(self, callback: Callable[[ProtocolDescriptor], None], interface: str):
		self._callback = callback
		self._sniffer = PacketSniffer(
			callback=self._internal_callback,
			interface=interface
		)

	def sniff(self):
		self._sniffer.sniff()

	def __enter__(self):
		self._sniffer.__enter__()
		return self

	def __exit__(self, _1, _2, _3):
		self._sniffer.__exit__(_1, _2, _3)

	def _internal_callback(self, packet: SimplePacket):
		port = packet.dst_port if packet.direction == SimplePacketDirection.OUT else packet.src_port
		match = ProtocolDescriptorMatch(
			transport_protocol=packet.transport_protocol,
			port=port
		)
		descriptor = descriptor_index.get(match)
		if descriptor is None:
			return
		self._callback(descriptor)
