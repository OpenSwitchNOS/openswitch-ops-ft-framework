###PROC+#####################################################################
# Name:        topology.VirtualXMLDeviceAdd
#
# Namespace:   topology
#
# Author:      Vince Mendoza
#
# Purpose:     Adds a device to the topologyt
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

def VirtualXMLDeviceAdd(**kwargs):
   name = kwargs.get('name')
   vendor = kwargs.get('vendor', "hp")
   platform = kwargs.get('platform', None)
   category = kwargs.get('category', "switch")
   macAddress = kwargs.get('macAddress', None)
   os = kwargs.get('os', None)
   partNumber = kwargs.get('partNumber', None)
   serialNumber = kwargs.get('serialNumber', None)
   productCode = kwargs.get('productCode', None)
   status = kwargs.get('status', "ok")
   pod = kwargs.get('pod', "virtual")

   # device tag block
   deviceTag = ET.SubElement(headers.TOPOLOGY, 'device')
   if name is None:
      retStruct = common.ReturnJSONCreate(returnCode=1)
      return(retStruct)

   deviceNameTag = ET.SubElement(deviceTag, 'name').text = name

   # Create System area
   systemTag = ET.SubElement(deviceTag, 'system')

   # System Area
   # Name
   systemNameTag = ET.SubElement(systemTag, "name").text = name


   # Vendor
   systemVendorTag = ET.SubElement(systemTag, "vendor").text = vendor

   # Platform
   if platform is None:
      systemPlatformTag = ET.SubElement(systemTag, "platform")
   else:
      systemPlatformTag = ET.SubElement(systemTag, "platform").text = platform

   systemPlatformTag = ET.SubElement(systemTag, "category").text = category

   # macAddress
   if macAddress is None:
      systemPlatformTag = ET.SubElement(systemTag, "macAddress")
   else:
      systemPlatformTag = ET.SubElement(systemTag, "macAddress").text = macAddress

   # os
   if os is None:
      systemPlatformTag = ET.SubElement(systemTag, "os")
   else:
      systemPlatformTag = ET.SubElement(systemTag, "os").text = os

   # partNumber
   if partNumber is None:
      systemPlatformTag = ET.SubElement(systemTag, "partNumber")
   else:
      systemPlatformTag = ET.SubElement(systemTag, "partNumber").text = partNumber

   # serialNumber
   if serialNumber is None:
      systemPlatformTag = ET.SubElement(systemTag, "serialNumber")
   else:
      systemPlatformTag = ET.SubElement(systemTag, "serialNumber").text = serialNumber

   # productCode
   if serialNumber is None:
      systemPlatformTag = ET.SubElement(systemTag, "productCode")
   else:
      systemPlatformTag = ET.SubElement(systemTag, "productCode").text = productCode

   # status
   systemPlatformTag = ET.SubElement(systemTag, "status").text = status

   # pod
   systemPlatformTag = ET.SubElement(systemTag, "pod").text = pod
   #
   # Add connection Area
   connectionTag = ET.SubElement(deviceTag, 'connection')

   # name
   connectionNameTag = ET.SubElement(connectionTag, "name").text = name

   connectionConsoleTag = ET.SubElement(connectionTag, "category").text = "console"
   connectionManagementTag = ET.SubElement(connectionTag, "type").text = "management"
   connectionIPTag = ET.SubElement(connectionTag, "ipAddr")
   connectionPortTag = ET.SubElement(connectionTag, "port")
   connectionProtocolTag = ET.SubElement(connectionTag, "protocol").text = "docker"
   connectionPriorityTag = ET.SubElement(connectionTag, "priority").text = "0"

   retStruct = common.ReturnJSONCreate(returnCode=0)
   return(retStruct)


