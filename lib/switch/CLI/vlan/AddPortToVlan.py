##########################################################################################
# Name:        switch.CLI.interface.AddPortToVlan.py
#
# Namespace:   switch.CLI.interface
#
# Author:      Diego Hurtado
#
# Purpose:     Library function to add a port to a VLAN.
#
# Params:      deviceObj - device object.
#              vlanId - Id of the VLAN to be used to add the port to.
#              interface - Id of the interface to add to the VLAN.
#               Routing will be disabled in the interface.
#               Send here a string "lag X" to add a lag.
#              access - True to add access to the command, False to add
#               trunk to the command. Defaults to False.
#              allowed - True to add allowed after trunk, False to add
#               native after trunk. Defaults to False.
#              tag - True to add tag after native. False to add nothing.
#               Defaults to False.
#              config - True if a port is to be added to the VLAN,
#               False if a port is to be removed from a VLAN.
#               Defaults to True.
#
# Returns:     returnStruct - return object with the following attributes:
#               returnCode - integer set to 0 if the function ended up succesfully
#                            or set to 1 if an error occurred.
#               data - None
#               buffer - string with the output of the command execution
#
##PROC-###################################################################################

import lib
import re
import time

def AddPortToVlan(**kwargs):
    deviceObj = kwargs.get('deviceObj', None)
    vlanId = kwargs.get('vlanId', None)
    interface = kwargs.get('interface', None)
    access = kwargs.get('access', False)
    allowed = kwargs.get('allowed', False)
    tag = kwargs.get('tag', False)
    config = kwargs.get('config', True)

    overallBuffer = []
    # If Device object is not passed, we need to error out
    if deviceObj is None or vlanId is None or interface is None:
        lib.LogOutput('error', "Need to pass switch device object deviceObj, interface interface and VLAN Id vlanId to this routine")
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

    # Get into config context
    returnStructure = deviceObj.ConfigVtyShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        lib.LogOutput('error', "Failed to get vtysh config prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    
    command = "interface " + str(interface) + "\n"

    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        lib.LogOutput('error', "Failed to get into interface prompt."+ command)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    else:
        lib.LogOutput('debug', "Got into interface prompt." + command)
 
    command = "no routing\n"

    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        lib.LogOutput('error', "Failed to disable routing in the interface."+ command)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    else:
        lib.LogOutput('debug', "Exited interface context." + command)
 
    if config:
        command = ""
    else:
        command = "no "

    command = command + "vlan "

    if access:
        command = command + "access " + str(vlanId) + "\n"
    else:
        command = command + "trunk "
        if allowed:
            command = command + "allowed " + str(vlanId) + "\n"
        else:
            command = command + "native "
            if tag:
                command = command + "tag"
            else:
                command = command + str(vlanId) + "\n"

    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        if config:
            lib.LogOutput('error', "Failed to add the port to the VLAN."+ command)
        else:
            lib.LogOutput('error', "Failed to remove the port from the VLAN."+ command)

        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    else:
        lib.LogOutput('debug', "Added the port to the VLAN." + command)
 
    command = "end\n"

    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        lib.LogOutput('error', "Failed to exit interface context."+ command)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    else:
        lib.LogOutput('debug', "Exited interface context." + command)
    
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

    #Return results
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = lib.returnStruct(returnCode=0, buffer=bufferString)
    return returnCls
