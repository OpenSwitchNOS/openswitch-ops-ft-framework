###PROC+#####################################################################
# Name:        topology.LinkStatusConfig
#
# Namespace:   topology
#
# Author:      Vince Mendoza
#
# Purpose:     Routine to modify the status of a virtual / physical link
#

# Params:      links   - list of links
#              enable  = 0 default 1 to enable
#              disable = 0 default 1 to disable
#              allPhysical = 0 default 1 for all physical links
#              allLogical = 0 default 1 for all logical links
#
#
# Returns:     JSON with..
#                returnCode
#                data
#
##PROC-#####################################################################
import headers
import common
import topology
try:
    import RTL
except ImportError:
    common.LogOutput('debug', "RTL environment not available")
import xml.etree.ElementTree as ET
import xml.dom.minidom

def LinkStatusConfig(**kwargs):
    links = kwargs.get('links', None)
    enable = kwargs.get('enable', 0)
    disable = kwargs.get('disable', 0)
    allPhysical = kwargs.get('allPhysical', 0)
    allLogical = kwargs.get('allLogical', 0)

    if headers.topoType == "virtual":
       # Do code for virutally altering the link
       statusSet = "down"
       if enable == 1:
          statusSet = "up"
       elif disable == 1:
          statusSet = "down"

       for curLink in links:
          retStruct = headers.mininetGlobal.VirtualLinkModifyStatus(link=curLink,status=statusSet)
          returnCode = common.ReturnJSONGetCode(json=retStruct)
    else:
       # Do RTL based code to modify the link status
       # Just pass all the arguements into the RTL version of this call.
       retStruct = RTL.LinkModifyStatus(links=links, enable=enable, disable=disable, allPhysical=allPhysical, allLogical=allLogical)
       returnCode = common.ReturnJSONGetCode(json=retStruct)

    retString = common.ReturnJSONCreate(returnCode=returnCode)
    return(retString)