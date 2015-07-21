###PROC+#####################################################################
# Name:        topology.InterfaceGetByDeviceLink
#
# Namespace:   topology
#
# Author:      Vince Mendoza
#
# Purpose:     Returns the interface associated with a link and device
#
#
# Params:      device - device name
#              link   - name of link
#
# Returns:     JSON with..
#                returnCode
#                data
#
##PROC-#####################################################################
import headers
import common
import xml.etree.ElementTree as ET
import xml.dom.minidom

def InterfaceGetByDeviceLink(**kwargs):
    device = kwargs.get('device', None)
    link = kwargs.get('link', None)

    xpath = ".//device[name='" + device + "']/link[name='" + link + "']/localInterface"

    retStruct = common.XmlGetElementsByTag(headers.TOPOLOGY, xpath)
    retString = common.ReturnJSONCreate(returnCode=0, data=retStruct.text)
    return(retString)