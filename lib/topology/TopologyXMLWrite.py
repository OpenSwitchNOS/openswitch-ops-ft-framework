###PROC+#####################################################################
# Name:        topology.TopologyXMLWrite
#
# Namespace:   topology
#
# Author:      Vince Mendoza
#
# Purpose:     Writes out TOPOLOGY XML to file
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

def TopologyXMLWrite():
    dumpString = ET.tostring(headers.TOPOLOGY)
    #print "topologyDump" + str(dumpString)
    myxml = xml.dom.minidom.parseString(dumpString)
    pretty_xml_as_string = myxml.toprettyxml()
    topoFileName = headers.ResultsDirectory['resultsDir'] + "/physicalTopology.xml"
    topologyXMLFile = open(topoFileName, 'w+')

    topologyXMLFile.write(pretty_xml_as_string)
    topologyXMLFile.close()