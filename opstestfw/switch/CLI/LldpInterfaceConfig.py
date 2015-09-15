##########################################################################################
# Name:        opstestfw.switch.CLI.lldp.LldpInterfaceConfig
#
# Namespace:   opstestfw.switch.CLI.lldp
#
# Author:      Vince Mendoza
#
# Purpose:     Library function configure lldp interface context settings
#
# Params:      deviceObj - device object
#              interface - interface number context
#              transmission - True turns on transmission / False turns off transmission
#              reception - True turns on transmission / False turns off transmission
#
# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data: 
#
##PROC-###################################################################################

from opstestfw import *
import re
import time

def LldpInterfaceConfig(**kwargs):
    deviceObj = kwargs.get('deviceObj', None)
    interface = kwargs.get('interface', None)
    transmission = kwargs.get('transmission', None)
    reception = kwargs.get('reception', None)
    
    # If Device object is not passed, we need to error out
    if deviceObj is None or interface is None:
        LogOutput('error', "Need to pass switch device object deviceObj and interface to this routine")
        returnCls = returnStruct(returnCode=1)
        return returnCls

    overallBuffer = []
    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls

    # Get into config context
    returnStructure = deviceObj.ConfigVtyShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to get vtysh config prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    
    # Get into the interface context
    command = "interface " + str(interface)
    returnDict = deviceObj.DeviceInteract(command=command)
    retCode = returnDict['returnCode']
    overallBuffer.append(returnDict['buffer'])
    if retCode != 0:
        LogOutput('error', "Failed to enter interface context for interface " + str(interface))
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    # Need to get into the Interface context
    if transmission is True:
        command = "lldp transmission\r"
        returnDict = deviceObj.DeviceInteract(command=command)
        retCode = returnDict['returnCode']
        overallBuffer.append(returnDict['buffer'])
        if retCode != 0:
            LogOutput('error', "Failed to enable lldp tranmission on interface " + str(interface))
        else:
            LogOutput('debug', "Enabled lldp transmission on interface " + str(interface))

    if transmission is False:
        command = "no lldp transmission\r"
        returnDict = deviceObj.DeviceInteract(command=command)
        retCode = returnDict['returnCode']
        overallBuffer.append(returnDict['buffer'])
        if retCode != 0:
            LogOutput('error', "Failed to disable lldp transmission on interface " + str(interface))
        else:
            LogOutput('debug', "Disabled lldp transmission on interface " + str(interface))
    
    if reception is True:
        command = "lldp reception\r"
        returnDict = deviceObj.DeviceInteract(command=command)
        retCode = returnDict['returnCode']
        overallBuffer.append(returnDict['buffer'])
        if retCode != 0:
            LogOutput('error', "Failed to enable lldp reception on interface  " + str(interface))
        else:
            LogOutput('debug', "Enabled lldp reception on interface " + str(interface))
    
    if reception is False:
        command = "no lldp reception\r"
        returnDict = deviceObj.DeviceInteract(command=command)
        retCode = returnDict['returnCode']
        overallBuffer.append(returnDict['buffer'])
        if retCode != 0:
            LogOutput('error', "Failed to disable lldp reception on interface  " + str(interface))
        else:
            LogOutput('debug', "Disabled lldp reception on interface " + str(interface))
    
    # Get out of the interface context
    command = "exit \r"
    returnDict = deviceObj.DeviceInteract(command=command)
    retCode = returnDict['returnCode']
    overallBuffer.append(returnDict['buffer'])
    if retCode != 0:
        LogOutput('error', "Failed to exit the interface context")
        
    
    # Get into config context
    returnStructure = deviceObj.ConfigVtyShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to exit vtysh config prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    
    # Get out of vtyshell
    returnStructure = deviceObj.VtyshShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to exit vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    #Return results
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = returnStruct(returnCode=0, buffer=bufferString)
    return returnCls

