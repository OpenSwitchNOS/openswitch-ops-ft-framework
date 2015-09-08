##########################################################################################
# Name:        switch.CLI.interface.ShowVlan.py
#
# Namespace:   switch.CLI.interface
#
# Author:      Diego Hurtado
#
# Purpose:     Library function to show the VLANs.
#
# Params:      deviceObj - device object.
#
# Returns:     returnStruct - return object with the following attributes:
#               returnCode - integer set to 0 if the function ended up succesfully
#                            or set to 1 if an error occurred.
#               data - list of dictionaries, each one with the following keys:
#                   Status - string set to "up" or "down"
#                   Reserved - string
#                   Name - string set to the name of the VLAN
#                   VLAN - string set to the id of the VLAN
#                   Reason - string
#                   Ports - list of strings
#               buffer - string with the output of the command execution
#
##PROC-###################################################################################

import lib
import re
import time

def ShowVlan(**kwargs):
    deviceObj = kwargs.get('deviceObj', None)
    
    overallBuffer = []
    # If Device object is not passed, we need to error out
    if deviceObj is None:
        lib.LogOutput('error', "Need to pass switch device object deviceObj to this routine")
        returnCls = lib.returnStruct(returnCode=1)
        return returnCls

    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        lib.LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

   
    command = "show vlan\n"

    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    temporaryBuffer = returnDevInt['buffer']
    if retCode != 0:
        lib.LogOutput('error', "Failed to create VLAN."+ command)
    else:
        lib.LogOutput('debug', "Created VLAN." + command)
    
   
    # Get out of vtyshell
    returnStructure = deviceObj.VtyshShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        lib.LogOutput('error', "Failed to exit vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    result = []
    keys = re.findall(r'\r\n(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\r\n', temporaryBuffer)

    if len(keys) == 1:
        keys = keys[0]
        vlans = re.findall(r'(\d+)\s+(\w+)\s+(\w+)\s+([\w_]+)\s+(\(\w+\))\s+([\w\d ,]+)?\r\n', temporaryBuffer)

        for vlan in vlans:
            dictionary = {}
            for key, value in zip(keys, vlan):
                if key == 'Ports':
                    dictionary[key] = value.split(', ')
                else:
                    dictionary[key] = value
            result.append(dictionary)

    #Return results
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = lib.returnStruct(returnCode=0, buffer=bufferString, data=result)
    return returnCls
