from dataclasses import dataclass
from enum import Enum
from enum import Enum
from ipaddress import IPv4Address, IPv6Address


class SimplePacketDirection(Enum):
	IN = "in"
	OUT = "out"


class SimplePacketIpProtocol(Enum):
	IPV4 = "IPv4"
	IPV6 = "IPv6"


class SimplePacketTransportProtocol(Enum):
	TCP = "TCP"
	UDP = "UDP"


@dataclass(kw_only=True)
class SimplePacket:
	direction: SimplePacketDirection
	ip_protocol: SimplePacketIpProtocol
	transport_protocol: SimplePacketTransportProtocol
	src_ip: IPv4Address | IPv6Address
	src_port: int
	dst_ip: IPv4Address | IPv6Address
	dst_port: int
