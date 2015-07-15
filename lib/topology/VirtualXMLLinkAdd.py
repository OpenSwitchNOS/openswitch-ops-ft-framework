###PROC+#####################################################################
# Name:        topology.VirtualXMLLinkAdd
#
# Namespace:   topology
#
# Author:      Vince Mendoza
#
# Purpose:     Adds a link to the topologyt 
#              
#
# Params:      device - device name
#
# Returns:     JSON structure
#                returnCode - status of command
#                data - None
#
##PROC-#####################################################################
import headers
import common
import xml.etree.ElementTree as ET

def VirtualXMLLinkAdd(**kwargs):
   device1 = kwargs.get("device1")
   device2 = kwargs.get("device2")
   link = kwargs.get("link")
   device1Port = kwargs.get("device1Port")
   device2Port = kwargs.get("device2Port")
   
   # Search for device1 to create interface block and link block
   xpath = ".//device[name='" + device1 + "']"
   device1Element = common.XmlGetElementsByTag(headers.TOPOLOGY, ".//device[name='" + device1 + "']")
   
   # create device 1 interface block
   dev1InterfaceTag = ET.SubElement(device1Element, "interface")
   interfaceName = ET.SubElement(dev1InterfaceTag, "name").text = str(device1Port)
   staticName = ET.SubElement(dev1InterfaceTag, "staticName").text = str(device1Port)
   
   # Dummied up values for now
   intId = ET.SubElement(dev1InterfaceTag, "id")
   rate = ET.SubElement(dev1InterfaceTag, "rate").text = "Ethernet-Auto-Negotiate"
   rate = ET.SubElement(dev1InterfaceTag, "rate").text = "Ethernet-10Mb"
   rate = ET.SubElement(dev1InterfaceTag, "rate").text = "Ethernet-100Mb"
   rate = ET.SubElement(dev1InterfaceTag, "rate").text = "Ethernet-1Gb"
   chassis = ET.SubElement(dev1InterfaceTag, "chassis")
   chassisPort = ET.SubElement(dev1InterfaceTag, "chassisPort")
   type = ET.SubElement(dev1InterfaceTag, "type").text = "auto"
   mode = ET.SubElement(dev1InterfaceTag, "mode").text = "100/1000T"
   module = ET.SubElement(dev1InterfaceTag, "module")
   poe = ET.SubElement(dev1InterfaceTag, "poe")
   slot = ET.SubElement(dev1InterfaceTag, "slot")
   systemPod = ET.SubElement(dev1InterfaceTag, "system-pod").text = "virtual"
    
   # create device 1 link block
   dev1LinkTag = ET.SubElement(device1Element, "link")
   linkName = ET.SubElement(dev1LinkTag, "name").text = link
   id = ET.SubElement(dev1LinkTag, "id")
   rate = ET.SubElement(dev1LinkTag, "rate").text = "Ethernet-1Gb"
   remoteDev1 = ET.SubElement(dev1LinkTag, "remoteDevice").text = device2
   remoteInterface1 = ET.SubElement(dev1LinkTag, "remoteInterface").text = str(device2Port)
   localInteface1 = ET.SubElement(dev1LinkTag, "localInterface").text = str(device1Port)
   type = ET.SubElement(dev1LinkTag, "type").text = "auto"
   asicVersion = ET.SubElement(dev1LinkTag, "asicVersion")
    
   # Search for device1 to create interface block and link block
   xpath = ".//device[name='" + device2 + "']"
   device2Element = common.XmlGetElementsByTag(headers.TOPOLOGY, xpath)
    
   # create device 1 interface block
   dev2InterfaceTag = ET.SubElement(device2Element, "interface")
   interfaceName = ET.SubElement(dev2InterfaceTag, "name").text = str(device2Port)
   staticName = ET.SubElement(dev2InterfaceTag, "staticName").text = str(device2Port)
    
   # Dummied up values for now
   intId = ET.SubElement(dev2InterfaceTag, "id")
   rate = ET.SubElement(dev2InterfaceTag, "rate").text = "Ethernet-Auto-Negotiate"
   rate = ET.SubElement(dev2InterfaceTag, "rate").text = "Ethernet-10Mb"
   rate = ET.SubElement(dev2InterfaceTag, "rate").text = "Ethernet-100Mb"
   rate = ET.SubElement(dev2InterfaceTag, "rate").text = "Ethernet-1Gb"
   chassis = ET.SubElement(dev2InterfaceTag, "chassis")
   chassisPort = ET.SubElement(dev2InterfaceTag, "chassisPort")
   type = ET.SubElement(dev2InterfaceTag, "type").text = "auto"
   mode = ET.SubElement(dev2InterfaceTag, "mode").text = "100/1000T"
   module = ET.SubElement(dev2InterfaceTag, "module")
   poe = ET.SubElement(dev2InterfaceTag, "poe")
   slot = ET.SubElement(dev2InterfaceTag, "slot")
   systemPod = ET.SubElement(dev2InterfaceTag, "system-pod").text = "virtual"
    
   # create device 1 link block
   dev2LinkTag = ET.SubElement(device2Element, "link")
   linkName = ET.SubElement(dev2LinkTag, "name").text = link
   id = ET.SubElement(dev2LinkTag, "id")
   rate = ET.SubElement(dev2LinkTag, "rate").text = "Ethernet-1Gb"
   remoteDev2 = ET.SubElement(dev2LinkTag, "remoteDevice").text = device1
   remoteInterface2 = ET.SubElement(dev2LinkTag, "remoteInterface").text = str(device1Port)
   localInteface2 = ET.SubElement(dev2LinkTag, "localInterface").text = str(device2Port)
   type = ET.SubElement(dev2LinkTag, "type").text = "auto"
   asicVersion = ET.SubElement(dev2LinkTag, "asicVersion")
   
   retStruct = common.ReturnJSONCreate(returnCode=0)
   return(retStruct)
   