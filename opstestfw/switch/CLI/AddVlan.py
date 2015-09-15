##########################################################################################
# Name:        opstestfw.switch.CLI.interface.AddVlan.py
#
# Namespace:   opstestfw.switch.CLI.interface
#
# Author:      Diego Hurtado
#
# Purpose:     Library function to add a VLAN.
#
# Params:      deviceObj - device object
#              vlanId - Id of the VLAN to be added. This is casted to string.
#              config - True if a VLAN is to be added, False if a VLAN is to be deleted.
#               Defaults to True.
#
# Returns:     returnStruct - return object with the following attributes:
#               returnCode - integer set to 0 if the function ended up succesfully
#                            or set to 1 if an error occurred.
#               data - None
#               buffer - string with the output of the command execution
#
##PROC-###################################################################################

import opstestfw
import re
import time

def AddVlan(**kwargs):
    deviceObj = kwargs.get('deviceObj', None)
    vlanId = kwargs.get('vlanId', None)
    config = kwargs.get('config', True)

    overallBuffer = []
    # If Device object is not passed, we need to error out
    if deviceObj is None or vlanId is None:
        opstestfw.LogOutput('error', "Need to pass switch device object deviceObj and VLAN Id vlanId to this routine")
        returnCls = opstestfw.returnStruct(returnCode=1)
        return returnCls

    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        opstestfw.LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = opstestfw.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    # Get into config context
    returnStructure = deviceObj.ConfigVtyShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        opstestfw.LogOutput('error', "Failed to get vtysh config prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = opstestfw.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    
    if config:
        command = ""
    else:
        command = "no "

    command = command + "vlan " + str(vlanId) + "\n"

    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        if config:
            opstestfw.LogOutput('error', "Failed to create VLAN or failed to get into VLAN context."+ command)
        else:
            opstestfw.LogOutput('error', "Failed to delete VLAN."+ command)
        returnCls = opstestfw.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    else:
        if config:
            opstestfw.LogOutput('debug', "Created VLAN or entered VLAN context." + command)
        else:
            opstestfw.LogOutput('debug', "Deleted VLAN." + command)
 
    command = "end\n"

    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        opstestfw.LogOutput('error', "Failed to exit vlan context."+ command)
        returnCls = opstestfw.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    else:
        opstestfw.LogOutput('debug', "Exited VLAN context." + command)
    
    # Get out of vtyshell
    returnStructure = deviceObj.VtyshShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        opstestfw.LogOutput('error', "Failed to exit vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = opstestfw.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    #Return results
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = opstestfw.returnStruct(returnCode=0, buffer=bufferString)
    return returnCls
