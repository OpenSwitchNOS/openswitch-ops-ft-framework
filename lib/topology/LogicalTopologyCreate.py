###PROC+#####################################################################
# Name:        topology.LogicalTopologyCreate
#
# Namespace:   topology
#
# Author:      Vince Mendoza
#
# Purpose:     Creates a logical document and write the file out.
#              
#
# Params:      device - device name
#
# Returns:     
#
##PROC-#####################################################################
import headers
import common
import xml.etree.ElementTree as ET
import xml.dom.minidom

def LogicalTopologyCreate(**kwargs):
    topoDict = kwargs.get('topoDict')
    
    headers.LOGICAL_TOPOLOGY = ET.Element("topology", attrib={'version': "3"})
    
    # Get target if there
    targets = str(topoDict.get('topoTarget', None))
    
    # create the links
    if "topoLinks" in  topoDict :
     topoLinks = str(topoDict['topoLinks'])
     for curLink in str.split(topoLinks,','):
       (link, dev1, dev2) = str.split(curLink, ':')
       linkTag = ET.SubElement(headers.LOGICAL_TOPOLOGY, 'link', attrib={'name': link, 'device1': dev1, 'device2': dev2, 'rate': "any"})
    
    topoDevices = str(topoDict['topoDevices'])
    for curDev in str.split(topoDevices):
        # Search for device in target
        curDevTarget = "false"
        for curTarget in str.split(targets):
           if curTarget == curDev:
              curDevTarget = "true"
              break
        
        deviceTag = ET.SubElement(headers.LOGICAL_TOPOLOGY, 'device', attrib={'name': curDev, 'target': curDevTarget, 'group': "NULL"})
    
    topoFilters = str(topoDict['topoFilters'])
    for curFilter in str.split(topoFilters, ','):
        (cDev, cAttr, cVal) = str.split(curFilter, ':')
        # Search for the tag in logical topology
        xpath = "./device[@name='"+cDev+"']"
        deviceTag = common.XmlGetElementsByTag(headers.LOGICAL_TOPOLOGY, xpath)
        if deviceTag != None:
           attributeTag = ET.SubElement(deviceTag, 'attribute', attrib={'name': cAttr, 'value': cVal})
        
    
    dumpString = ET.tostring(headers.LOGICAL_TOPOLOGY)
    
    # Write the topology out
    myxml = xml.dom.minidom.parseString(dumpString)
    pretty_xml_as_string = myxml.toprettyxml()
    topoFileName = headers.ResultsDirectory['resultsDir'] + "/logicalTopology.xml"
    topologyXMLFile = open(topoFileName, 'w+')
    topologyXMLFile.write(pretty_xml_as_string)
    topologyXMLFile.close()
