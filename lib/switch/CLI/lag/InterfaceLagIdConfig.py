##########################################################################################
# Name:        switch.CLI.LAG.InterfaceLagIdConfig
#
# Namespace:   switch.CLI.LAG
#
# Author:      Randall Loaiza
#
# Purpose:     Library function to configure LAG parameters on an interface
#
# Params:      deviceObj - device object.
#              interface - interface to config   
#              lagId - Name to identify the LAG which the interface belongs
#              enable - True for configuration/false for removing LAG   
#
# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data: {}
#
##PROC-###################################################################################

from lib import *
import re
import time

def InterfaceLagIdConfig(**kwargs):
    deviceObj = kwargs.get('deviceObj', None)
    interface = kwargs.get('interface', None)
    lagId = kwargs.get('lagId', None)
    enable  = kwargs.get('enable', True)
    
    #Definition of the return dictionary 
    returnCode = 0
    retStruct = dict()
    overallBuffer = []
    bufferString = ""

    # If Device object is not passed, we need to error out
    if deviceObj is None:
        LogOutput('error', "Need to pass switch device object deviceObj")
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
    #  Link with the lag ID
    ##############################################################################################

    if enable is True:
        command = "lag "+ str(lagId) +"\r"
        returnDict = deviceObj.DeviceInteract(command=command)
        retCode = returnDict['returnCode']
        overallBuffer.append(returnDict['buffer'])
        if retCode != 0:
            LogOutput('error', "Failed to configure the LAG ID" + str(interface))
        else:
            LogOutput('info', "LAG ID linked with the Interface " + str(interface))

    else :
        command = "no lag "+ str(lagId) +"\r"
        returnDict = deviceObj.DeviceInteract(command=command)
        retCode = returnDict['returnCode']
        overallBuffer.append(returnDict['buffer'])
        if retCode != 0:
            LogOutput('error', "Failed to disable the LAG ID for the interface" + str(interface))
        else:
            LogOutput('info', "LAG ID No longer assign to the interface" + str(interface))

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

