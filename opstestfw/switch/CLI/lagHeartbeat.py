##########################################################################################
# Name:        opstestfw.switch.CLI.lag.lagHeartbeat
#
# Namespace:   opstestfw.switch.CLI.lag
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

import opstestfw

def lagHeartbeat(**kwargs):
    #Params
    lagId = kwargs.get('lagId', None)
    deviceObj = kwargs.get('deviceObj', None)
    lacpFastFlag = kwargs.get('lacpFastFlag', True)
    
    #Variables
    overallBuffer = []
    finalReturnCode = 0
    
    #If device, LAG Id or lacpFastFlag are not passed, return an error
    if deviceObj is None or lagId is None or lacpFastFlag is None:
        common.opstestfw.LogOutput('error', "Need to pass deviceObj and lagId to use this routine")
        returnCls= opstestfw.returStruct(returnCode=1)
        return returnJCls
    
    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell(enter=True)
    overallBuffer.append(returnStructure.buffer())
    returnCode = returnStructure.returnCode()
    if returnCode != 0:
        opstestfw.LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = opstestfw.returnStruct(returnCode=returnCode, buffer=bufferString)
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
        returnCls = opstestfw.returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls
    
    #enter LAG configuration context
    command = "interface lag %s" % str(lagId)
    returnDevInt = deviceObj.DeviceInteract(command=command)
    returnCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if returnCode != 0:
        opstestfw.LogOutput('error', "Failed to create LAG " + str(lagId) + " on device " + deviceObj.device)
    else:
        opstestfw.LogOutput('debug', "Created LAG " + str(lagId) + " on device " + deviceObj.device)
     
     #configure LAG heartbeat settings
     
    command = ""
    if lacpFastFlag is False:
        command = "no "
    command += "lacp rate fast"
    finalReturnCode = deviceObj.DeviceInteract(command=command)
    returnCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if finalReturnCode != 0:
        if lacpFastFlag is True:
            opstestfw.LogOutput('error', "Failed to configure LACP fast heartbeat on interface lag " + str(lagId) + " on device " + deviceObj.device)
        else:
            opstestfw.LogOutput('error', "Failed to configure LACP slow heartbeat on interface lag " + str(lagId) + " on device " + deviceObj.device)
    else:
        if lacpFastFlag is True:
            opstestfw.LogOutput('debug', "Configured LACP fast heartbeat on interface lag " + str(lagId) + " on device " + deviceObj.device)
        else:
            opstestfw.LogOutput('debug', "Configure LACP slow heartbeat on interface lag " + str(lagId) + " on device " + deviceObj.device)
        
    #exit LAG configuration context
    command = "exit"
    returnDevInt = deviceObj.DeviceInteract(command=command)
    returnCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if returnCode != 0:
        opstestfw.LogOutput('error', "Failed to exit LAG " + str(lagId) + " configuration context")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = opstestfw.returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls
    
    # Get out of  config context
    returnStructure = deviceObj.ConfigVtyShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        opstestfw.LogOutput('error', "Failed to get out of vtysh config context")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = opstestfw.returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls
    
    # Get out of vtyshell
    returnStructure = deviceObj.VtyshShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        opstestfw.LogOutput('error', "Failed to exit vty shell")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = opstestfw.returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls

    #Compile information to return
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = opstestfw.returnStruct(returnCode=finalReturnCode, buffer=bufferString)
    return returnCls
