import json
class FilterModule(object):
	def filters(self):
		return {
			'assign_nimble_port': self.assign_nimble_port,
			'standardswitchesrequest': self.standardswitchesrequest,
		}

	def assign_nimble_port(self, nimble_json, port_name, network_uri):
		for p in nimble_json['ports']:
			if p['name'] == port_name:
				p['expectedNetworkUri'] = network_uri
				p['mode'] = "Managed"
		return nimble_json
		
	def standardswitchesrequest(self, tmp, eins, uris, zwei):		
		data = []
		uniqueNetworkNames = []
		for e in eins:
			if("ethernet-networks" in e["networkUri"]):
				tmp = {}
				tmp["networkUri"] = e["networkUri"]
				tmp["name"] = e["name"]
				tmp["id"] = e["id"]
				tmp["portId"] = e["portId"]
				data.append(tmp)
		#print(data)
		
		data2 = {}
		for z in zwei["results"]:
			tmp = {}
			z = z["json"]
			#print(z)
			tmp["name"] = z["name"]
			tmp["uri"] = z["uri"]
			tmp["vlanId"] = z["vlanId"]
			tmp["purpose"] = z["purpose"]
			data2[z["name"]]=tmp
		#print(data2)
		
		ret = []
		for networkName in data2:
			#print("now Networkname "+networkName)
			vars = data2[networkName]

			tmp =  {
				"name": networkName,
				"virtualSwitchType": "Standard",
				"version": None,
				"virtualSwitchPortGroups": [
				  {
					"name": networkName,
					"networkUris": [
					  vars["uri"]
					],
					"vlan": "0",
					"virtualSwitchPorts": [
					  {
						"virtualPortPurpose": [
						  vars["purpose"]
						],
						"ipAddress": None,
						"subnetMask": None,
						"dhcp": True,
						"action": "NONE"
					  }
					],
					"action": "NONE"
				  }
				],
				"virtualSwitchUplinks": [],
				"action": "NONE",
				"networkUris": [
				  vars["uri"]
				]
			  }

			for d in data:
				if(d["networkUri"] == vars["uri"]):
					tmp2 = {}
					tmp2["name"] = d["portId"]
					tmp2["active"] = False
					tmp2["mac"] = None
					tmp2["vmnic"] = None
					tmp2["action"] = "NONE"
					tmp["virtualSwitchUplinks"].append(tmp2)
			ret.append(tmp)

		#print(json.dumps(ret))
		return json.dumps(ret)
		