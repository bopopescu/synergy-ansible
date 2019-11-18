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
			print("now Networkname "+networkName)
			vars = data2[networkName]
			
			
			
			tmp =  {
				"name": networkName,
				"virtualSwitchType": "Standard",
				"version": "",
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
						"ipAddress": "",
						"subnetMask": "",
						"dhcp": "true",
						"action": "NONE"
					  }
					],
					"action": "NONE"
				  }
				],
				"virtualSwitchUplinks": [],
				"action": "NONE",
				"networkUris": [
				  "{{ network_uri }}"
				]
			  }
			


			for d in data:
				if(d["networkUri"] == vars["uri"]):
					tmp2 = {}
					tmp2["name"] = d["portId"]
					tmp2["active"] = "false"
					tmp2["mac"] = ""
					tmp2["vmnic"] = ""
					tmp2["action"] = "NONE"
					tmp["virtualSwitchUplinks"].append(tmp2)
			ret.append(tmp)



			"""
			ret = ret+'  - name: "'+networkName+'"\n'
			ret = ret+'    virtualSwitchType: Standard\n'
			ret = ret+'    version: \n'
			ret = ret+'    virtualSwitchPortGroups:\n'
			ret = ret+'    - name: "'+networkName+'"\n'
			ret = ret+'      networkUris:\n'
			ret = ret+'      - "'+vars["uri"]+'"\n'
			ret = ret+'      vlan: "0"\n'
			ret = ret+'      virtualSwitchPorts:\n'
			ret = ret+'      - virtualPortPurpose:\n'
			ret = ret+'        - "'+vars["purpose"]+'"\n'
			ret = ret+'        ipAddress: \n'
			ret = ret+'        subnetMask: \n'
			ret = ret+'        dhcp: true\n'
			ret = ret+'        action: NONE\n'
			ret = ret+'      action: NONE\n'
			ret = ret+'    virtualSwitchUplinks:\n'
			for d in data:
				if(d["networkUri"] == vars["uri"]):
					ret = ret+'    - name: '+d["portId"]+'\n'
					ret = ret+'      active: false\n'
					ret = ret+'      mac: \n'
					ret = ret+'      vmnic: \n'
					ret = ret+'      action: NONE\n'
			ret = ret+'    action: NONE\n'
			ret = ret+'    networkUris:\n'
			ret = ret+'    - "'+vars["uri"]+'"\n'
			"""
		print(json.dumps(ret))
			
		return json.dumps(ret)
		