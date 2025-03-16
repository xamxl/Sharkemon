import datetime
import json
from pathlib import Path

from pydantic import BaseModel

from sharkemon.packet_monitor.macos import get_active_network_interfaces

CONFIG_DIR = Path("~/.sharkemon/").expanduser()
CONFIG_DIR.mkdir(exist_ok=True)

config_path = CONFIG_DIR / "config.json"
discoveries_path = CONFIG_DIR / "discoveries.json"


class Config(BaseModel):
	network_interface: str


class DiscoveredProtocolStatistics(BaseModel):
	packet_count: int


class DiscoveredProtocol(BaseModel):
	id: str
	date_found: datetime.datetime
	date_last_seen: datetime.datetime
	statistics: DiscoveredProtocolStatistics


class Discoveries(BaseModel):
	discoveries: list[DiscoveredProtocol]


def load_discoveries() -> Discoveries:
	if discoveries_path.exists():
		with open(discoveries_path, "r") as file:
			return Discoveries.model_validate_json(file.read())
	else:
		return Discoveries(discoveries=[])


def save_discoveries(discoveries: Discoveries):
	with open(discoveries_path, "w") as file:
		file.write(discoveries.model_dump_json(indent=2))


def load_config() -> Config:
	if config_path.exists():
		with open(config_path, "r") as file:
			return Config.model_validate_json(file.read())
	else:
		# load default config if there is none!
		network_interface = get_active_network_interfaces()[0]
		return Config(
			network_interface=network_interface
		)


def save_config(config: Config):
	with open(config_path, "w") as file:
		file.write(config.model_dump_json(indent=2))
