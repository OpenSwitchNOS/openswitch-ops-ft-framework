##########################################################################################
# Name:        opstestfw.switch.CLI.LAG.InterfaceLacpPortPriorityConfig
#
# Namespace:   opstestfw.switch.CLI.LAG
#
# Author:      Randall Loaiza
#
# Purpose:     Library function to configure LAG parameters on an interface
#
# Params:      deviceObj - device object.
#              interface - interface to config   
#              lacpPortPriority - Range between 1 and 65535 to assign priority of interface between members of same dynamic LAG (LACP)
#
# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data:  {}
#
##PROC-###################################################################################

from opstestfw import *
import re
import time

def InterfaceLacpPortPriorityConfig(**kwargs):
    
    deviceObj = kwargs.get('deviceObj', None)
    interface = kwargs.get('interface', None)
    lacpPortPriority = kwargs.get('lacpPortPriority', None)


    #Definition of the return dictionary 
    returnCode = 0
    retStruct = dict()
    overallBuffer = []
    bufferString = ""

    #Check if parameter required is used, if not return error -- Constrains

    if deviceObj is None:
        LogOutput('error', "Need to pass switch device object deviceObj")
        returnCode = 1
        returnCls = returnStruct(returnCode=returnCode, buffer=overallBuffer, data=retStruct)
        return returnCls

    if lacpPortPriority is None:
        LogOutput('error', "Need to pass the Port priority value")
        returnCode = 1
        returnCls = returnStruct(returnCode=returnCode, buffer=overallBuffer, data=retStruct)
        return returnCls

    #############################################################################################
    # Navigation to the config Context
    #############################################################################################
    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell(enter=True)
    overallBuffer.append(returnStructure.buffer())
    returnCode = returnStructure.returnCode()
    if returnCode != 0:
        LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString,data=retStruct)
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
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString, data=retStruct)
        return returnCls
    
    ##############################################################################################
    # Getting into the interface
    ##############################################################################################

    command = "interface " + str(interface) + "\r"
    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        LogOutput('error', "Failed to get the interface prompt " + deviceObj.device)
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString, data=retStruct)
        return returnCls    


    ##############################################################################################
    # Assign a port-priority for lacp
    ##############################################################################################

    #if enable is True: Removing this part, because no matter if disable or enable always has to set the value
    command = "lacp port-priority "+ str(lacpPortPriority) +"\r"
    returnDict = deviceObj.DeviceInteract(command=command)
    retCode = returnDict['returnCode']
    overallBuffer.append(returnDict['buffer'])
    if retCode != 0:
        opstestfw.LogOutput('error', "Failed to configure the port-priority to the interface" + str(interface))
    else:
        opstestfw.LogOutput('debug', "Port-priority assigned" + str(interface))       

    ##############################################################################################
    # End assign a port-priority for lacp
    ##############################################################################################



    #############################################################################################
    # Process of return to the Root context
    #############################################################################################

    # Get out of the interface context
    command = "exit \r"
    returnDict = deviceObj.DeviceInteract(command=command)
    retCode = returnDict['returnCode']
    overallBuffer.append(returnDict['buffer'])
    if retCode != 0:
        LogOutput('error', "Failed to exit the interface context")

    # Get out of  config context
    returnStructure = deviceObj.ConfigVtyShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to get out of vtysh config context")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    
    # Get out of vtyshell
    returnStructure = deviceObj.VtyshShell(enter=False)
    retCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if retCode != 0:
        LogOutput('error', "Failed to exit vty shell")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=1, buffer=bufferString, data=retStruct)
        return returnCls
    bufferString = ""
    for curLine in overallBuffer:
            bufferString += str(curLine)
    returnCls = returnStruct(returnCode=0, buffer=bufferString, data=retStruct)
    return returnCls