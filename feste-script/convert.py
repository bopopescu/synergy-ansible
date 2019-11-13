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
exceltabhypervisor = "Synergy Integrationen"
outputfolder = "output"

############################################################################
############## Only change Variables above this line #######################
############################################################################

variablesAll = []
variablesNimbleAll = {}
variablesHypervisorAll = {}

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
	global variablesHypervisorAll
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
		data = str(worksheet.cell_value(row,1))
		if(data=="" or data=="#TODO" or data=="n/a" or data.startswith("#TODO")):
			continue
		
		if(data.find("#TODO") != -1):
			pos = data.find("#TODO")
			data = data[:pos-1]
		
		name = convertToAnsibleVariableName(name)			
		variablesHypervisorAll[name] = data

	print(variablesHypervisorAll)

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
		outfile.write('             credentials:'+"\n")
		outfile.write('                 ip_hostname:               "'+variablesNimbleAll[frame["letter"]]["name"].lower()+'.'+variablesNimbleAll[frame["letter"]]["variables"]["domain_name"]+'"'+"\n")
		outfile.write('                 username:                  "oneview"'+"\n")
		outfile.write('                 password:                  "'+frame["variables"]["administrator_passwort"]+'"'+"\n")
		outfile.write('             managedPools:                  ""'+"\n")
		outfile.write('                   domain:                  "default"'+"\n")
		outfile.write('                   name:                    ""'+"\n")
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
		outfile.write('          description: "Test"\n')
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





def writeAddHypervisorManager(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)

		#BEGIN
		outfile.write('  - name: Login to API and retrieve AUTH-Token\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: no\n')
		outfile.write('      headers:\n')
		outfile.write('        X-Api-Version: 1000\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: https://'+frame["variables"]["oneview_hostname"].lower()+'.'+frame["variables"]["domain_name"]+'/rest/login-sessions\n')
		outfile.write('      method: POST\n')
		outfile.write('      body_format: json\n')
		outfile.write('      body:\n')
		outfile.write('        authLoginDomain: "LOCAL"\n')
		outfile.write('        password: "'+frame["variables"]["administrator_passwort"]+'"\n')
		outfile.write('        userName: "Administrator"\n')
		outfile.write('        loginMsgAck: "true"\n')
		outfile.write('    register: var_this\n')
		outfile.write('\n')
		outfile.write('  - set_fact: var_token=\'{{ var_this["json"]["sessionID"] }}\'\n')
		outfile.write('\n')
		outfile.write('  - debug:\n')
		outfile.write('      var: var_token\n')
		outfile.write('\n')
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


def main():
	findFrames()	
	findNimbles()	
	findHypervisor()	
	writeConfigs()
	writeTimelocale("01","ntp")
	writeAddresspoolsubnet("02","subnetrange")
	writeAddHypervisorManager("03","addhypervisormanager")
	writeCreatenetwork("04","ethernetnetworkwithassociatedsubnet")
	writeOSdeploymentServer("05","osds")
	writeNetworkset("06","networkset")
	writeLogicalInterconnectGroup("07","logicalinterconnectgroup") #https://github.com/HewlettPackard/oneview-ansible/blob/master/examples/synergy_environment_setup.yml
	writeEnclosureGroup("08","enclosuregroup")
	writeLogicalEnclosure("09","logicalenclosure")
	writeStoragesystem("10","storagesystem")
	writeAddFirmwareBundle("11","addfirmwarebundle")
	writeSetImagestreameripInConfig("12","setimagestreameripinconfig")
	writeUploadAndExtractIsArtifact("13","uploadAndExtractIsArtifact")
	writeUploadGI("14","uploadGI")
	writeCreatedeploymentplan("15","createdeploymentplan")
	

	
#start
main()



