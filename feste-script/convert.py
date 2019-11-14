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
exceltabstorage = "Nimble"
exceltabhypervisor = "Synergy-VMware"
exceltabnimble = "Synergy-Nimble"
outputfolder = "output"

############################################################################
############## Only change Variables above this line #######################
############################################################################

variablesAll = []
variablesNimbleAll = {}
variablesHypervisorAll = {}
varaiblesClustersAll = []

#change working directory to script path/xlsx path
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)





def columnCharToInt(c):
	c = c.lower()
	return string.ascii_lowercase.index(c)

def writeFileheader(outfile,configFileName):
	filename = os.path.basename(outfile.name)
	print("now: "+filename)
	outfile.write("###\n")
	outfile.write("# created by python script convert.py\n")
	outfile.write("# Felix Sterzelmaier, Concat AG\n")
	outfile.write("# Created: "+datetime.now(tzlocal.get_localzone()).strftime("%Y-%m-%d %H:%M:%S %Z(%z)")+"\n")
	outfile.write("# Dependencies: pip install --upgrade pip\n")
	outfile.write("# Dependencies: pip install pyvmomi\n")
	outfile.write("# Run with: ansible-playbook -c local -i localhost, "+filename+"\n")
	outfile.write("# Run on: 10.10.5.239/olant-ansible as user olant in path /home/olant/synergy-ansible/feste-script/output\n")
	outfile.write("# Before reading this playbook please read the README.txt and the sourcecode of convert.py first!\n")
	outfile.write("###\n")
	outfile.write("---\n")
	outfile.write("- hosts: localhost\n")
	outfile.write("  vars:\n")
	outfile.write('    config: "{{ playbook_dir }}/'+configFileName+'"\n')
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


def findHypervisor():
	global variablesHypervisorAll,varaiblesClustersAll
	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabhypervisor)

	start = False
	end = False
	for row in range(worksheet.nrows):
		name = str(worksheet.cell_value(row,0))
		
		if(name==""):
			continue
			
		if(name=="Type"):
			start = True
			
		if(not start):
			continue
			
		if(end):
			continue
			
		if(name=="High availability"):
			end = True
		
		#found valid line
		data = worksheet.cell_value(row,1)
		if(isinstance(data,float)):
			data = str(int(data))
		
		if(data=="" or data=="#TODO" or data=="n/a" or data.startswith("#TODO")):
			continue
		
		if(data.find("#TODO") != -1):
			pos = data.find("#TODO")
			data = data[:pos-1]
		
		name = convertToAnsibleVariableName(name)			
		variablesHypervisorAll[name] = data
		
		
	#clusters
	start = False
	for row in range(worksheet.nrows):
		name = str(worksheet.cell_value(row,3))
		
		if(name==""):
			continue
			
		if(name=="Cluster"):
			start = True
			continue
			
		if(not start):
			continue
		
		#found valid line
		if(not name in varaiblesClustersAll):
			varaiblesClustersAll.append(name)	

def findNimbles():
	global variablesNimbleAll
	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabstorage)
	

	columnNamesInt = columnCharToInt(columnNames)
	for row in range(worksheet.nrows):
		name = str(worksheet.cell_value(row,columnNamesInt))
		
		if(name==""):
			continue
			
		if(name=="Storage System Name"):
			
			for col in range(columnCharToInt(columnNames)+1,worksheet.ncols):
				data = str(worksheet.cell_value(row,col))
				if(data=="" or data=="#TODO" or data=="n/a" or data.startswith("#TODO") or str(worksheet.cell_value(row-1,col))=="Bemerkungen"):
					continue
					
				tmp = {"name":data,"column":col,"letter":data[0]}
				variablesNimbleAll[data[0]] = tmp
			break
	
	#ehemals fillvariablesnimble
	for l in variablesNimbleAll:
		nimble = variablesNimbleAll[l]
		variables = {}
		start = False
		end = False
		for row in range(worksheet.nrows):
			name = str(worksheet.cell_value(row,columnNamesInt))
			
			if(name==""):
				continue
				
			if(name=="Group name"):
				start = True
				
			if(not start):
				continue
				
			if(end):
				continue
				
			if(name=="NTP (time) server IP address"):
				end = True
			
			#found valid line
			columnDataInt = nimble["column"]
			data = str(worksheet.cell_value(row,columnDataInt))
			if(data=="" or data=="#TODO" or data=="n/a" or data.startswith("#TODO")):
				continue
			
			if(data.find("#TODO") != -1):
				pos = data.find("#TODO")
				data = data[:pos-1]
			
			name = convertToAnsibleVariableName(name)			

			
			variables[name] = data
		nimble["variables"] = variables

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
	
	#ehemals fillvariables
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
			outfile.write("            purpose:                \""+variablesOneNet["purpose"]+"\"\n")
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
	   
	   

def writeLogicalEnclosure(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		
		#BEGIN
		outfile.write('  - name: Gather facts about SPP\n')
		outfile.write('    oneview_firmware_driver_facts:\n')
		outfile.write('      config: "{{ config }}"\n')
		outfile.write('    no_log: true\n')
		outfile.write('    delegate_to: localhost\n')
		outfile.write('    register: result\n')
		outfile.write('\n')
		outfile.write('  - set_fact:\n')
		outfile.write('      firmware_baseline_uri="{{ result.ansible_facts.firmware_drivers[0].uri }}"\n')
		outfile.write("\n")
		outfile.write('  - name: Gather information about Enclosure '+frame["letter"]+'-Master1'+"\n")
		outfile.write('    oneview_enclosure_info:'+"\n")
		outfile.write('      config: "{{ config }}"'+"\n")
		outfile.write('      name: "'+frame["letter"]+'-Master1"'+"\n")
		outfile.write('    no_log: true'+"\n")
		outfile.write('    delegate_to: localhost'+"\n")
		outfile.write('    register: result'+"\n")
		outfile.write("\n")
		outfile.write('  - set_fact:'+"\n")
		outfile.write('      var_master1uri="{{ result.enclosures[0].uri }}"'+"\n")
		outfile.write("\n")
		outfile.write('  - name: Gather information about Enclosure '+frame["letter"]+'-Master2'+"\n")
		outfile.write('    oneview_enclosure_info:'+"\n")
		outfile.write('      config: "{{ config }}"'+"\n")
		outfile.write('      name: "'+frame["letter"]+'-Master2"'+"\n")
		outfile.write('    no_log: true'+"\n")
		outfile.write('    delegate_to: localhost'+"\n")
		outfile.write('    register: result'+"\n")
		outfile.write("\n")
		outfile.write('  - set_fact:'+"\n")
		outfile.write('      var_master2uri="{{ result.enclosures[0].uri }}"'+"\n")
		outfile.write("\n")
		outfile.write('  - name: Gather information about Enclosure '+frame["letter"]+'-Slave'+"\n")
		outfile.write('    oneview_enclosure_info:'+"\n")
		outfile.write('      config: "{{ config }}"'+"\n")
		outfile.write('      name: "'+frame["letter"]+'-Slave"'+"\n")
		outfile.write('    no_log: true'+"\n")
		outfile.write('    delegate_to: localhost'+"\n")
		outfile.write('    register: result'+"\n")
		outfile.write("\n")
		outfile.write('  - set_fact:'+"\n")
		outfile.write('      var_slaveuri="{{ result.enclosures[0].uri }}"'+"\n")
		outfile.write("\n")
		outfile.write('  - name: Gather facts about Enclosure Groups'+"\n")
		outfile.write('    oneview_enclosure_group_facts:'+"\n")
		outfile.write('      config: "{{ config }}"'+"\n")
		outfile.write('      name: "Nublar_EG_3e"'+"\n") #CODE gleicher Name wie in enclosuregroup
		outfile.write('    delegate_to: localhost'+"\n")
		outfile.write('  - set_fact: var_enclosure_group_uri="{{ enclosure_groups.uri }}"'+"\n")
		outfile.write("\n")
		outfile.write('  - name: Create a Logical Enclosure (available only on HPE Synergy)'+"\n")
		outfile.write('    oneview_logical_enclosure:'+"\n")
		outfile.write('      config: "{{ config }}"'+"\n")
		outfile.write('      state: present'+"\n")
		outfile.write('      data:'+"\n")
		outfile.write('        name: "ComputeBlock'+frame["letter"]+'"'+"\n")
		outfile.write('        enclosureUris:'+"\n")
		outfile.write('          - "{{ var_master1uri }}"'+"\n")
		outfile.write('          - "{{ var_master2uri }}"'+"\n")
		outfile.write('          - "{{ var_slaveuri }}"'+"\n")
		outfile.write('        enclosureGroupUri: "{{ var_enclosure_group_uri }}"'+"\n")
		outfile.write('        firmwareBaselineUri: "{{ firmware_baseline_uri }}"'+"\n")
		outfile.write('    delegate_to: localhost'+"\n")
		outfile.write("\n")
		#END
		outfile.close()
		
		

def writeStoragesystem(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		
		#BEGIN
		outfile.write('     - name: Create a Storage System "group2" '+"\n")
		outfile.write('       oneview_storage_system:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         state: present'+"\n")
		outfile.write('         data:'+"\n")
		outfile.write('           credentials:'+"\n")
		outfile.write('             ip_hostname:               "'+variablesNimbleAll[frame["letter"]]["name"].lower()+'.'+variablesNimbleAll[frame["letter"]]["variables"]["domain_name"]+'"'+"\n")
		outfile.write('             username:                  "oneview"'+"\n")
		outfile.write('             password:                  "'+frame["variables"]["administrator_passwort"]+'"'+"\n")
		outfile.write('           managedPools:                  ""'+"\n")
		outfile.write('             domain:                  "default"'+"\n")
		outfile.write('             name:                    ""'+"\n")
		outfile.write('       delegate_to: localhost'+"\n")
		outfile.write("\n")
		#END
		outfile.close()
		
		
def writeAddFirmwareBundle(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		
		#BEGIN
		outfile.write('    - name: Ensure that a firmware bundle is present\n')
		outfile.write('      oneview_firmware_bundle:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        file_path: "{{ playbook_dir }}/files/'+frame["variables"]["synergy_spp"]+'"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('    - debug: var=firmware_bundle\n')
		outfile.write('\n')
		#END
		outfile.close()
		
		
def writeSetImagestreameripInConfig(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		outfile.write('    - name: Gather facts about all OS Deployment Servers\n')
		outfile.write('      oneview_os_deployment_server_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('\n')
		outfile.write('    - set_fact:\n')
		outfile.write('        var_osds_ip="{{ os_deployment_servers[0].primaryIPV4 }}"\n')
		outfile.write('\n')
		outfile.write('    - name: load var from file\n')
		outfile.write('      include_vars:\n')
		outfile.write('        file: "{{ playbook_dir }}/'+config_prefx+frame["letter"]+config_sufix+'"\n')
		outfile.write('        name: imported_var\n')
		outfile.write('\n')
		outfile.write('    - name: append more key/values\n')
		outfile.write('      set_fact:\n')
		outfile.write('        imported_var: "{{ imported_var | default([]) | combine({ \'image_streamer_ip\': var_osds_ip }) }}"\n')
		outfile.write('\n')
		outfile.write('    - name: write var to file\n')
		outfile.write('      copy:\n')
		outfile.write('        content: "{{ imported_var | to_nice_json }}"\n')
		outfile.write('        dest: "{{ playbook_dir }}/'+config_prefx+frame["letter"]+config_sufix+'"\n')
		outfile.write('\n')
		outfile.close()
		
def writeUploadAndExtractIsArtifact(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)

		#BEGIN
		outfile.write('\n')
		outfile.write('    - name: Upload an Artifact Bundle\n')
		outfile.write('      image_streamer_artifact_bundle:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        data:\n')
		outfile.write('          localArtifactBundleFilePath: "{{ playbook_dir }}/files/'+frame["variables"]["artifact_bundle"]+'"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('\n')
		
		outfile.write('    - name: Extract an Artifact Bundle\n')
		outfile.write('      image_streamer_artifact_bundle:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: extracted\n')
		outfile.write('        data:\n')
		outfile.write('          name: "'+frame["variables"]["artifact_bundle"].replace(".zip","")+'"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('\n')
		
		#END
		outfile.close()
		
		
		
		
def writeUploadGI(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)

		#BEGIN
		outfile.write('    - name: Upload a Golden Image\n')
		outfile.write('      image_streamer_golden_image:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        data:\n')
		outfile.write('          name: "'+frame["variables"]["golden_image"].replace(".zip","")+'"\n')
		outfile.write('          description: "Release Build mit SUT und NCM"\n')
		outfile.write('          localImageFilePath: "{{ playbook_dir }}/files/'+frame["variables"]["golden_image"]+'"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('\n')
		#END
		outfile.close()
		
		
		


def writeCreatedeploymentplan(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)

		#BEGIN
		outfile.write('    - name: Retrieve GoldenImage URI\n')
		outfile.write('      image_streamer_golden_image_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        name: "'+frame["variables"]["golden_image"].replace(".zip","")+'"\n')
		outfile.write('      register: result\n')
		outfile.write('\n')
		outfile.write('    - name: Create a Deployment Plan\n')
		outfile.write('      image_streamer_deployment_plan:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        data:\n')
		outfile.write('          description: "Release Build mit SUT und NCM"\n')
		outfile.write('          name: "nublarEsxiUpdated"\n')
		outfile.write('          hpProvided: "false"\n')
		outfile.write('          oeBuildPlanName: "HPE - ESXi 6.7 - deploy with multiple management NIC HA config - 2019-07-24"\n')
		outfile.write('          goldenImageURI: "{{ golden_images[0].uri }}"\n')
		outfile.write('          type: "OEDeploymentPlanV5"\n')
		outfile.write('          customAttributes:\n')
		outfile.write('            - name: ManagementNIC\n')
		outfile.write('              constraints: "{\\"ipv4static\\":true,\\"ipv4dhcp\\":true,\\"ipv4disable\\":false,\\"parameters\\":[\\"dns1\\",\\"dns2\\",\\"gateway\\",\\"ipaddress\\",\\"mac\\",\\"netmask\\",\\"vlanid\\"]}"\n')
		outfile.write('              description: "Configuring first NIC for Teaming in ESXi"\n')
		outfile.write('              editable: true\n')
		outfile.write('              id: "edc74bf8-d469-470f-a3e2-107e5c45e750"\n')
		outfile.write('              type: nic\n')
		outfile.write('              value: null\n')
		outfile.write('              visible: true\n')
		outfile.write('            - name: DomainName\n')
		outfile.write('              constraints: "{\\"helpText\\":\\"\\"}"\n')
		outfile.write('              description: "Fully Qualified Domain Name for ESXi host"\n')
		outfile.write('              editable: true\n')
		outfile.write('              id: "55704650-ce70-4f45-85f1-f3ff4dfeaf04"\n')
		outfile.write('              type: fqdn\n')
		outfile.write('              value: "ad.nublar.de"\n')
		outfile.write('              visible: true\n')
		outfile.write('            - name: SSH\n')
		outfile.write('              constraints: "{\\"options\\":[\\"enabled\\",\\"disabled\\"]}"\n')
		outfile.write('              description: "To enable/disable and start/stop SSH in ESXi"\n')
		outfile.write('              editable: true\n')
		outfile.write('              id: "99c9c40d-1f83-48a2-9367-1028ed55513f"\n')
		outfile.write('              type: option\n')
		outfile.write('              value: enabled\n')
		outfile.write('              visible: true\n')
		outfile.write('            - name: Hostname\n')
		outfile.write('              constraints: "{\\"helpText\\":\\"\\"}"\n')
		outfile.write('              description: "Hostname for VMware ESXi host. The hostname value can be defined manually or by using the tokens. This value must conform to valid hostname requirement defined by Internet standards."\n')
		outfile.write('              editable: true\n')
		outfile.write('              id: "8b11e853-e49a-49f0-9a0d-fbd80805758f"\n')
		outfile.write('              type: hostname\n')
		outfile.write('              value: ""\n')
		outfile.write('              visible: true\n')
		outfile.write('            - name: ManagementNIC2\n')
		outfile.write('              constraints: "{\\"ipv4static\\":true,\\"ipv4dhcp\\":false,\\"ipv4disable\\":false,\\"parameters\\":[\\"mac\\",\\"vlanid\\"]}"\n')
		outfile.write('              description: "Configuring second NIC for Teaming in ESXi"\n')
		outfile.write('              editable: true\n')
		outfile.write('              id: "46c75ab3-6da7-4a2b-a575-ef18dab2d458"\n')
		outfile.write('              type: nic\n')
		outfile.write('              value: null\n')
		outfile.write('              visible: true\n')
		outfile.write('            - name: Password\n')
		outfile.write('              constraints: "{\\"options\\":[\\"\\"]}"\n')
		outfile.write('              description: "Password value must meet password complexity and minimum length requirements defined for ESXi 5.x, ESXi 6.x appropriately."\n')
		outfile.write('              editable: true\n')
		outfile.write('              id: "e6709ead-e111-4b3e-8039-0cc97f2c0120"\n')
		outfile.write('              type: password\n')
		outfile.write('              value: ""\n')
		outfile.write('              visible: true\n')
		outfile.write('\n')
		#END
		outfile.close()




def writeFilepartRESTAPILogin(outfile,host,username,password):
		outfile.write('  - name: Login to API and retrieve AUTH-Token\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: no\n')
		outfile.write('      headers:\n')
		outfile.write('        X-Api-Version: 1000\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: https://'+host+'/rest/login-sessions\n')
		outfile.write('      method: POST\n')
		outfile.write('      body_format: json\n')
		outfile.write('      body:\n')
		outfile.write('        authLoginDomain: "LOCAL"\n')
		outfile.write('        password: "'+password+'"\n')
		outfile.write('        userName: "'+username+'"\n')
		outfile.write('        loginMsgAck: "true"\n')
		outfile.write('    register: var_this\n')
		outfile.write('\n')
		outfile.write('  - set_fact: var_token=\'{{ var_this["json"]["sessionID"] }}\'\n')
		outfile.write('\n')
		outfile.write('  - debug:\n')
		outfile.write('      var: var_token\n')
		outfile.write('\n')



def writeAddHypervisorManager(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		writeFilepartRESTAPILogin(outfile,frame["variables"]["oneview_hostname"].lower()+'.'+frame["variables"]["domain_name"],"Administrator",frame["variables"]["administrator_passwort"])
		
		
		#BEGIN
		outfile.write('  - name: Initiate asynchronous registration of an external hypervisor manager with the appliance. (Using AUTH-Token) (Statuscode should be 202)\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: no\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: 1000\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: https://'+frame["variables"]["oneview_hostname"].lower()+'.'+frame["variables"]["domain_name"]+'/rest/hypervisor-managers\n')
		outfile.write('      method: POST\n')
		outfile.write('      body_format: json\n')
		outfile.write('      body:\n')
		outfile.write('        type: "HypervisorManagerV2"\n')
		outfile.write('        name: "'+variablesHypervisorAll["hostname"]+'"\n')
		outfile.write('        username: "'+variablesHypervisorAll["username"]+'"\n')
		outfile.write('        password: "'+variablesHypervisorAll["password"]+'"\n')
		outfile.write('        hypervisorType: "Vmware"\n')
		outfile.write('        preferences:\n')
		outfile.write('          type: "Vmware"\n')
		outfile.write('          drsEnabled: '+("true" if (variablesHypervisorAll["distributed_resource_scheduler"]=="Enabled") else "false")+'\n')
		outfile.write('          haEnabled: '+("true" if (variablesHypervisorAll["high_availability"]=="Enabled") else "false")+'\n')
		outfile.write('          distributedSwitchVersion: "'+variablesHypervisorAll["distributed_vswitch_version"]+'"\n')
		outfile.write('          distributedSwitchUsage: "'+variablesHypervisorAll["use_distributed_vswitch_for"]+'"\n')
		outfile.write('          multiNicVMotion: '+("true" if (variablesHypervisorAll["multi_nic_vmotion"]=="Enabled") else "false")+'\n')
		outfile.write('          virtualSwitchType: "'+variablesHypervisorAll["vswitch_type"]+'"\n')
		outfile.write('      status_code: 202\n')
		outfile.write('    register: var_return\n')
		outfile.write('\n')
		outfile.write('  - debug:\n')
		outfile.write('      var: var_return\n')
		outfile.write('\n')
		outfile.write('  - name: Taskinfo\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: no\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: 1000\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: \'{{ var_return["location"] }}\'\n')
		outfile.write('      method: GET\n')
		outfile.write('      status_code: 200\n')
		outfile.write('    register: var_taskinfo\n')
		outfile.write('\n')
		outfile.write('  - debug:\n')
		outfile.write('      var: var_taskinfo\n')
		outfile.write('\n')
		#END
		outfile.close()
		

def writeRenameEnclosures(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)

		#BEGIN
		outfile.write('    - name: Gather facts about all Enclosures\n')
		outfile.write('      oneview_enclosure_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: enc_m1="{{ item }}"\n')
		outfile.write('      loop: "{{ enclosures }}"\n')
		outfile.write('      when: item.applianceBays.0.model is match "Synergy Composer" and item.applianceBays.1.model is none\n')
		outfile.write('\n')
		outfile.write('    - set_fact: enc_m2="{{ item }}"\n')
		outfile.write('      loop: "{{ enclosures }}"\n')
		outfile.write('      when: item.applianceBays.0.model is match "Synergy Composer" and item.applianceBays.1.model is match "Synergy Image Streamer"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: enc_sl="{{ item }}"\n')
		outfile.write('      loop: "{{ enclosures }}"\n')
		outfile.write('      when: item.applianceBays.0.model is none and item.applianceBays.1.model is match "Synergy Image Streamer"\n')
		outfile.write('\n')
		outfile.write('    - name: Rename Enclosure Master-1\n')
		outfile.write('      oneview_enclosure:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        validate_etag: False\n')
		outfile.write('        data:\n')
		outfile.write('          name: "{{ enc_m1.name }}"\n')
		outfile.write('          newName: "'+frame["letter"]+'-Master1"\n')
		outfile.write('\n')
		outfile.write('    - name: Rename Enclosure Master-2\n')
		outfile.write('      oneview_enclosure:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        validate_etag: False\n')
		outfile.write('        data:\n')
		outfile.write('          name: "{{ enc_m2.name }}"\n')
		outfile.write('          newName: "'+frame["letter"]+'-Master2"\n')
		outfile.write('\n')
		outfile.write('    - name: Rename Enclosure Slave\n')
		outfile.write('      oneview_enclosure:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        validate_etag: False\n')
		outfile.write('        data:\n')
		outfile.write('          name: "{{ enc_sl.name }}"\n')
		outfile.write('          newName: "'+frame["letter"]+'-Slave"\n')
		outfile.write('\n')
		#END
		outfile.close()
		
		
		
		
def writeRenameServerHardwareTypes(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)

		#BEGIN
		outfile.write('    - name: Gather facts about all Server Hardware Types\n')
		outfile.write('      oneview_server_hardware_type_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('\n')
		outfile.write('    - set_fact: var_one="{{ item }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{server_hardware_types}}"\n')
		outfile.write('      when: item["adapters"]|length==1\n')
		outfile.write('\n')
		outfile.write('    - set_fact: var_two="{{ item }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{server_hardware_types}}"\n')
		outfile.write('      when: item["adapters"]|length==2\n')
		outfile.write('\n')
		outfile.write('    - debug: msg="{{ var_one[\'name\'] }}"\n')
		outfile.write('    - debug: msg="{{ var_two[\'name\'] }}"\n')
		outfile.write('\n')
		outfile.write('    - name: Rename the Server Hardware Type\n')
		outfile.write('      oneview_server_hardware_type:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        data:\n')
		outfile.write('          name: "{{ var_one[\'name\'] }}"\n')
		outfile.write('          newName: "HypervisorNode"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('\n')
		outfile.write('    - name: Rename the Server Hardware Type\n')
		outfile.write('      oneview_server_hardware_type:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        data:\n')
		outfile.write('          name: "{{ var_two[\'name\'] }}"\n')
		outfile.write('          newName: "StorageNode"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('\n')
		outfile.write('    - name: Gather facts about all Server Hardware Types\n')
		outfile.write('      oneview_server_hardware_type_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('\n')
		outfile.write('    - set_fact: var_one="{{ item }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{server_hardware_types}}"\n')
		outfile.write('      when: item["adapters"]|length==1\n')
		outfile.write('\n')
		outfile.write('    - set_fact: var_two="{{ item }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{server_hardware_types}}"\n')
		outfile.write('      when: item["adapters"]|length==2\n')
		outfile.write('\n')
		outfile.write('    - debug: msg="{{ var_one[\'name\'] }}"\n')
		outfile.write('    - debug: msg="{{ var_two[\'name\'] }}"\n')
		outfile.write('\n')
		#END
		outfile.close()
		
		

def writeAddHypervisorClusterProfile(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		hostname = frame["variables"]["oneview_hostname"].lower()+'.'+frame["variables"]["domain_name"]
		writeFilepartRESTAPILogin(outfile,hostname,"Administrator",frame["variables"]["administrator_passwort"])
		
		
		
		#BEGIN get Hypervisor managers
		outfile.write('  - name: get Hypervisor managers\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: no\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: 1000\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: https://'+hostname+'/rest/hypervisor-managers\n')
		outfile.write('      method: GET\n')
		outfile.write('      body_format: json\n')
		outfile.write('      body:\n')
		outfile.write('      status_code: 200\n')
		outfile.write('    register: var_hypervisor_managers\n')
		outfile.write('  - set_fact: var_hypervisor_manager_uri="{{var_hypervisor_managers["json"]["members"][0]["uri"]}}"\n')
		outfile.write('\n')
		
		
		#BEGIN get Server Profile Templates
		outfile.write('  - name: get Server Profile Templates\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: no\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: 1000\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: https://'+hostname+'/rest/server-profile-templates\n')
		outfile.write('      method: GET\n')
		outfile.write('      body_format: json\n')
		outfile.write('      body:\n')
		outfile.write('      status_code: 200\n')
		outfile.write('    register: var_server_profile_templates\n')
		
		
		
		#outfile.write('  - set_fact: var_hypervisor_manager_uri="{{var_hypervisor_managers["json"]["members"][0]["uri"]}}"\n')
		outfile.write('\n')
		
		
		for cluster in varaiblesClustersAll:
			if(cluster[0]!=frame["letter"]):
				continue
				
			#BEGIN SET
			outfile.write('  - name: Initiate asynchronous registration of an Hypervisor-Cluster-Profile (Using AUTH-Token) (Statuscode should be 202)\n')
			outfile.write('    uri:\n')
			outfile.write('      validate_certs: no\n')
			outfile.write('      headers:\n')
			outfile.write('        Auth: "{{ var_token }}"\n')
			outfile.write('        X-Api-Version: 1000\n')
			outfile.write('        Content-Type: application/json\n')
			outfile.write('      url: https://'+hostname+'/rest/hypervisor-cluster-profiles\n')
			outfile.write('      method: POST\n')
			outfile.write('      body_format: json\n')
			outfile.write('      body:\n')
			
			#BEGIN SET BODY
			outfile.write('        type: HypervisorClusterProfileV3\n')
			outfile.write('        name: "'+cluster+'"\n')
			outfile.write('        description: ""\n')
			outfile.write('        hypervisorType: Vmware\n')
			outfile.write('        hypervisorManagerUri: "{{ var_hypervisor_manager_uri }}"\n')
			outfile.write('        path: "FFM-'+frame["letter"]+'"\n')
			outfile.write('        mgmtIpSettingsOverride:\n')
			outfile.write('          netmask: "{{ mgt_network_netmask }}"\n')
			outfile.write('          gateway: "{{ mgt_network_gateway }}"\n')
			outfile.write('          dnsDomain: "{{ mgt_network_domain }}"\n')
			outfile.write('          primaryDns: "{{ mgt_network_dns1 }}"\n')
			outfile.write('          secondaryDns: "{{ mgt_network_dns2 }}"\n')		
			outfile.write('        hypervisorClusterSettings:\n')
			outfile.write('          type: "Vmware"\n')
			outfile.write('          drsEnabled: '+("true" if (variablesHypervisorAll["distributed_resource_scheduler"]=="Enabled") else "false")+'\n')
			outfile.write('          haEnabled: '+("true" if (variablesHypervisorAll["high_availability"]=="Enabled") else "false")+'\n')
			outfile.write('          distributedSwitchVersion: "'+variablesHypervisorAll["distributed_vswitch_version"]+'"\n')
			outfile.write('          distributedSwitchUsage: "'+variablesHypervisorAll["use_distributed_vswitch_for"]+'"\n')
			outfile.write('          multiNicVMotion: '+("true" if (variablesHypervisorAll["multi_nic_vmotion"]=="Enabled") else "false")+'\n')
			outfile.write('          virtualSwitchType: "'+variablesHypervisorAll["vswitch_type"]+'"\n')
			outfile.write('        hypervisorHostProfileTemplate:\n')
			outfile.write('          serverProfileTemplateUri: "{{ spt_uri }}"\n') #CODE depends on step 17
			outfile.write('          deploymentPlan:\n')
			outfile.write('            serverPassword: "{{ serverPassword }}"\n')
			outfile.write('            deploymentCustomArgs: []\n')
			outfile.write('          hostprefix: "{{ hvcp_name }}"\n')
			outfile.write('          virtualSwitches:\n')
			outfile.write('\n')        #CODE Loop_start über alle Standard-Switches
			outfile.write('          - name: "{{ vswitch_name }}"\n')
			outfile.write('            virtualSwitchType: Standard\n')
			outfile.write('            version: \n')
			outfile.write('            virtualSwitchPortGroups:\n')
			outfile.write('            - name: "{{ portgroup_name }}"\n')
			outfile.write('              networkUris:\n')
			outfile.write('              - "{{ network_uri }}"\n')
			outfile.write('              vlan: "0"\n')
			outfile.write('              virtualSwitchPorts:\n')
			outfile.write('              - virtualPortPurpose:\n')
			outfile.write('                - {{ network_purpose }}\n')
			outfile.write('                ipAddress: \n')
			outfile.write('                subnetMask: \n')
			outfile.write('                dhcp: true\n')
			outfile.write('                action: NONE\n')
			outfile.write('              action: NONE\n')
			outfile.write('            virtualSwitchUplinks:\n')
			outfile.write('            - name: Mezz 3:1-d\n') #CODE aus Server Profile Template
			outfile.write('              active: false\n')
			outfile.write('              mac: \n')
			outfile.write('              vmnic: \n')
			outfile.write('              action: NONE\n')
			outfile.write('            - name: Mezz 3:2-d\n') #CODE aus Server Profile Template
			outfile.write('              active: false\n')
			outfile.write('              mac: \n')
			outfile.write('              vmnic: \n')
			outfile.write('              action: NONE\n')
			outfile.write('            action: NONE\n')
			outfile.write('            networkUris:\n')
			outfile.write('            - "{{ network_uri }}"\n')
			outfile.write('\n')          #CODE Loop_end      
			outfile.write('\n')        #CODE Loop_start über alle Distributed Switches
			outfile.write('          - name: "{{ vswitch_name }}"\n')
			outfile.write('            virtualSwitchType: Distributed\n')
			outfile.write('            version: 6.6.0\n')
			outfile.write('            virtualSwitchPortGroups:\n')
			outfile.write('\n')        	#CODE Loop_start über alle Netze im netSet
			outfile.write('            - name: "{{ network_name }}"\n')
			outfile.write('              networkUris:\n')
			outfile.write('              - "{{ network_uri }}\n')
			outfile.write('              vlan: "{{ network_vlan }}"\n')
			outfile.write('              virtualSwitchPorts: []\n')
			outfile.write('              action: NONE\n')
			outfile.write('\n')        	#CODE Loop_end
			outfile.write('            virtualSwitchUplinks:\n')
			outfile.write('            - name: Mezz 3:1-f\n') #CODE aus Server Profile Template
			outfile.write('              active: false\n')
			outfile.write('              mac: \n')
			outfile.write('              vmnic: \n')
			outfile.write('              action: NONE\n')
			outfile.write('            - name: Mezz 3:2-f\n') #CODE aus Server Profile Template
			outfile.write('              active: false\n')
			outfile.write('              mac: \n')
			outfile.write('              vmnic: \n')
			outfile.write('              action: NONE\n')
			outfile.write('            action: NONE\n')
			outfile.write('            networkUris:\n')
			outfile.write('            - "{{ networkset_uri }}"\n')
			outfile.write('\n')        #CODE Loop_end
			outfile.write('          hostConfigPolicy:\n')
			outfile.write('            leaveHostInMaintenance: false\n')
			outfile.write('            useHostnameToRegister: true\n')
			outfile.write('          virtualSwitchConfigPolicy:\n')
			outfile.write('            manageVirtualSwitches: true\n')
			outfile.write('            configurePortGroups: true\n')
			#END BODY
			
			outfile.write('      status_code: 202\n')
			outfile.write('    register: var_return\n')
			outfile.write('\n')
			outfile.write('  - debug:\n')
			outfile.write('      var: var_return\n')
			outfile.write('\n')
		#END
		outfile.close()

def writeCreateServerProfileTemplate(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		hostname = frame["variables"]["oneview_hostname"].lower()+'.'+frame["variables"]["domain_name"]


		#BEGIN
		outfile.write('    - name: Gather facts about all Os Deployment Plans\n')
		outfile.write('      oneview_os_deployment_plan_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('    - set_fact:         var_os_deployment_plans_0_name="{{os_deployment_plans[0]["name"]}}"\n')
		outfile.write('\n')
		outfile.write('    - name: Find Deployment Plan URI\n')
		outfile.write('      oneview_os_deployment_plan_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        name: "{{ var_os_deployment_plans_0_name }}"\n')
		outfile.write('    - set_fact: deployment_plan_uri="{{ os_deployment_plans[0].uri }}"\n')
		outfile.write('\n')
		outfile.write('    - name: Find Firmware Baseline URI\n')
		outfile.write('      oneview_firmware_driver_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('    - set_fact: firmware_baseline_uri="{{ firmware_drivers[0].uri }}"\n')
		outfile.write('\n')
		outfile.write('    - name: Find Network Set URI\n')
		outfile.write('      oneview_network_set_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: prod_netset_uri="{{ item.uri }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{ network_sets }}"\n')
		outfile.write('      when: item.name is match "set_Prod"\n')
		outfile.write('\n')
		outfile.write('    - name: Gather network URIs\n')
		outfile.write('      oneview_ethernet_network_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: deploy_network_uri="{{ item.uri }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{ ethernet_networks }}"\n')
		outfile.write('      when: item.name is match "iSCSI-Deployment"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: management_network_uri="{{ item.uri }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{ ethernet_networks }}"\n')
		outfile.write('      when: item.name is match "ib-mgmt"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: vmotion_network_uri="{{ item.uri }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{ ethernet_networks }}"\n')
		outfile.write('      when: item.name is match "vSphereVMotion"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: iscsi_a_network_uri="{{ item.uri }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{ ethernet_networks }}"\n')
		outfile.write('      when: item.name is match "iSCSI-A"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: iscsi_b_network_uri="{{ item.uri }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{ ethernet_networks }}"\n')
		outfile.write('      when: item.name is match "iSCSI-B"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: ft_network_uri="{{ item.uri }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{ ethernet_networks }}"\n')
		outfile.write('      when: item.name is match "vSphereFT"\n')
		outfile.write('\n')
		outfile.write('    - name: Create Server Profile Template\n')
		outfile.write('      oneview_server_profile_template:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        data:\n')
		outfile.write('          type: ServerProfileTemplateV6\n')
		outfile.write('          name: "Nublar_ESXi"\n') #CODE
		outfile.write('          description: "ESXi 6.7 Update 2 Build 13981272 mit NCM 6.1 und iSUT 2.4"\n') #CODE
		outfile.write('          serverProfileDescription: ""\n')
		outfile.write('          serverHardwareTypeName: "HypervisorNode"\n')
		outfile.write('          enclosureGroupName: "Nublar_EG_3e"\n')
		outfile.write('          affinity: Bay\n')
		outfile.write('          hideUnusedFlexNics: true\n')
		outfile.write('          macType: Virtual\n')
		outfile.write('          wwnType: Virtual\n')
		outfile.write('          serialNumberType: Virtual\n')
		outfile.write('          iscsiInitiatorNameType: AutoGenerated\n')
		outfile.write('          osDeploymentSettings:\n')
		outfile.write('            osDeploymentPlanUri: "{{ deployment_plan_uri }}"\n')
		outfile.write('            osCustomAttributes:\n')
		outfile.write('            - name: DomainName\n')
		outfile.write('              value: ad.nublar.de\n')
		outfile.write('              constraints: \'{"helpText":""}\'\n')
		outfile.write('              type: fqdn\n')
		outfile.write('            - name: Hostname\n')
		outfile.write('              value: ""\n')
		outfile.write('              constraints: \'{"helpText":""}\'\n')
		outfile.write('              type: hostname\n')
		outfile.write('            - name: ManagementNIC.connectionid\n')
		outfile.write('              value: "3"\n')
		outfile.write('            - name: ManagementNIC.dns1\n')
		outfile.write('              value: 10.40.72.10\n')
		outfile.write('            - name: ManagementNIC.dns2\n')
		outfile.write('              value: 10.40.72.11\n')
		outfile.write('            - name: ManagementNIC.gateway\n')
		outfile.write('              value: 10.40.195.254\n')
		outfile.write('            - name: ManagementNIC.ipaddress\n')
		outfile.write('              value: ""\n')
		outfile.write('            - name: ManagementNIC.netmask\n')
		outfile.write('              value: 255.255.254.0\n')
		outfile.write('            - name: ManagementNIC.networkuri\n')
		outfile.write('              value: "{{ management_network_uri }}"\n')
		outfile.write('            - name: ManagementNIC.constraint\n')
		outfile.write('              value: userspecified\n')
		outfile.write('            - name: ManagementNIC.vlanid\n')
		outfile.write('              value: "0"\n')
		outfile.write('            - name: ManagementNIC2.connectionid\n')
		outfile.write('              value: "4"\n')
		outfile.write('            - name: ManagementNIC2.networkuri\n')
		outfile.write('              value: "{{ management_network_uri }}"\n')
		outfile.write('            - name: ManagementNIC2.constraint\n')
		outfile.write('              value: userspecified\n')
		outfile.write('            - name: ManagementNIC2.vlanid\n')
		outfile.write('              value: "0"\n')
		outfile.write('            - name: Password\n')
		outfile.write('              value: ""\n')
		outfile.write('            - name: SSH\n')
		outfile.write('              value: enabled\n')
		outfile.write('              constraints: \'{"options":["enabled","disabled"]}\'\n')
		outfile.write('              type: option\n')
		outfile.write('            complianceControl: Checked\n')
		outfile.write('          firmware:\n')
		outfile.write('            manageFirmware: true\n')
		outfile.write('            firmwareBaselineUri: "{{ firmware_baseline_uri }}"\n')
		outfile.write('            forceInstallFirmware: false\n')
		outfile.write('            firmwareInstallType: FirmwareOnlyOfflineMode\n')
		outfile.write('            firmwareActivationType: Immediate\n')
		outfile.write('            complianceControl: Checked\n')
		outfile.write('          connectionSettings:\n')
		outfile.write('            connections:\n')
		outfile.write('            - id: 1\n')
		outfile.write('              name: Deployment Network A\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Mezz 3:1-a\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ deploy_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: Auto\n')
		outfile.write('              ipv4:\n')
		outfile.write('                ipAddressSource: SubnetPool\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: Primary\n')
		outfile.write('                bootVlanId: \n')
		outfile.write('                ethernetBootType: iSCSI\n')
		outfile.write('                bootVolumeSource: UserDefined\n')
		outfile.write('                iscsi:\n')
		outfile.write('                  initiatorNameSource: ProfileInitiatorName\n')
		outfile.write('                  secondBootTargetIp: ""\n')
		outfile.write('                  chapLevel: None\n')
		outfile.write('            - id: 2\n')
		outfile.write('              name: Deployment Network B\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Mezz 3:2-a\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ deploy_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: Auto\n')
		outfile.write('              ipv4:\n')
		outfile.write('                ipAddressSource: SubnetPool\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: Secondary\n')
		outfile.write('                bootVlanId: \n')
		outfile.write('                ethernetBootType: iSCSI\n')
		outfile.write('                bootVolumeSource: UserDefined\n')
		outfile.write('                iscsi:\n')
		outfile.write('                  initiatorNameSource: ProfileInitiatorName\n')
		outfile.write('                  secondBootTargetIp: ""\n')
		outfile.write('                  chapLevel: None\n')
		outfile.write('            - id: 3\n')
		outfile.write('              name: mgmt-1\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Mezz 3:1-d\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ management_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 4\n')
		outfile.write('              name: mgmt-2\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Mezz 3:2-d\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ management_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 5\n')
		outfile.write('              name: vmotion-1\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ vmotion_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 6\n')
		outfile.write('              name: vmotion-2\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ vmotion_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 7\n')
		outfile.write('              name: prod-1\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ prod_netset_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 8\n')
		outfile.write('              name: prod-2\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ prod_netset_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 9\n')
		outfile.write('              name: iSCSI-A\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ iscsi_a_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 10\n')
		outfile.write('              name: iSCSI-B\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ iscsi_b_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 11\n')
		outfile.write('              name: ft-1\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ ft_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 12\n')
		outfile.write('              name: ft-2\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ ft_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            manageConnections: true\n')
		outfile.write('            complianceControl: Checked\n')
		outfile.write('          bootMode:\n')
		outfile.write('            manageMode: true\n')
		outfile.write('            mode: UEFIOptimized\n')
		outfile.write('            secureBoot: Unmanaged\n')
		outfile.write('            pxeBootPolicy: Auto\n')
		outfile.write('            complianceControl: Checked\n')
		outfile.write('          boot:\n')
		outfile.write('            manageBoot: true\n')
		outfile.write('            order:\n')
		outfile.write('            - HardDisk\n')
		outfile.write('            complianceControl: Checked\n')
		outfile.write('          bios:\n')
		outfile.write('            manageBios: true\n')
		outfile.write('            overriddenSettings:\n')
		outfile.write('            - id: IntelUpiPowerManagement\n')
		outfile.write('              value: Disabled\n')
		outfile.write('            - id: UncoreFreqScaling\n')
		outfile.write('              value: Maximum\n')
		outfile.write('            - id: EnergyEfficientTurbo\n')
		outfile.write('              value: Disabled\n')
		outfile.write('            - id: MinProcIdlePkgState\n')
		outfile.write('              value: NoState\n')
		outfile.write('            - id: PowerRegulator\n')
		outfile.write('              value: StaticHighPerf\n')
		outfile.write('            - id: MinProcIdlePower\n')
		outfile.write('              value: NoCStates\n')
		outfile.write('            - id: SubNumaClustering\n')
		outfile.write('              value: Enabled\n')
		outfile.write('            - id: EnergyPerfBias\n')
		outfile.write('              value: MaxPerf\n')
		outfile.write('            - id: CollabPowerControl\n')
		outfile.write('              value: Disabled\n')
		outfile.write('            - id: WorkloadProfile\n')
		outfile.write('              value: Virtualization-MaxPerformance\n')
		outfile.write('            - id: NumaGroupSizeOpt\n')
		outfile.write('              value: Clustered\n')
		outfile.write('            complianceControl: Checked\n')
		outfile.write('          managementProcessor:\n')
		outfile.write('            manageMp: false\n')
		outfile.write('            mpSettings: []\n')
		outfile.write('            complianceControl: Unchecked\n')
		outfile.write('          localStorage:\n')
		outfile.write('            sasLogicalJBODs: []\n')
		outfile.write('            controllers:\n')
		outfile.write('            - logicalDrives:\n')
		outfile.write('              - name: local-raid1\n')
		outfile.write('                raidLevel: RAID1\n')
		outfile.write('                bootable: false\n')
		outfile.write('                numPhysicalDrives: 2\n')
		outfile.write('                driveTechnology: \n')
		outfile.write('                sasLogicalJBODId: \n')
		outfile.write('                accelerator: Unmanaged\n')
		outfile.write('              deviceSlot: Embedded\n')
		outfile.write('              mode: Mixed\n')
		outfile.write('              initialize: false\n')
		outfile.write('              driveWriteCache: Unmanaged\n')
		outfile.write('            complianceControl: Unchecked\n')
		outfile.write('          sanStorage:\n')
		outfile.write('            manageSanStorage: true\n')
		outfile.write('            hostOSType: VMware (ESXi)\n')
		outfile.write('            volumeAttachments: []\n')
		outfile.write('            sanSystemCredentials: []\n')
		outfile.write('            complianceControl: CheckedMinimum\n')
		outfile.write('\n')
		outfile.write('    - debug: var=server_profile_template\n')
		outfile.write('\n')
		#END
		
def main():
	findFrames()	
	findNimbles()	
	findHypervisor()	
	writeConfigs()
	writeTimelocale("01","ntp") #todo: test
	writeAddresspoolsubnet("02","subnetrange")
	writeAddHypervisorManager("03","addhypervisormanager") #todo: test
	writeCreatenetwork("04","ethernetnetworkwithassociatedsubnet")
	writeOSdeploymentServer("05","osds")
	writeNetworkset("06","networkset")
	writeLogicalInterconnectGroup("07","logicalinterconnectgroup") #https://github.com/HewlettPackard/oneview-ansible/blob/master/examples/synergy_environment_setup.yml
	writeEnclosureGroup("08","enclosuregroup")
	writeLogicalEnclosure("09","logicalenclosure")
	writeStoragesystem("10","storagesystem") #todo umsetzung via RESR-API
	writeAddFirmwareBundle("11","addfirmwarebundle")
	writeSetImagestreameripInConfig("12","setimagestreameripinconfig")
	writeUploadAndExtractIsArtifact("13","uploadAndExtractIsArtifact")
	writeUploadGI("14","uploadGI")
	writeCreatedeploymentplan("15","createdeploymentplan")
	writeRenameServerHardwareTypes("16","renameserverhardwaretypes") #todo: test
	writeCreateServerProfileTemplate("17","createserverprofiletemplate") #todo: implement
	writeAddHypervisorClusterProfile("18","addhypervisorclusterprofile") #todo umsetzung via RESR-API
	writeRenameEnclosures("19","renameenclosures") #todo: test
	#20 Create Volume Template
	#21 Create Volumes

	
#start
main()



