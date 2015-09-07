##########################################################################################
# Name:        switch.CLI.lag.lagHeartbeat
#
# Namespace:   switch.CLI.lag
#
# Author:      Jose Pablo Hernandez 
#
# Purpose:     Library function to configure a LAGs mode (static/dynamic)
#
# Params:         deviceObj - Switch identifier
#                 lagId - LAG identifier
#                 lacpMode - static: Static LAG - active: Active dynamic LAG - passive: Passive dynamic LAG
#
# Returns:     JSON structure
#                   returnCode :- status of command(0 for pass , gets errorcodes for failure)
#                   data: -            Dictionary as per manipulated expect data
#                                         rawBuffer(Device buffer)
#
##PROC-###################################################################################

import lib

def lagMode(**kwargs):
    #Params
    lagId = kwargs.get('lagId', None)
    deviceObj = kwargs.get('deviceObj', None)
    lagMode = kwargs.get('lagMode', None)
    
    #Variables
    overallBuffer = []
    
    #If deviceObj, lagId or lagMode are not present, thorw an error
    if deviceObj is None or lagId is None or lagMode is None:
        common.lib.LogOutput('error', "Need to pass deviceObj, lagId and lagMode to use this routinge")
        returnJson = common.ReturnJSONCreate(returnCode=1)
        return returnJson
    
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
    command = "interface lag %s\r" % str(lagId)
    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        lib.LogOutput('error', "Failed to create LAG " + str(lagId) + " on device " + deviceObj.device)
    else:
        lib.LogOutput('debug', "Created LAG " + str(lagId) + " on device " + deviceObj.device)
     
     #configure LAG mode
     
    if str(lagMode) != 'static':
        command = "lacp mode %d\r" % lagMode
    else:
        command = "no lacp"
    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        lib.LogOutput('error', "Failed to configure LACP mode to " + lagMode + " on device " + deviceObj.device)
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=retCode, buffer=bufferString)
        return returnCls
    else:
        lib.LogOutput('debug', "Changed LACP mode to " + lagMode + " on device " + deviceObj.device)
        
    #exit LAG configuration context
    command = "exit\r"
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
