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
#                 lacpMode - off: Static LAG - active: Active dynamic LAG - passive: Passive dynamic LAG
#
# Returns:     JSON structure
#                   returnCode :- status of command(0 for pass , gets errorcodes for failure)
#                   data: -            Dictionary as per manipulated expect data
#                                         rawBuffer(Device buffer)
#
##PROC-###################################################################################

import lib
import re
import pexpect

def lagMode(**kwargs):
    #Params
    lagId = kwargs.get('lagId', None)
    deviceObj = kwargs.get('deviceObj', None)
    lacpMode = kwargs.get('lacpMode', None)
    
    #Variables
    overallBuffer = []
    initialStatus = ''
    
    #If deviceObj, lagId or lacpMode are not present, thorw an error
    if deviceObj is None or lagId is None or lacpMode is None:
        lib.LogOutput('error', "Need to pass deviceObj, lagId and lacpMode to use this routine")
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
    
    # Query switch for LAG configuration
    command = 'show lacp aggregates lag' + str(lagId)
    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        lib.LogOutput('error', "Could not obtain LAG LACP mode initial status")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=retCode, buffer=bufferString)
    
    ########################TEMPORARY########################################
    #Obtain result of command
    buffer2 = ''
    while True:
        result = deviceObj.expectHndl.expect(['# ',pexpect.TIMEOUT],timeout=5)
        buffer2 += str(deviceObj.expectHndl.before) + str(deviceObj.expectHndl.after)
        if result == 1:
            break
    overallBuffer.append(buffer2)
    ######################END OF TEMPORARY########################################
    
    #Parse buffer for values of interest
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    result = re.search('Aggregate mode[ ]+: (off|passive|active)', bufferString)
    if result is None:
        lib.LogOutput('error', "Could not identify LAG LACP mode initial status")
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    else:
        initialStatus = result.group(1)
        lib.LogOutput('debug', "LAG LACP mode initial status identified as " + initialStatus)
        
    #Verify if the LAG was already in static mode and will be changed again
    if initialStatus == lacpMode and lacpMode == 'off':
        lib.LogOutput('debug', "LACP mode is set to off already. No change is performed")
    else:
        
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
            lib.LogOutput('error', "Failed to enter LAG" + str(lagId) + " configuration context on device " + deviceObj.device)
            bufferString = ""
            for curLine in overallBuffer:
                bufferString += str(curLine)
            returnCls = lib.returnStruct(returnCode=retCode, buffer=bufferString)
        else:
            lib.LogOutput('debug', "Entered LAG" + str(lagId) + " configuration context on device " + deviceObj.device)
         
         #configure LAG mode
         
        if str(lacpMode) != 'off':
            command = "lacp mode " + str(lacpMode)
        else:
            command = "no lacp mode " + str(lacpMode)
        returnDevInt = deviceObj.DeviceInteract(command=command)
        retCode = returnDevInt['returnCode']
        overallBuffer.append(returnDevInt['buffer'])
        if retCode != 0:
            lib.LogOutput('error', "Failed to configure LACP mode to " + lacpMode + " on device " + deviceObj.device)
            bufferString = ""
            for curLine in overallBuffer:
                bufferString += str(curLine)
            returnCls = lib.returnStruct(returnCode=retCode, buffer=bufferString)
            return returnCls
        else:
            lib.LogOutput('debug', "Changed LACP mode to " + lacpMode + " on device " + deviceObj.device)
            
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
