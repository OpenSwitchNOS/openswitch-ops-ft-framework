##########################################################################################
# Name:        switch.CLI.lag.lagFallback
#
# Namespace:   switch.CLI.lag
#
# Author:      Jose Pablo Hernandez 
#
# Purpose:     Library function to configure fallback settings for a LAG working in dynamic mode
#
# Params:         deviceObj - Switch identifier
#                 lagId - LAG identifier
#                 fallbackFlag - off: Static LAG - active: Active dynamic LAG - passive: Passive dynamic LAG
#
# Returns:     JSON structure
#                   returnCode :-      status of command(0 for pass , gets errorcodes for failure)
#                   data: -            Dictionary as per manipulated expect data
#                                         rawBuffer(Device buffer)
#
##PROC-###################################################################################

import lib

def lagFallback(**kwargs):
    #Params
    lagId = kwargs.get('lagId', None)
    deviceObj = kwargs.get('deviceObj', None)
    fallbackFlag = kwargs.get('fallbackFlag', True)
    
    #Variables
    overallBuffer = []
    
    #If deviceObj, lagId or fallbackFlag are not passed, we need to throw an error
    if deviceObj is None or lagId is None:
        common.lib.LogOutput('error', "Need to pass deviceObj and lagId to use this routine")
        returnCls = lib.returnStruct(returnCode=1)
        return returnCls
    
    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell(enter=True)
    overallBuffer.append(returnStructure.buffer())
    returnCode = returnStructure.returnCode()
    if returnCode != 0:
        lib.LogOutput('error', "Failed to get vtysh prompt")
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
        lib.LogOutput('error', "Failed to get vtysh config prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls
    
    #enter LAG configuration context
    command = "interface lag %s" % str(lagId)
    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        lib.LogOutput('error', "Failed to create LAG " + str(lagId) + " on device " + deviceObj.device)
    else:
        lib.LogOutput('debug', "Created LAG " + str(lagId) + " on device " + deviceObj.device)
     
     #configure LAG's LACP fallback settings
     
    if fallbackFlag is True:
        command = "lacp fallback"
    else:
        command = "no lacp fallback"
    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        if fallbackFlag is True:
            lib.LogOutput('error', "Failed to enable LACP fallback on interface lag " + str(lagId) + " on device " + deviceObj.device)
        else:
            lib.LogOutput('error', "Failed to disable LACP fallback on interface lag " + str(lagId) + " on device " + deviceObj.device)
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=retCode, buffer=bufferString)
        return returnCls
    else:
        if fallbackFlag is True:
            lib.LogOutput('debug', "Enabled LACP fallback on interface lag " + str(lagId) + " on device " + deviceObj.device)
        else:
            lib.LogOutput('debug', "Disabled LACP fallback on interface lag " + str(lagId) + " on device " + deviceObj.device)
        
    #exit LAG configuration context
    command = "exit"
    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        lib.LogOutput('error', "Failed to exit LAG " + str(lagId) + " configuration context")
        
    
    # Get out of  config context
    returnStructure = deviceObj.ConfigVtyShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        lib.LogOutput('error', "Failed to get out of vtysh config context")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    
    # Get out of vtyshell
    returnStructure = deviceObj.VtyshShell(enter=False)
    retCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if retCode != 0:
        lib.LogOutput('error', "Failed to exit vty shell")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    #Compile information to return
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = lib.returnStruct(returnCode=0, buffer=bufferString)
    return returnCls
