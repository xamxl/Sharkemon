import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Annotated

from pydantic import BaseModel, BeforeValidator, field_serializer, Base64Bytes

from .simple_packet import SimplePacketTransportProtocol


@dataclass(frozen=True, eq=True)
class ProtocolDescriptorMatch:
	transport_protocol: SimplePacketTransportProtocol
	port: int


def _protocols_validator(strings: Any):
	protocols = []
	if not isinstance(strings, list):
		raise ValueError("invalid")
	for string in strings:
		sliced = string.split(":")
		assert len(sliced) == 2
		protocol_enum = SimplePacketTransportProtocol(sliced[0])
		port = int(sliced[1])
		protocols.append(ProtocolDescriptorMatch(
			transport_protocol=protocol_enum,
			port=port
		))
	return protocols


class ProtocolDescriptorRarity(Enum):
	common = "common"
	rare = "rare"
	epic = "epic"
	legendary = "legendary"


class ProtocolDescriptor(BaseModel):
	id: str
	name: str
	rarity: ProtocolDescriptorRarity
	full_name: str
	wikipedia_title: str
	matches: Annotated[list[ProtocolDescriptorMatch], BeforeValidator(_protocols_validator)]

	@field_serializer("matches")
	def protocols_serializer(self, protocols, _info):
		return [f"{protocol.transport_protocol.value}:{protocol.port}" for protocol in protocols]


def load_protocol_descriptors() -> list[ProtocolDescriptor]:
	protocol_descriptors_path = Path(__file__).parent / "protocol_descriptors.json"
	with open(protocol_descriptors_path, "r") as file:
		data = json.load(file)

	return [ProtocolDescriptor(**raw_descriptor) for raw_descriptor in data]
