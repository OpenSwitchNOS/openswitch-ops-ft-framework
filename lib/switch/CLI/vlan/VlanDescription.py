##########################################################################################
# Name:        switch.CLI.interface.VlanDescription.py
#
# Namespace:   switch.CLI.interface
#
# Author:      Diego Hurtado
#
# Purpose:     Library function to set a VLAN description.
#
# Params:      deviceObj - device object
#              vlanId - Id of the VLAN to be added. This is casted to string.
#              description - string with the VLAN description. This is casted to string.
#              config - True if a VLAN description is to be added,
#               False if a VLAN description is to be deleted.
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

def VlanDescription(**kwargs):
    deviceObj = kwargs.get('deviceObj', None)
    vlanId = kwargs.get('vlanId', None)
    description = kwargs.get('description', None)
    config = kwargs.get('config', True)
    
    overallBuffer = []
    # If Device object is not passed, we need to error out
    if deviceObj is None or description is None or vlanId is None:
        lib.LogOutput('error', "Need to pass switch device object deviceObj, VLAN id vlanId and VLAN description description to this routine")
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
    
    command = "vlan " + str(vlanId) + "\n"

    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        lib.LogOutput('error', "Failed to get into vlan prompt."+ command)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    else:
        lib.LogOutput('debug', "Created VLAN." + command)

    if config:
        command = ""
    else:
        command = "no "

    command = command + "description " + str(description) + "\n"

    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        if config:
            lib.LogOutput('error', "Failed to set the VLAN description."+ command)
        else:
            lib.LogOutput('error', "Failed to remove the VLAN description."+ command)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    else:
        lib.LogOutput('debug', "VLAN description set." + command)
 
    command = "end\n"

    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        lib.LogOutput('error', "Failed to exit vlan context."+ command)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    else:
        lib.LogOutput('debug', "Exited VLAN context." + command)
   
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
