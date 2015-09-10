##########################################################################################
# Name:        switch.CLI.lag.lagHeartbeat
#
# Namespace:   switch.CLI.lag
#
# Author:      Jose Pablo Hernandez 
#
# Purpose:     Library function to configure heartbeat speed on a LAG
#
# Params:         deviceObj - Switch identifier
#                 lagId - LAG identifier
#                 lacpFastFlag - True for LACP fast heartbeat, false for slow heartbeat
#
# Returns:     JSON structure
#                   returnCode :- status of command(0 for pass , gets error codes for failure)
#                   data: -            Dictionary as per manipulated expect data
#                                         rawBuffer(Device buffer)
#
##PROC-###################################################################################

import lib

def lagHeartbeat(**kwargs):
    #Params
    lagId = kwargs.get('lagId', None)
    deviceObj = kwargs.get('deviceObj', None)
    lacpFastFlag = kwargs.get('lacpFastFlag', True)
    
    #Variables
    overallBuffer = []
    
    #If device, LAG Id or lacpFastFlag are not passed, return an error
    if deviceObj is None or lagId is None or lacpFastFlag is None:
        common.lib.LogOutput('error', "Need to pass deviceObj and lagId to use this routine")
        returnCls= lib.returStruct(returnCode=1)
        return returnJCls
    
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
     
     #configure LAG heartbeat settings
     
    command = ""
    if lacpFastFlag is False:
        command = "no "
    command += "lacp rate fast"
    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        if lacpFastFlag is True:
            lib.LogOutput('error', "Failed to configure LACP fast heartbeat on interface lag " + str(lagId) + " on device " + deviceObj.device)
        else:
            lib.LogOutput('error', "Failed to configure LACP slow heartbeat on interface lag " + str(lagId) + " on device " + deviceObj.device)
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=retCode, buffer=bufferString)
        return returnCls
    else:
        if lacpFastFlag is True:
            lib.LogOutput('debug', "Configured LACP fast heartbeat on interface lag " + str(lagId) + " on device " + deviceObj.device)
        else:
            lib.LogOutput('debug', "Configure LACP slow heartbeat on interface lag " + str(lagId) + " on device " + deviceObj.device)
        
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
