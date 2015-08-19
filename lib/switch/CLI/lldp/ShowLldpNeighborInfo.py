##########################################################################################
# Name:        switch.CLI.ShowLldpNeighborInfo
#
# Namespace:   switch.CLI
#
# Author:      Payal Upadhyaya
#
# Purpose:     Run the show lldp commands in vtysh shell
#
# Params:      deviceObj - device object
#              port  - Ethernet port (Optional)
#
# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data: 
#                   buffer: - string of buffer of command
#                   portStats:  - indexed by port (Neighbor_Entries_Deleted, Neighbor_Entries_Dropped,
#                                                  Neighbor_Entries, Neighbor_portID, TTL, 
#                                                  Neighbor_chassisID, Chassis_Capabilities_Enabled,
#                                                  Neighbor_chassisName, Chassis_Capabilities_Available,
#                                                  Neighbor_chassisDescription)
#                   globalStats:  - global statistics all ports
#                                    (Total_Neighbor_Entries, Total_Neighbor_Entries_Aged-out, 
#                                     Total_Neighbor_Entries_Deleted, Total_Neighbor_Entries_Dropped)
#
##PROC-###################################################################################
import common
import switch
import lib
import re
import time

def ShowLldpNeighborInfo(**kwargs):
    deviceObj = kwargs.get('deviceObj')
    port = kwargs.get('port', None)
    #if connection is None:
    #    return False

    returnDict = dict()
    #Enter the vtysh shell to access LLDP commands
    #returnStructure = switch.CLI.VtyshShell(connection = connection)
    #vtyshInfo = common.ReturnJSONGetData(json=returnStructure, dataElement='vtyshPrompt')
    #returnCode = common.ReturnJSONGetCode(json = returnStructure)
    
    returnStructure = deviceObj.VtyshShell()
    vtyshInfo = common.ReturnJSONGetData(json=returnStructure, dataElement='vtyshPrompt')
    returnCode = common.ReturnJSONGetCode(json = returnStructure)
    if returnCode != 0:
        common.LogOutput('error', "Failed to get vtysh prompt")
        returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=returnStructure)
        return returnJson
    else:
        common.LogOutput("debug","vtysh shell buffer: \n"+vtyshInfo)

    #Pass LLDP commands here
    command = "show lldp neighbor-info"
    if port != None:
        command += " " + str(port)
    
    common.LogOutput("info","Show LLDP command ***"+command)
    #devIntRetStruct = switch.DeviceInteract(connection=connection, command=command)
    devIntRetStruct = deviceObj.DeviceInteract(command=command)
    returnCode = devIntRetStruct.get('returnCode')
    if returnCode != 0:
        common.LogOutput('error', "Failed to get show lldp neighbor-info command")
        returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=devIntRetStruct)
        return returnJson
    else:
        rawBuffer = devIntRetStruct.get('buffer')
        bufferSplit  = rawBuffer.split("\r\n")
        globalStatsDict = dict()
        portDict = dict()
        if port != None:
            globalStatsDict['Total_Neighbor_Entries'] = ""
            globalStatsDict['Total_Neighbor_Entries_Deleted'] = ""
            globalStatsDict['Total_Neighbor_Entries_Dropped'] = ""
            globalStatsDict['Total_Neighbor_Entries_Aged-out'] = ""
            for line in bufferSplit:
                portLine = re.match("^Port\s+:\s*(\d+)\s*$", line)
                if portLine:
                    curPort = portLine.group(1)
                    portDict[curPort] = dict()
                    continue
                NeighborEntries = re.match("^Neighbor\s+entries\s+:\s*(\d+)\s*$",line)
                if NeighborEntries :
                    portDict[curPort]['Neighbor_Entries'] = NeighborEntries.group(1)
                    continue
                NeighborEntriesDeleted = re.match("^Neighbor\s+entries\s+deleted\s+:\s*(\d+)\s*$",line)
                if NeighborEntriesDeleted :
                    portDict[curPort]['Neighbor_Entries_Deleted'] = NeighborEntriesDeleted.group(1)
                    continue
                NeighborEntriesDropped = re.match("^Neighbor\s+entries\s+dropped\s+:\s*(\d+)\s*$",line)
                if NeighborEntriesDropped :
                    portDict[curPort]['Neighbor_Entries_Dropped'] = NeighborEntriesDropped.group(1)
                    continue
                NeighborEntriesAgedOut = re.match("^Neighbor\s+entries\s+aged-out\s+:\s*(\d+)\s*$",line)
                if NeighborEntriesAgedOut :
                    portDict[curPort]['Neighbor_Entries_Aged-out'] = NeighborEntriesAgedOut.group(1)
                    continue
                Neighbor_chasisName = re.match(r'Neighbor Chassis-Name\s+:\s*(\S+)\s*$',line)
                if Neighbor_chasisName:
                    portDict[curPort]['Neighbor_chassisName'] = Neighbor_chasisName.group(1)
                    continue
                Neighbor_chasisDescrip = re.match(r'Neighbor Chassis-Description\s+:\s*(.*)$',line)
                if Neighbor_chasisDescrip:
                    portDict[curPort]['Neighbor_chassisDescription'] = Neighbor_chasisDescrip.group(1)
                    continue
                Neighbor_chasisID = re.match(r'Neighbor Chassis-ID :([0-9a-f:]+|\s*)$',line)
                if Neighbor_chasisID:
                    portDict[curPort]['Neighbor_chasisID'] = Neighbor_chasisID.group(1)
                    continue
                Chassis_CapAvail = re.match(r'Chassis Capabilities Available\s*:\s*(.*)$',line)
                if Chassis_CapAvail:
                    portDict[curPort]['Chassis_Capabilities_Available'] = Chassis_CapAvail.group(1)
                    continue
                Chassis_CapEnabled = re.match(r'Chassis Capabilities Enabled\s*:\s*(.*)$',line)
                if Chassis_CapEnabled:
                    portDict[curPort]['Chassis_Capabilities_Enabled'] = Chassis_CapEnabled.group(1)
                    continue
                Neighbor_portID = re.match(r'Neighbor Port-ID\s*:\s*(.*)$',line)
                if Neighbor_portID:
                    portDict[curPort]['Neighbor_portID'] = Neighbor_portID.group(1)
                ttl = re.match(r'TTL :(\d+|\s*)$',line)
                if ttl:
                    portDict[curPort]['TTL'] = ttl.group(1)
            returnDict['globalStats'] = globalStatsDict
            returnDict['portStats'] = portDict
            returnDict['buffer'] = rawBuffer
            #returnDict['lldpNeighborBuffer'] = rawBuffer
        else:
            # This means we are parsing out output w/out ports
            for line in bufferSplit:
                # Pull out Totals
                totalNeighEntries = re.match("^Total\s+neighbor\s+entries\s+:\s+(\d+)\s*$", line)
                if totalNeighEntries:
                    globalStatsDict['Total_Neighbor_Entries'] = totalNeighEntries.group(1)
                    continue
                totalNeighEntriesDeleted = re.match("^Total\s+neighbor\s+entries\s+deleted\s+:\s+(\d+)\s*$", line)
                if totalNeighEntriesDeleted:
                    globalStatsDict['Total_Neighbor_Entries_Deleted'] = totalNeighEntriesDeleted.group(1)
                    continue
                totalNeighEntriesDropped = re.match("^Total\s+neighbor\s+entries\s+dropped\s+:\s+(\d+)\s*$", line)
                if totalNeighEntriesDropped:
                    globalStatsDict['Total_Neighbor_Entries_Dropped'] = totalNeighEntriesDropped.group(1)
                    continue
                totalNeighEntriesAgedOut = re.match("^Total\s+neighbor\s+entries\s+aged-out\s+:\s+(\d+)\s*$", line)
                if totalNeighEntriesAgedOut:
                    globalStatsDict['Total_Neighbor_Entries_Aged-out'] = totalNeighEntriesAgedOut.group(1)
                    continue
                
                # Now lets go through each line
                blankPortEntry = re.match("^([0-9-]+)\s*$", line)
                if blankPortEntry:
                    curPort = blankPortEntry.group(1)
                    portDict[curPort] = dict()
                    portDict[curPort]['Neighbor_Entries_Deleted'] = ""
                    portDict[curPort]['Neighbor_Entries_Dropped'] = ""
                    portDict[curPort]['Neighbor_Entries'] = ""
                    portDict[curPort]['Neighbor_Chassis-ID'] = ""
                    portDict[curPort]['Neighbor_chassisName'] = ""
                    portDict[curPort]['Neighbor_chassisDescription'] = ""
                    portDict[curPort]['Chassis_Capabilities_Available'] = ""
                    portDict[curPort]['Neighbor_Port-ID'] = ""
                    portDict[curPort]['Chassis_Capabilities_Enabled'] = ""
                    portDict[curPort]['TTL'] = ""
                    continue
                populatedPortEntry = re.match("^([0-9-]+)\s+([0-9a-f:]+)\s+(\S+)\s+(\d+)\s*$", line)
                if populatedPortEntry:
                    curPort = populatedPortEntry.group(1)
                    portDict[curPort] = dict()
                    portDict[curPort]['Neighbor_Entries_Deleted'] = ""
                    portDict[curPort]['Neighbor_Entries_Dropped'] = ""
                    portDict[curPort]['Neighbor_Entries'] = ""
                    portDict[curPort]['Neighbor_Chassis-ID'] = populatedPortEntry.group(2) 
                    portDict[curPort]['Neighbor_chassisName'] = ""
                    portDict[curPort]['Neighbor_chassisDescription'] = ""
                    portDict[curPort]['Chassis_Capabilities_Available'] = ""
                    portDict[curPort]['Chassis_Capabilities_Enabled'] = ""
                    portDict[curPort]['Neighbor_Port-ID'] = populatedPortEntry.group(3)
                    portDict[curPort]['TTL'] = populatedPortEntry.group(4)
            returnDict['globalStats'] = globalStatsDict
            returnDict['portStats'] = portDict
            returnDict['buffer'] = rawBuffer
            

    #Exit the vtysh shell
    #returnStructure = switch.CLI.VtyshShell(connection = connection,configOption="unconfig")
    returnStructure = deviceObj.VtyshShell(configOption="unconfig")
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

