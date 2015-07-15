###PROC+#####################################################################
# Name:        topology.VirtualXMLCreate
#
# Namespace:   topology
#
# Author:      Vince Mendoza
#
# Purpose:     Creates a Virtual XML Document 
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

def VirtualXMLCreate():
   # Create Logical Topology based on dictionary - Low PRiority
   
   # Create a Phytsical Topology - High Priority
   # Need concept of logical topology definition to create base TOPO
   
   # Create XML Document
   #  Set up comment
   #  Here create reservation header w/ id = virtual
   #  Create out devices in the files
   # Base Topology Tag
   headers.TOPOLOGY = ET.Element("topology", attrib={'version': "1.0"})
   
   # Reservation Tag
   reservationTag = ET.SubElement(headers.TOPOLOGY, 'reservation')
   reservationIdTag = ET.SubElement(reservationTag, 'id').text = "virtual"
   reservationIdTag = ET.SubElement(reservationTag, 'user')
   reservationIdTag = ET.SubElement(reservationTag, 'server')
   