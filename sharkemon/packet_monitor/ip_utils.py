import socket
from ipaddress import IPv4Address, IPv6Address

# test addresses for identifying the local address
_IPV4_ADDR = "1.1.1.1"
_IPV6_ADDR = "2606:4700:4700::1111"


def get_local_ipv4_address() -> IPv4Address:
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		s.connect((_IPV4_ADDR, 80))
		local_ip = s.getsockname()[0]
		return IPv4Address(local_ip)


def get_local_ipv6_address() -> IPv6Address:
	with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as s:
		s.connect((_IPV6_ADDR, 80))
		local_ip = s.getsockname()[0]
		return IPv6Address(local_ip)