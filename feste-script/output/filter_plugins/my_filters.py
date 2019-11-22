import json
class FilterModule(object):
	def filters(self):
		return {
			'assign_nimble_port': self.assign_nimble_port,
		}

	def assign_nimble_port(self, nimble_json, port_name, network_uri):
		for p in nimble_json['ports']:
			if p['name'] == port_name:
				p['expectedNetworkUri'] = network_uri
				p['mode'] = "Managed"
		return nimble_json