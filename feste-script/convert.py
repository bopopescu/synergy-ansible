#Created by Felix Sterzelmaier, Concat AG
#2019-11
#tested on Python 3.7.4 and 3.7.5rc1
#run with "run.bat" or "python3 ./convert.py" or "python ./convert.py"

#imports
import xlrd
import os
import sys
from datetime import datetime
from datetime import time
from pytz import timezone
from datetime import timezone, datetime, timedelta
import tzlocal
import string
import re

############################################################################
############ Only Change Variables below this line #########################
############################################################################

filename_prefix = ""
filename_sufix = ".yml"
columnNames = "A" # in exceltabgeneral
config_prefx = ""
config_sufix = "_oneview_config.json"
inputfilename = "wip_checkliste_gesamt.xlsx"
exceltabgeneral = "Synergy-MGMT"
exceltabsubnets = "Synergy-Subnets"
exceltabnets = "Synergy-Networks"
outputfolder = "output"

############################################################################
############## Only change Variables above this line #######################
############################################################################

variables = {}
variablesAll = []

#change working directory to script path/xlsx path
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)





def columnCharToInt(c):
	c = c.lower()
	return string.ascii_lowercase.index(c)

def fillVariables():
	global variablesAll
	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabgeneral)

	columnNamesInt = columnCharToInt(columnNames)
	
	
	for frame in variablesAll:
		variables = {}
		infocount = 0
		foundGateway = False
		for row in range(worksheet.nrows):
			name = str(worksheet.cell_value(row,columnNamesInt))
			
			if(name==""):
				continue
				
			if(name=="Infos"):
				infocount = infocount + 1
				continue

			if(infocount!=1):
				continue
			
			#found valid line
			columnDataInt = frame["column"]
			data = str(worksheet.cell_value(row,columnDataInt))
			if(data=="" or data=="#TODO" or data=="n/a" or data.startswith("#TODO")):
				continue
			
			if(data.find("#TODO") != -1):
				pos = data.find("#TODO")
				data = data[:pos-1]
			
			name = convertToAnsibleVariableName(name)			
			if(name=="gateway"):
				if(foundGateway):
					continue
				foundGateway = True
			
			variables[name] = data

		frame["variables"] = variables


def writeFileheader(outfile,configFileName):
	outfile.write("###\n")
	outfile.write("# created by python script convert.py\n")
	outfile.write("# Felix Sterzelmaier, Concat AG\n")
	outfile.write("# Created: "+datetime.now(tzlocal.get_localzone()).strftime("%Y-%m-%d %H:%M:%S %Z(%z)")+"\n")
	outfile.write("# Dependencies: pip install --upgrade pip\n")
	outfile.write("# Dependencies: pip install pyvmomi\n")
	outfile.write("# Dependencies: pip3.6 install --upgrade pip\n")
	outfile.write("# Dependencies: /usr/local/bin/pip3.6 install pyvmomi\n")
	outfile.write("# Test with: ansible-playbook (filename) --connection=local --check\n")
	outfile.write("# Run with: ansible-playbook (filename) --connection=local\n")
	outfile.write("# OR run with Python 2.7.5: ansible-playbook (filename) --connection=local -e 'ansible_python_interpreter=/usr/bin/python2'\n")
	outfile.write("# OR run with Python 2.7.16: ansible-playbook (filename) --connection=local -e 'ansible_python_interpreter=/usr/bin/python2.7'\n")
	outfile.write("# OR run with Python 3.6.8: ansible-playbook (filename) --connection=local -e 'ansible_python_interpreter=/usr/bin/python3'\n")
	outfile.write("# Run on: 10.10.5.239/olant-ansible as user olant in path /home/olant/synergy-ansible/feste-script/output\n")
	outfile.write("# Before reading this playbook please read the README.txt and the sourcecode of convert.py first!\n")
	outfile.write("###\n")
	outfile.write("---\n")
	outfile.write("- hosts: localhost\n")
	outfile.write("  vars:\n")
	outfile.write("    config: \""+configFileName+"\"\n")
	outfile.write("  tasks:\n")
	outfile.write("\n")
		


def writeTimelocale(nr,name):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+name+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		outfile.write("     - name: Configure time locale in en_US.UTF-8\n")
		outfile.write("       oneview_appliance_time_and_locale_configuration:\n")
		outfile.write("         config: \"{{ config }}\"\n")
		outfile.write("         state: present\n")
		outfile.write("         data:\n")
		outfile.write("             locale: en_US.UTF-8\n")
		outfile.write("             timezone: UTC\n")
		outfile.write("             ntpServers:\n")
		outfile.write("                 - "+frame["variables"]["gateway"]+"\n")
		outfile.write("       delegate_to: localhost\n")
		outfile.write("\n")
		outfile.close()
		
		

def writeAddresspoolsubnet(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		outfile.close()
		
		
		
	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabsubnets)
	
	
	variablesHead = []
	
	for col in range(worksheet.ncols):
		name = convertToAnsibleVariableName(worksheet.cell_value(0,col))
		variablesHead.append(name)
	print(variablesHead)
	
	for row in range(1,worksheet.nrows):
		variablesOneSubnet = {}
		for col in range(worksheet.ncols):
			val = str(worksheet.cell_value(row,col))
			
			if(val=="#TODO" or val=="n/a" or val.startswith("#TODO")):
				val = ""
			
			if(val.find("#TODO") != -1):
				pos = val.find("#TODO")
				val = val[:pos-1]
			
			if(val!=""):
				variablesOneSubnet[variablesHead[col]] = val
		writeAddresspoolsubnetOne(nr,filenamepart,variablesOneSubnet)


		
def writeAddresspoolsubnetOne(nr,filenamepart,variablesOneSubnet):
	print(variablesOneSubnet)
	print()
	
	if(not "zone" in variablesOneSubnet):
		print("variablesOneSubnet missing zone!")
		return
		
	if(not "name" in variablesOneSubnet):
		print("variablesOneSubnet missing name!")
		return
		
	if(not "type" in variablesOneSubnet):
		print("variablesOneSubnet missing typ!")
		return

	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'a')

		if(variablesOneSubnet["zone"].find(frame["letter"]) != -1):
			if(variablesOneSubnet["type"]=="Subnet"):
				if(not "subnetid" in variablesOneSubnet):
					print("variablesOneSubnet missing subnetid!")
					return
					
				if(not "subnetmask" in variablesOneSubnet):
					print("variablesOneSubnet missing subnetmask!")
					return

				outfile.write("     - name: Create subnet "+variablesOneSubnet["subnetid"]+"\n")
				outfile.write("       oneview_id_pools_ipv4_subnet:\n")
				outfile.write("         config: \"{{ config }}\"\n")
				outfile.write("         state: present\n")
				outfile.write("         data:\n")
				outfile.write("             name: "+variablesOneSubnet["subnetid"]+"_Subnet\n")
				outfile.write("             type: Subnet\n")
				outfile.write("             networkId: "+variablesOneSubnet["subnetid"]+"\n")
				outfile.write("             subnetmask: "+variablesOneSubnet["subnetmask"]+"\n")
				
				if("gateway" in variablesOneSubnet):
					outfile.write("             gateway: "+variablesOneSubnet["gateway"]+"\n")
				if("domain" in variablesOneSubnet):
					outfile.write("             domain: "+variablesOneSubnet["domain"]+"\n")
				if("dnsserver1" in variablesOneSubnet):
					outfile.write("             dnsServers:\n")
					outfile.write("                 - "+variablesOneSubnet["dnsserver1"]+"\n")
				if("dnsserver2" in variablesOneSubnet):
					outfile.write("                 - "+variablesOneSubnet["dnsserver2"]+"\n")
				if("dnsserver3" in variablesOneSubnet):
					outfile.write("                 - "+variablesOneSubnet["dnsserver3"]+"\n")
				outfile.write("       delegate_to: localhost\n")
				outfile.write("\n")
					
			if(variablesOneSubnet["type"]=="Range"):
				if(not "rangestart" in variablesOneSubnet):
					print("variablesOneSubnet "+variablesOneSubnet["name"]+" missing rangestart!")
					return
					
				if(not "rangeend" in variablesOneSubnet):
					print("variablesOneSubnet "+variablesOneSubnet["name"]+" missing rangeend!")
					return

				outfile.write("     - set_fact: subnet_uri=\"{{ id_pools_ipv4_subnet[\"uri\"] }}\" \n")
				outfile.write("     - name: Create IPV4 range "+variablesOneSubnet["name"]+"\n")
				outfile.write("       oneview_id_pools_ipv4_range:\n")
				outfile.write("         config: \"{{ config }}\"\n")
				outfile.write("         state: present\n")
				outfile.write("         data:\n")
				outfile.write("             name: "+variablesOneSubnet["name"]+"\n")
				outfile.write("             subnetUri: \"{{ subnet_uri }}\" \n")
				outfile.write("             type: Range\n")
				outfile.write("             rangeCategory: Custom\n")
				outfile.write("             startAddress: "+variablesOneSubnet["rangestart"]+"\n")
				outfile.write("             endAddress: "+variablesOneSubnet["rangeend"]+"\n")
				outfile.write("       delegate_to: localhost\n")
				outfile.write("\n")

		outfile.close()

def findFrames():
	global variablesAll
	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabgeneral)
	

	columnNamesInt = columnCharToInt(columnNames)
	for row in range(worksheet.nrows):
		name = str(worksheet.cell_value(row,columnNamesInt))
		
		if(name==""):
			continue
			
		if(name=="OneView Hostname"):
			
			for col in range(columnCharToInt(columnNames)+1,worksheet.ncols):
				data = str(worksheet.cell_value(row,col))
				if(data=="" or data=="#TODO" or data=="n/a" or data.startswith("#TODO")):
					continue
					
				tmp = {"name":data,"column":col,"letter":data[0]}
				variablesAll.append(tmp)
			break


def writeConfigs():
	for frame in variablesAll:
		configFile = outputfolder+"/"+config_prefx+frame["letter"]+config_sufix
		outfile = open(configFile,'w')
		outfile.write("{"+"\n")
		outfile.write("    \"ip\": \""+frame["variables"]["oneview_hostname"].lower()+"."+frame["variables"]["domain_name"]+"\","+"\n")
		outfile.write("    \"credentials\": {"+"\n")
		outfile.write("        \"userName\": \"Administrator\","+"\n")
		outfile.write("        \"password\": \""+frame["variables"]["administrator_passwort"]+"\""+"\n")
		outfile.write("    },"+"\n")
		outfile.write("    \"image_streamer_ip\": \"\","+"\n") #todo, bleibt erstmal leer
		outfile.write("    \"api_version\": 1000"+"\n")
		outfile.write("}"+"\n")
		outfile.close()
	


def writeCreatenetwork(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		outfile.close()

	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabnets)
	
	variablesHead = []
	
	for col in range(worksheet.ncols):
		name = convertToAnsibleVariableName(worksheet.cell_value(0,col))
		variablesHead.append(name)
	print(variablesHead)
	
	for row in range(1,worksheet.nrows):
		variablesOneNet = {}
		for col in range(worksheet.ncols):
			val = worksheet.cell_value(row,col)
			
			if(isinstance(val,float)):
				val = str(int(val))
			
			if(val=="#TODO" or val=="n/a" or val.startswith("#TODO")):
				val = ""
			
			if(val.find("#TODO") != -1):
				pos = val.find("#TODO")
				val = val[:pos-1]
			
			if(val!=""):
				variablesOneNet[variablesHead[col]] = val
		writeCreatenetworkOne(nr,filenamepart,variablesOneNet)


def writeCreatenetworkOne(nr,filenamepart,variablesOneNet):
	print()
	print(variablesOneNet)
	
	if(not "zone" in variablesOneNet):
		print("variablesOneNet missing zone!")
		return
	
	if(not "ipv4subnet" in variablesOneNet):
		print("variablesOneNet missing ipv4subnet!")
		return
		
	if(not "name" in variablesOneNet):
		print("variablesOneNet missing name!")
		return
		
	if(not "vlanid" in variablesOneNet):
		print("variablesOneNet missing vlanid!")
		return

	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'a')
		
		if(variablesOneNet["zone"].find(frame["letter"]) != -1):
			
			if(variablesOneNet["ipv4subnet"]!="None"):
			
			
			
				outfile.write("    - name: Gather facts about ID Pools IPV4 Subnets by name\n")
				outfile.write("      oneview_id_pools_ipv4_subnet_facts:\n")
				outfile.write("        config: \"{{ config }}\"\n")
				outfile.write("        name: '"+variablesOneNet["ipv4subnet"]+"_Subnet'\n")
				outfile.write("      delegate_to: localhost\n")
				outfile.write("\n")
				outfile.write("    - set_fact: subnet_uri=\"{{ id_pools_ipv4_subnets[0].uri }}\"\n")
				outfile.write("    - debug: var=subnet_uri\n")
				outfile.write("\n")
			
			outfile.write("    - name: Create an Ethernet Network\n")
			outfile.write("      oneview_ethernet_network:\n")
			outfile.write("        config: \"{{ config }}\"\n")
			outfile.write("        state: present\n")
			outfile.write("        data:\n")
			outfile.write("            name:                   \""+variablesOneNet["name"]+"\"\n")
			outfile.write("            ethernetNetworkType:    "+variablesOneNet["type"]+"\n")
			outfile.write("            type:    ethernet-networkV4\n")
			outfile.write("            purpose:                Management\n")
			outfile.write("            smartLink:              "+variablesOneNet["smartlink"].lower()+"\n")
			outfile.write("            privateNetwork:         "+variablesOneNet["privatenetwork"].lower()+"\n")
			outfile.write("            vlanId:                 "+variablesOneNet["vlanid"]+"\n")
			if(variablesOneNet["ipv4subnet"]!="None"):
				outfile.write("            subnetUri:              \"{{ subnet_uri }}\"\n")
			outfile.write("            bandwidth:\n")
			outfile.write("               typicalBandwidth: "+variablesOneNet["preferredbandwidth"]+"\n")
			outfile.write("               maximumBandwidth: "+variablesOneNet["maxbandwidth"]+"\n")
			outfile.write("      delegate_to: localhost\n")
			outfile.write("\n")
		
		outfile.close()
		
def convertToAnsibleVariableName(n):
	n = str(n)
	n = n.lower().replace(" ","_").replace("-","_")
	n = re.sub(r'\W+', '', n)
	return n
		
def writeLogicalInterconnectGroup(nr,filenamepart):
	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabnets)
	
	variablesHead = []
	variables = []
	
	for col in range(worksheet.ncols):
		name = convertToAnsibleVariableName(worksheet.cell_value(0,col))
		variablesHead.append(name)
	print(variablesHead)
	
	for row in range(1,worksheet.nrows):
		variablesOneNet = {}
		for col in range(worksheet.ncols):
			val = worksheet.cell_value(row,col)
			
			if(isinstance(val,float)):
				val = str(int(val))
			
			if(val=="#TODO" or val=="n/a" or val.startswith("#TODO")):
				val = ""
			
			if(val.find("#TODO") != -1):
				pos = val.find("#TODO")
				val = val[:pos-1]
			
			variablesOneNet[variablesHead[col]] = val
		variables.append(variablesOneNet)
		print(variables)
	
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		
		#BEGIN
		outfile.write('#---------------------------- Logical Interconnect Group lig_sas'+"\n")
		outfile.write('     - name: Create logical Interconnect Group lig_sas'+"\n")
		outfile.write('       oneview_sas_logical_interconnect_group:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         state: present'+"\n")
		outfile.write('         data:'+"\n")
		outfile.write('             name:                   "lig_sas"'+"\n")
		outfile.write('             enclosureType:          "SY12000"'+"\n")
		outfile.write('             redundancyType:         ""'+"\n")
		outfile.write('             type:                   "sas-logical-interconnect-groupV2"'+"\n")
		outfile.write('             interconnectBaySet:     1'+"\n")
		outfile.write('             enclosureIndexes:'+"\n")
		outfile.write('                 - 1'+"\n")
		outfile.write('             interconnectMapTemplate:'+"\n")
		outfile.write('                 interconnectMapEntryTemplates:'+"\n")
		outfile.write('                     - permittedInterconnectTypeUri: "/rest/sas-interconnect-types/Synergy12GbSASConnectionModule"'+"\n")
		outfile.write('                       enclosureIndex:               "1"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    4'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('                             - relativeValue:    1'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('                     - permittedInterconnectTypeUri: "/rest/sas-interconnect-types/Synergy12GbSASConnectionModule"'+"\n")
		outfile.write('                       enclosureIndex:               "1"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    1'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('                             - relativeValue:    1'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('       delegate_to: localhost'+"\n")
		outfile.write(' '+"\n")
		outfile.write('#---------------------------- Logical Interconnect Group lig_vc'+"\n")
		
		for v in variables:
			if(frame["letter"] in v["zone"]):
				outfile.write('     - name: Get uri for network '+v["name"]+"\n")
				outfile.write('       oneview_ethernet_network_facts:'+"\n")
				outfile.write('         config:         "{{ config }}"'+"\n")
				outfile.write('         name:           "'+v["name"]+'"'+"\n")
				outfile.write('     - set_fact:         var_'+convertToAnsibleVariableName(v["name"])+'="{{ethernet_networks.uri}}"'+"\n")
				outfile.write("\n")

		outfile.write('     - name: Create logical Interconnect Group lig_vc'+"\n")
		outfile.write('       oneview_logical_interconnect_group:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         state: present'+"\n")
		outfile.write('         data:'+"\n")
		outfile.write('             name:                   "lig_vc"'+"\n")
		outfile.write('             enclosureType:          "SY12000"'+"\n")
		outfile.write('             type:                   "logical-interconnect-groupV6"'+"\n")
		outfile.write('             redundancyType:         "HighlyAvailable"'+"\n")
		outfile.write('             interconnectBaySet:     3'+"\n")
		outfile.write('             ethernetSettings:           '+"\n")
		outfile.write('                 type:                           "EthernetInterconnectSettingsV5"'+"\n")
		outfile.write('                 enableIgmpSnooping:             false'+"\n")
		outfile.write('                 igmpIdleTimeoutInterval:        260'+"\n")
		outfile.write('                 enableNetworkLoopProtection:    true'+"\n")
		outfile.write('                 enablePauseFloodProtection:     true'+"\n")
		outfile.write('                 enableRichTLV:                  false'+"\n")
		outfile.write('                 enableTaggedLldp:               true'+"\n")
		outfile.write('                 enableStormControl:             false'+"\n")
		outfile.write('                 stormControlThreshold:          0'+"\n")
		outfile.write('                 enableFastMacCacheFailover:     true'+"\n")
		outfile.write('                 macRefreshInterval:             5'+"\n")
		outfile.write('             enclosureIndexes:'+"\n")
		outfile.write('                 - 1'+"\n")
		outfile.write('                 - 2'+"\n")
		outfile.write('                 - 3'+"\n")
		outfile.write('             interconnectMapTemplate:'+"\n")
		outfile.write('                 interconnectMapEntryTemplates:'+"\n")
		outfile.write('                     - permittedInterconnectTypeName: "Synergy 20Gb Interconnect Link Module"'+"\n")
		outfile.write('                       enclosureIndex:               "2"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    3'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('                             - relativeValue:    2'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('                     - permittedInterconnectTypeName: "Synergy 20Gb Interconnect Link Module"'+"\n")
		outfile.write('                       enclosureIndex:               "3"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    6'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('                             - relativeValue:    3'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('                     - permittedInterconnectTypeName: "Synergy 20Gb Interconnect Link Module"'+"\n")
		outfile.write('                       enclosureIndex:               "3"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    3'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('                             - relativeValue:    3'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('                     - permittedInterconnectTypeName: "Synergy 20Gb Interconnect Link Module"'+"\n")
		outfile.write('                       enclosureIndex:               "1"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    1'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('                             - relativeValue:    6'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('                     - permittedInterconnectTypeName: "Virtual Connect SE 40Gb F8 Module for Synergy"'+"\n")
		outfile.write('                       enclosureIndex:               "2"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    6'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('                             - relativeValue:    2'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('                     - permittedInterconnectTypeName: "Virtual Connect SE 40Gb F8 Module for Synergy"'+"\n")
		outfile.write('                       enclosureIndex:               "1"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    1'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('                             - relativeValue:    3'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('             internalNetworkUris:'+"\n")
		
		for v in variables:
			if(frame["letter"] in v["zone"] and v["uplinkset"]=="Internal"):
				outfile.write('                - "{{var_'+convertToAnsibleVariableName(v["name"])+'}}"    # networkName: '+v["name"]+' '+"\n")

		outfile.write('             uplinkSets:'+"\n")
		outfile.write('                 - name:                  "iSCSI-Deployment"'+"\n")
		outfile.write('                   networkType:           "Ethernet"'+"\n")
		outfile.write('                   ethernetNetworkType:   "ImageStreamer"'+"\n")
		outfile.write('                   mode:                  "Auto"'+"\n")
		outfile.write('                   networkUris:'+"\n")

		for v in variables:
			if(frame["letter"] in v["zone"] and v["uplinkset"]=="iSCSI-Deployment"):
				outfile.write('                         - "{{var_'+convertToAnsibleVariableName(v["name"])+'}}"    # networkName: '+v["name"]+' '+"\n")

		outfile.write('                   logicalPortConfigInfos:'+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 63'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                             - relativeValue: 6'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                             - relativeValue: 2'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 1'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('                             - relativeValue: 62'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                             - relativeValue: 3'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 62'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                             - relativeValue: 6'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                             - relativeValue: 2'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 1'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('                             - relativeValue: 63'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                             - relativeValue: 3'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                 - name:             "Uplink_Prod"'+"\n")
		outfile.write('                   networkType:      "Ethernet"'+"\n")
		outfile.write('                   mode:             "Auto"'+"\n")
		outfile.write('                   lacpTimer:        "Long"'+"\n")
		outfile.write('                   networkUris:'+"\n")
		
		for v in variables:
			if(frame["letter"] in v["zone"] and v["uplinkset"]=="Uplink_Prod"):
				outfile.write('                         - "{{var_'+convertToAnsibleVariableName(v["name"])+'}}"    # networkName: '+v["name"]+' '+"\n")

		outfile.write('                   logicalPortConfigInfos:'+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 6'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                             - relativeValue: 2'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('                             - relativeValue: 71'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 1'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('                             - relativeValue: 3'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                             - relativeValue: 71'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 1'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('                             - relativeValue: 66'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                             - relativeValue: 3'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 6'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                             - relativeValue: 66'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                             - relativeValue: 2'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('       delegate_to: localhost'+"\n")
		outfile.write(''+"\n")
		#END
		
		outfile.close()


def writeOSdeploymentServer(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		
		#BEGIN
		outfile.write('  tasks:'+"\n")
		outfile.write('    - name: Ensure that the Deployment Server is present'+"\n")
		outfile.write('      oneview_os_deployment_server:'+"\n")
		outfile.write('        config: "{{ config }}"'+"\n")
		outfile.write('        state: present'+"\n")
		outfile.write('        data:'+"\n")
		outfile.write('          name: "'+frame["variables"]["oneview_hostname"]+'_OSDS"'+"\n")		 				#CODE oneview_hostname+"_OSDS"
		outfile.write('          mgmtNetworkName: "oob-mgmt"'+"\n")
		outfile.write('          applianceName: "'+frame["letter"]+'-Master2, appliance 2"'+"\n")		 #CODE Zone+"-Master2, appliance 2"
		outfile.write('          deplManagersType: "Image Streamer"'+"\n")
		outfile.write(''+"\n")
		outfile.write('    - debug: var=os_deployment_server'+"\n")
		outfile.write("\n")
		#END
		outfile.close()
		
def writeNetworkset(nr,filenamepart):
	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabnets)
	
	variablesHead = []
	variables = []
	networksets = []
	
	for col in range(worksheet.ncols):
		name = convertToAnsibleVariableName(worksheet.cell_value(0,col))
		variablesHead.append(name)
	
	for row in range(1,worksheet.nrows):
		variablesOneNet = {}
		for col in range(worksheet.ncols):
			val = worksheet.cell_value(row,col)
			
			if(isinstance(val,float)):
				val = str(int(val))
			
			if(val=="#TODO" or val=="n/a" or val.startswith("#TODO")):
				val = ""
			
			if(val.find("#TODO") != -1):
				pos = val.find("#TODO")
				val = val[:pos-1]
			
			variablesOneNet[variablesHead[col]] = val
			
			if(variablesHead[col]=="networkset"):
				if(val!=""):
					if(not val in networksets):
						networksets.append(val)
			
		variables.append(variablesOneNet)
	
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)

		#BEGIN
		for networkset in networksets:
			outfile.write('    - name: Create Network Set '+networkset+"\n")
			outfile.write('      oneview_network_set:'+"\n")
			outfile.write('        config: "{{ config }}"'+"\n")
			outfile.write('        state: present'+"\n")
			outfile.write('        data:'+"\n")
			outfile.write('          type: "network-setV4"'+"\n")
			outfile.write('          name: "'+networkset+'"'+"\n")
			outfile.write('          networkUris:'+"\n") # it is possible to pass names instead of URIs
			for v in variables:
				if(v["networkset"] == networkset):
					if(frame["letter"] in v["zone"]):
						outfile.write('            - '+v["name"]+"\n")
			outfile.write('      delegate_to: localhost'+"\n")
			outfile.write("\n")
		#END
		outfile.close()



def writeEnclosureGroup(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		
		#BEGIN
		outfile.write('#---------------------------- Enclosure Group  Nublar_EG_3e'+"\n")
		outfile.write('     - name: Get uri for LIG lig_sas'+"\n")
		outfile.write('       oneview_sas_logical_interconnect_group_facts:'+"\n")
		outfile.write('         config:         "{{ config }}"'+"\n")
		outfile.write('         name:           "lig_sas"'+"\n")
		outfile.write('     - set_fact:         var_lig_sas="{{sas_logical_interconnect_groups[0].uri}}"'+"\n")
		outfile.write(' '+"\n")
		outfile.write('     - name: Get uri for LIG lig_vc'+"\n")
		outfile.write('       oneview_logical_interconnect_group_facts:'+"\n")
		outfile.write('         config:         "{{ config }}"'+"\n")
		outfile.write('         name:           "lig_vc"'+"\n")
		outfile.write('     - set_fact:         var_lig_vc="{{logical_interconnect_groups[0].uri}}"'+"\n")
		outfile.write(''+"\n")
		outfile.write('     - name: Get uri for oobm-mgmt Pool'+"\n")
		outfile.write('       oneview_ethernet_network_facts:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         name: "oob-mgmt"'+"\n")
		outfile.write('     - set_fact:         var_oob_mgmt_subnet="{{ ethernet_networks.subnetUri }}"'+"\n")
		outfile.write(''+"\n")
		outfile.write('     - name: Get uri for oob-mgmt_Range'+"\n")
		outfile.write('       oneview_id_pools_ipv4_range_facts:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         subnetUri: "{{ var_oob_mgmt_subnet }}"'+"\n")
		outfile.write('     - set_fact: var_oob_mgmt_subnet_range="{{ id_pools_ipv4_ranges[0].uri }}"'+"\n")
		outfile.write(' '+"\n")
		outfile.write('     - name: Create Enclosure Group Nublar_EG_3e'+"\n")
		outfile.write('       oneview_enclosure_group:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         state: present'+"\n")
		outfile.write('         data:'+"\n")
		outfile.write('             name:                                   "Nublar_EG_3e"'+"\n")
		outfile.write('             ipAddressingMode:                       "IpPool"'+"\n")
		outfile.write('             ipRangeUris:'+"\n")
		outfile.write('               - "{{ var_oob_mgmt_subnet_range }}"'+"\n")
		outfile.write('             osDeploymentSettings:'+"\n")
		outfile.write('               manageOSDeployment: true'+"\n")
		outfile.write('               deploymentModeSettings:'+"\n")
		outfile.write('                 deploymentMode: Internal'+"\n")
		outfile.write('             enclosureCount:                         3'+"\n")
		outfile.write('             powerMode:                              RedundantPowerFeed'+"\n")
		outfile.write('             interconnectBayMappings:'+"\n")
		outfile.write('                 - interconnectBay:                  1'+"\n")
		outfile.write('                   enclosureIndex:                   1'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_sas}}"  # lig name  lig_sas '+"\n")
		outfile.write('                 - interconnectBay:                  1'+"\n")
		outfile.write('                   enclosureIndex:                   2'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_sas}}"  # lig name  lig_sas '+"\n")
		outfile.write('                 - interconnectBay:                  1'+"\n")
		outfile.write('                   enclosureIndex:                   3'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_sas}}"  # lig name  lig_sas '+"\n")
		outfile.write('                 - interconnectBay:                  3'+"\n")
		outfile.write('                   enclosureIndex:                   1'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_vc}}"  # lig name  lig_vc '+"\n")
		outfile.write('                 - interconnectBay:                  3'+"\n")
		outfile.write('                   enclosureIndex:                   2'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_vc}}"  # lig name  lig_vc '+"\n")
		outfile.write('                 - interconnectBay:                  3'+"\n")
		outfile.write('                   enclosureIndex:                   3'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_vc}}"  # lig name  lig_vc '+"\n")
		outfile.write('                 - interconnectBay:                  4'+"\n")
		outfile.write('                   enclosureIndex:                   1'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_sas}}"  # lig name  lig_sas '+"\n")
		outfile.write('                 - interconnectBay:                  4'+"\n")
		outfile.write('                   enclosureIndex:                   2'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_sas}}"  # lig name  lig_sas '+"\n")
		outfile.write('                 - interconnectBay:                  4'+"\n")
		outfile.write('                   enclosureIndex:                   3'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_sas}}"  # lig name  lig_sas '+"\n")
		outfile.write('                 - interconnectBay:                  6'+"\n")
		outfile.write('                   enclosureIndex:                   1'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_vc}}"  # lig name  lig_vc '+"\n")
		outfile.write('                 - interconnectBay:                  6'+"\n")
		outfile.write('                   enclosureIndex:                   2'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_vc}}"  # lig name  lig_vc '+"\n")
		outfile.write('                 - interconnectBay:                  6'+"\n")
		outfile.write('                   enclosureIndex:                   3'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_vc}}"  # lig name  lig_vc '+"\n")
		outfile.write('       delegate_to: localhost'+"\n")
		outfile.write("\n")
		#END
		outfile.close()
	   
	   

def writeLogicatEnclosure(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		
		#BEGIN
		outfile.write('#firmware_baseline_uri: "/rest/firmware-drivers/SPP_2018_11_20190205_for_HPE_Synergy_Z7550-96592"  #TODO später'+"\n")
		outfile.write("\n")
		outfile.write('	 - name: Gather information about Enclosure '+frame["letter"]+'-Master1'+"\n")
		outfile.write('       oneview_enclosure_info:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         name: "'+frame["letter"]+'-Master1"'+"\n")
		outfile.write('       no_log: true'+"\n")
		outfile.write('       delegate_to: localhost'+"\n")
		outfile.write('       register: result'+"\n")
		outfile.write("\n")
		outfile.write('     - set_fact:'+"\n")
		outfile.write('         var_master1uri="{{ result.enclosures[0].uri }}"'+"\n")
		outfile.write("\n")
		outfile.write('	 - name: Gather information about Enclosure '+frame["letter"]+'-Master2'+"\n")
		outfile.write('       oneview_enclosure_info:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         name: "'+frame["letter"]+'-Master2"'+"\n")
		outfile.write('       no_log: true'+"\n")
		outfile.write('       delegate_to: localhost'+"\n")
		outfile.write('       register: result'+"\n")
		outfile.write("\n")
		outfile.write('     - set_fact:'+"\n")
		outfile.write('         var_master2uri="{{ result.enclosures[0].uri }}"'+"\n")
		outfile.write("\n")
		outfile.write('	 - name: Gather information about Enclosure '+frame["letter"]+'-Slave'+"\n")
		outfile.write('       oneview_enclosure_info:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         name: "'+frame["letter"]+'-Slave"'+"\n")
		outfile.write('       no_log: true'+"\n")
		outfile.write('       delegate_to: localhost'+"\n")
		outfile.write('       register: result'+"\n")
		outfile.write("\n")
		outfile.write('     - set_fact:'+"\n")
		outfile.write('         var_slaveuri="{{ result.enclosures[0].uri }}"'+"\n")
		outfile.write("\n")
		outfile.write('     - name: Gather facts about Enclosure Groups'+"\n")
		outfile.write('       oneview_enclosure_group_facts:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         name: "Nublar_EG_3e"'+"\n") #CODE gleicher Name wie in enclosuregroup
		outfile.write('       delegate_to: localhost'+"\n")
		outfile.write('     - set_fact: var_enclosure_group_uri="{{ enclosure_groups.uri }}"'+"\n")
		outfile.write("\n")
		outfile.write('     - name: Create a Logical Enclosure (available only on HPE Synergy)'+"\n")
		outfile.write('       oneview_logical_enclosure:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         state: present'+"\n")
		outfile.write('         data:'+"\n")
		outfile.write('             name: "ComputeBlock'+frame["letter"]+'"'+"\n")
		outfile.write('             enclosureUris:'+"\n")
		outfile.write('               - var_master1uri'+"\n")
		outfile.write('               - var_master2uri'+"\n")
		outfile.write('               - var_slaveuri'+"\n")
		outfile.write('             enclosureGroupUri: "{{ var_enclosure_group_uri }}"'+"\n")
		outfile.write('       delegate_to: localhost'+"\n")
		outfile.write("\n")
		#END
		outfile.close()
		
		
		
		
def main():
	findFrames()
	fillVariables()
	
	print(variablesAll)
	print()
	
	writeConfigs()
	writeTimelocale("01","ntp")
	writeAddresspoolsubnet("02","subnetrange")
	####3 später: Register hypervisor manager
	writeCreatenetwork("04","ethernetnetworkwithassociatedsubnet")
	writeOSdeploymentServer("05","osds")
	writeNetworkset("06","networkset")
	writeLogicalInterconnectGroup("07","logicalinterconnectgroup") #https://github.com/HewlettPackard/oneview-ansible/blob/master/examples/synergy_environment_setup.yml
	writeEnclosureGroup("08","enclosuregroup")
	writeLogicatEnclosure("09","logicalenclosure")
	#10 storagesystem
	
#start
main()



