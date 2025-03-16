import subprocess
import re


def get_active_network_interfaces():
	result = subprocess.run(["/usr/sbin/scutil", "--nwi"], stdout=subprocess.PIPE)
	result.check_returncode()
	output = result.stdout.decode("ascii")
	pattern = re.compile(r"^Network interfaces: (.*)$", re.MULTILINE)
	match = pattern.search(output)
	interfaces = match.group(1).split(" ")
	return interfaces
