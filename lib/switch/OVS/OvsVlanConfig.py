###PROC+#####################################################################
# Name:        switch.OVS.OvsVlan
#
# Namespace:   switch.OVS
#
# Author:      Vince Mendoza
#
# Purpose:     Create a vlan via ovs-vsctl
#
# Params:      connection - device connection
#              action - config / unconfig
#              bridge - bridge to add the vlan too
#              vlans - list of Vlans to add to the bridge
#
# Returns:     JSON structure
#              returnCode - status of command
#
##PROC-#####################################################################

from lib import *
import switch
import re

def OvsVlanConfig(**kwargs):
    connection = kwargs.get('connection')
    action = kwargs.get('action', 'config')
    bridge = kwargs.get('bridge', 'br0')
    vlans = kwargs.get('vlans')

    if connection is None:
       return False

    if action == 'config':
       #   command = "ovs-vsctl add-vlan " + bridge + " " +
       LogOutput("info","Configuring Vlan over OVS bridge")
       for curVlan in vlans:
          command = "ovs-vsctl add-vlan " + bridge + " " + str(curVlan) + " admin=up"
          # Send command to the switch
          devIntRetStruct = switch.DeviceInteract(connection=connection, command=command)
          retCode = devIntRetStruct.get('returnCode')
          if retCode != 0:
             LogOutput('error', "Failed to create vlan " + str(curVlan) + " over bridge " + bridge)
             retString = returnStruct(returnCode=1)
             return retString

             buffer = devIntRetStruct.get('buffer')
    else:
       # We are in unconfig
       for curVlan in vlans:
          LogOutput("info","Unconfiguring Vlan over OVS bridge")
          command = "ovs-vsctl del-vlan " + bridge + " " + str(curVlan)
          # Send command to the switch
          devIntRetStruct = switch.DeviceInteract(connection=connection, command=command)
          retCode = devIntRetStruct.get('returnCode')
          if retCode != 0:
             LogOutput('error', "Failed to delete vlan " + str(curVlan) + " over bridge " + bridge)
             retString = returnStruct(returnCode=1)
             return retString

             buffer = devIntRetStruct.get('buffer')

    retString = returnStruct(returnCode=0)
    return retString
