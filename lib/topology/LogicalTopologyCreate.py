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

    # Create TopoDevices
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
        #print curFilter
        (cDev, cAttr, cVal) = str.split(curFilter, ':')
        # Search for the tag in logical topology
        xpath = ".//device[@name='"+cDev+"']"
        deviceTag = common.XmlGetElementsByTag(headers.LOGICAL_TOPOLOGY, xpath)
        if deviceTag != None:
            attributeTag = ET.SubElement(deviceTag, 'attribute', attrib={'name': cAttr, 'value': cVal})

    # Need to inspect ETREE to see if profile is specific.  If not, lets assume auto-ubuntu-12-04 for workstations
    xpath = ".//device/attribute[@value='workstation']/.."
    wrkstonDevsTag = common.XmlGetElementsByTag(headers.LOGICAL_TOPOLOGY, xpath, allElements=True)
    for curTag in wrkstonDevsTag:
        #print curTag
        attribute_list = curTag.iter('attribute')
        #print "attrList "
        #print attribute_list
        found_profile = 0
        for curAttr in attribute_list:
            #print "curAttr"
            attrName = curAttr.get('name')
            #print attrName
            if attrName == "system-profile":
                found_profile = 1
                common.LogOutput('debug', "Found system-profile attribute stated for device - not assuming auto-ubuntu-12-04")
        if found_profile == 0:
            # Need to add subelements
            common.LogOutput('debug', "No system-profile attribute found, defaulting to auto-ubuntu-12-04")
            deviceTag = ET.SubElement(curTag, 'attribute', attrib={'name': "system-profile", 'value': "auto-ubuntu-12-04"})



    dumpString = ET.tostring(headers.LOGICAL_TOPOLOGY)

    # Write the topology out
    myxml = xml.dom.minidom.parseString(dumpString)
    pretty_xml_as_string = myxml.toprettyxml()
    topoFileName = headers.ResultsDirectory['resultsDir'] + "/logicalTopology.xml"
    topologyXMLFile = open(topoFileName, 'w+')
    topologyXMLFile.write(pretty_xml_as_string)
    topologyXMLFile.close()
