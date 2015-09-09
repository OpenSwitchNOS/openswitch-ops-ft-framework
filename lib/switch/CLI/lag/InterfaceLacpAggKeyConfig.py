##########################################################################################
# Name:        switch.CLI.LAG.InterfaceLacpAggKeyConfig
#
# Namespace:   switch.CLI.LAG
#
# Author:      Randall Loaiza
#
# Purpose:     Library function to configure LAG parameters on an interface
#
# Params:      deviceObj - device object.
#              interface - interface to config   
#              lacpAggKey - Range betwen 1 and 65535. Key used to identify all members of LAG to be of the same 2 switches. Will probably not be added in Basil
#
# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data: {}
#
##PROC-###################################################################################

from lib import *
import re
import time

def InterfaceLacpAggKeyConfig(**kwargs):

    deviceObj = kwargs.get('deviceObj', None)
    interface = kwargs.get('interface', None)
    lacpAggKey = kwargs.get('lacpAggKey', None)

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

    if lacpAggKey is None:
        LogOutput('error', "Need to pass the Port ID value")
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
    # Assign a aggregation-key for lacp
    ##############################################################################################

    #if enable is True: Removing this part, because no matter if disable or enable always has to set the value
    command = "lacp aggregation-key "+ str(lacpAggKey) +"\r"
    returnDict = deviceObj.DeviceInteract(command=command)
    retCode = returnDict['returnCode']
    overallBuffer.append(returnDict['buffer'])
    if retCode != 0:
        lib.LogOutput('error', "Failed to configure the aggregation-key to the interface" + str(interface))
    else:
        lib.LogOutput('debug', "Aggregation-key assigned" + str(interface))   

    ##############################################################################################
    # End Assign a aggregation-key for lacp
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