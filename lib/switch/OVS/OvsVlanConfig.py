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
import common
import switch
import re

def OvsVlanConfig(**kwargs):
    connection = kwargs.get('connection')
    action = kwargs.get('action', 'config')
    bridge = kwargs.get('bridge', 'br0')
    vlans = kwargs.get('vlans')
    
    if connection is None:
       return False
    
    retStruct = dict()
    if action == 'config':
       #   command = "ovs-vsctl add-vlan " + bridge + " " +
       common.LogOutput("info","Configuring Vlan over OVS bridge")
       for curVlan in vlans:
          command = "ovs-vsctl add-vlan " + bridge + " " + str(curVlan) + " admin=up"
          # Send command to the switch 
          devIntRetStruct = switch.DeviceInteract(connection=connection, command=command)
          retCode = devIntRetStruct.get('returnCode')
          if retCode != 0:
             common.LogOutput('error', "Failed to create vlan " + str(curVlan) + " over bridge " + bridge)
             retString = common.ReturnJSONCreate(returnCode=1, data=retStruct)
             return retString

             buffer = devIntRetStruct.get('buffer')
    else:
       # We are in unconfig
       for curVlan in vlans:
          common.LogOutput("info","Unconfiguring Vlan over OVS bridge")
          command = "ovs-vsctl del-vlan " + bridge + " " + str(curVlan)
          # Send command to the switch 
          devIntRetStruct = switch.DeviceInteract(connection=connection, command=command)
          retCode = devIntRetStruct.get('returnCode')
          if retCode != 0:
             common.LogOutput('error', "Failed to delete vlan " + str(curVlan) + " over bridge " + bridge)
             retString = common.ReturnJSONCreate(returnCode=1, data=retStruct)
             return retString

             buffer = devIntRetStruct.get('buffer')

    retString = common.ReturnJSONCreate(returnCode=0, data=retStruct)
    return retString
