##########################################################################################
# Name:        switch.CLI.interface.InterfaceEnable
#
# Namespace:   switch.CLI.interface
#
# Author:      Vince Mendoza
#
# Purpose:     Library function enable / disable interface
#
# Params:      deviceObj - device object
#              interface - interface number context
#              enable    - True to Enable, False to disable
#
# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data: 
#
##PROC-###################################################################################
import common
import lib
import re
import time

def InterfaceEnable(**kwargs):
    deviceObj = kwargs.get('deviceObj', None)
    interface = kwargs.get('interface', None)
    enable = kwargs.get('enable', True)
    
    # If Device object is not passed, we need to error out
    if deviceObj is None or interface is None:
        common.LogOutput('error', "Need to pass switch device object deviceObj and interface to this routine")
        returnCls = lib.returnStruct(returnCode=1)
        return returnCls

    overallBuffer = []
    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        common.LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls

    # Get into config context
    returnStructure = deviceObj.ConfigVtyShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        common.LogOutput('error', "Failed to get vtysh config prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    
    # Get into the interface context
    command = "interface " + str(interface)
    returnStructure = deviceObj.DeviceInteract(command=command)
    retCode = returnStructure['returnCode']
    overallBuffer.append(returnStructure['buffer'])
    if retCode != 0:
        common.LogOutput('error', "Failed to enter interface context for interface " + str(interface))
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.retStruct(returnCode=retCode, buffer=bufferString)
        return returnCls

    # Need to get into the Interface context
    if enable is True:
        command = "no shutdown\r"
        returnStructure = deviceObj.DeviceInteract(command=command)
        retCode = returnStructure['returnCode']
        overallBuffer.append(returnStructure['buffer'])
        if retCode != 0:
            common.LogOutput('error', "Failed to enable interface " + str(interface))
        else:
            common.LogOutput('debug', "Enabled interface " + str(interface))
    else:
        command = "shutdown\r"
        returnStructure = deviceObj.DeviceInteract(command=command)
        retCode = returnStructure['returnCode']
        overallBuffer.append(returnStructure['buffer'])
        if retCode != 0:
            common.LogOutput('error', "Failed to disable interface " + str(interface))
        else:
            common.LogOutput('debug', "Disabled interface " + str(interface))
    
    # Get out of the interface context
    command = "exit \r"
    returnStructure = deviceObj.DeviceInteract(command=command)
    retCode = returnStructure['returnCode']
    overallBuffer.append(returnStructure['buffer'])
    if retCode != 0:
        common.LogOutput('error', "Failed to exit the interface context")

    # Get into config context
    returnStructure = deviceObj.ConfigVtyShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        common.LogOutput('error', "Failed to exit vtysh config prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.retStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls
    
    # Get out of vtyshell
    returnStructure = deviceObj.VtyshShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        common.LogOutput('error', "Failed to exit vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.retStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls

    #Return results
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = lib.returnStruct(returnCode=0, buffer=bufferString)
    return returnCls

