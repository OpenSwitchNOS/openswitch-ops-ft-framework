##########################################################################################
# Name:        switch.CLI.ShowLldpNeighborInfo
#
# Namespace:   switch.CLI
#
# Author:      Payal Upadhyaya 
#
# Purpose:     Run the show lldp commands in vtysh shell
#
# Params:      connection - device connection
#              port  - Ethernet port
#
# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data: (LLDP statistics): 
#                      NeighBour_chasisID:
#                      NeighbourEntries
#                      Neighbor_Info
#                      lldpNeighborBuffer(Device buffer)
#
##PROC-###################################################################################
import common
import switch
import re
import time

def ShowLldpNeighborInfo(**kwargs):
    connection = kwargs.get('connection')
    port = kwargs.get('port')
    if connection is None:
       return False

    returnDict = dict()
    #Enter the vtysh shell to access LLDP commands
    returnStructure = switch.CLI.VtyshShell(connection = connection)
    vtyshInfo = common.ReturnJSONGetData(json=returnStructure, dataElement='vtyshPrompt')
    common.LogOutput("debug","vtysh shell buffer: \n"+vtyshInfo)
    returnCode = common.ReturnJSONGetCode(json = returnStructure)
    if returnCode != 0:
       common.LogOutput('error', "Failed to get vtysh prompt")
       returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=returnStructure)
       return returnJson

    #Pass LLDP commands here 
    command = "show lldp neighbor-info %d"%(port)
    common.LogOutput("info","Show LLDP command ***"+command)
    devIntRetStruct = switch.DeviceInteract(connection=connection, command=command)
    returnCode = devIntRetStruct.get('returnCode')
    if returnCode != 0:
       common.LogOutput('error', "Failed to get show lldp neighbor-info command")
       returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=devIntRetStruct)
       return returnJson
    else :
       rawBuffer = devIntRetStruct.get('buffer')
       bufferSplit  = rawBuffer.split("\r\n")
       for line in bufferSplit:
         Neighbor_Info = re.match( r'.*neighbor-info\s+(\d+)',line)
         if Neighbor_Info :
           returnDict['Neighbor_Info'] = Neighbor_Info.group(1)
         NeighbourEntries = re.match(r'Neighbor entries :(\d+)',line)
         if NeighbourEntries :
           returnDict['NeighbourEntries'] = NeighbourEntries.group(1)
         NeighBour_chasisID = re.match(r'Neighbor Chassis-ID :()',line)
         if NeighBour_chasisID:
           returnDict['NeighBour_chasisID'] = NeighBour_chasisID.group(1)
       returnDict['lldpNeighborBuffer'] = rawBuffer

    #Exit the vtysh shell 
    returnStructure = switch.CLI.VtyshShell(connection = connection,configOption="unconfig")
    vtyshExitInfo = common.ReturnJSONGetData(json=returnStructure, dataElement='vtyshPrompt')
    common.LogOutput("debug","vtysh shell buffer: \n"+vtyshExitInfo) 
    returnCode = common.ReturnJSONGetCode(json = returnStructure)
    if returnCode != 0:
       common.LogOutput('error', "Failed to exit vtysh prompt")
       returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=returnStructure)
       return returnJson

    #Return results
    returnJson = common.ReturnJSONCreate(returnCode=0, data=returnDict)
    return returnJson
    
