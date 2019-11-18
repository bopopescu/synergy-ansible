import json
class FilterModule(object):
	def filters(self):
		return {
			'assign_nimble_port': self.assign_nimble_port,
			'switchesrequest': self.switchesrequest,
		}

	def assign_nimble_port(self, nimble_json, port_name, network_uri):
		for p in nimble_json['ports']:
			if p['name'] == port_name:
				p['expectedNetworkUri'] = network_uri
				p['mode'] = "Managed"
		return nimble_json
		
	def switchesrequest(self, tmp, eins, uris, zwei, uris2, drei, letter, connections, distributedswitches_networks):
	
		###############
		###############		Standard
		###############
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

		data2 = {}
		for z in zwei["results"]:
			tmp = {}
			z = z["json"]
			tmp["name"] = z["name"]
			tmp["uri"] = z["uri"]
			tmp["vlanId"] = z["vlanId"]
			tmp["purpose"] = z["purpose"]
			data2[z["name"]]=tmp

		ret = []
		for networkName in data2:
			vars = data2[networkName]
			if(networkName == "iSCSI-Deployment"):
				continue

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


		###############
		###############		DISTRIBUTED
		###############		
		dataD = []
		data3 = {}
		for z in drei["results"]:
			tmp = {}
			z = z["json"]
			tmp["name"] = z["name"]
			tmp["uri"] = z["uri"]
			tmp["networkUris"] = z["networkUris"]
			data3[z["name"]]=tmp

		for e in eins:
			if("network-set" in e["networkUri"]):
				tmp = {}
				tmp["networkUri"] = e["networkUri"]
				tmp["name"] = e["name"]
				tmp["id"] = e["id"]
				tmp["portId"] = e["portId"]
				dataD.append(tmp)

		for networkName in data3:
			vars = data3[networkName]
			tmp =  {
				"name": letter+"-Prod",
				"virtualSwitchType": "Distributed",
				"version": "6.6.0",
				"virtualSwitchPortGroups": [],
				"virtualSwitchUplinks": [],
				"action": "NONE",
				"networkUris": [
				  vars["uri"]
				]
			  }

			for d in distributedswitches_networks:
				tmp2 = {}
				d = d["json"]
				tmp2["name"] = d["name"]
				tmp2["networkUris"] = [d["uri"]]
				tmp2["vlan"] = d["vlanId"]
				tmp2["virtualSwitchPorts"] = []
				tmp2["action"] = "NONE"
				tmp["virtualSwitchPortGroups"].append(tmp2)
					
			names = []
			for d in dataD:
				if(d["networkUri"] == vars["uri"]):
					if(not d["name"] in names):
						names.append(d["name"])
						
			for c in connections:
				if(c["name"] in names):
					tmp2 = {
							"name":c["portId"],
							"active": False,
							"mac": None,
							"vmnic": None,
							"action": "NONE"
						}
					tmp["virtualSwitchUplinks"].append(tmp2)
					
			ret.append(tmp)

		return json.dumps(ret)
		