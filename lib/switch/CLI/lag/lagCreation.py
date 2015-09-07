##########################################################################################
# Name:        switch.CLI.lagCreation
#
# Namespace:   switch.CLI.lag
#
# Author:      Jose Pablo Hernandez 
#
# Purpose:     Library function to create/delete a LAG
#
# Params:         deviceObj - Switch identifier
#                 lagId - LAG identifier
#                 configFlag - True for configuration/false for removing LAG   
#
# Returns:     JSON structure
#                   returnCode :- status of command(0 for pass , gets errorcodes for failure)
#                   data: -            Dictionary as per manipulated expect data
#                                         rawBuffer(Device buffer)
#
##PROC-###################################################################################

import lib

def lagCreation(**kwargs):
    #Params
    lagId = kwargs.get('lagId', None)
    deviceObj = kwargs.get('deviceObj', None)
    configFlag = kggMode = kwargs.get('configFlag', None)
    
    #Variables
    overallBuffer = []
    
    #If deviceObj, lagId or configFlag are not present, throw an error
    if deviceObj is None or lagId is None or configFlag is None:
        lib.LogOutput('error', "Need to pass deviceObj, lagId and configFlag to use this routine")
        rreturnCls = lib.returnStruct(returnCode=1)
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
    
    #Verify if creating or deleting a LAG
    if configFlag is True:
        #create LAG
        command = "interface lag %s\r" % str(lagId)
        returnDevInt = deviceObj.DeviceInteract(command=command)
        retCode = returnDevInt['returnCode']
        overallBuffer.append(returnDevInt['buffer'])
        if retCode != 0:
            lib.LogOutput('error', "Failed to create LAG " + str(lagId) + " on device " + deviceObj.device)
            bufferString = ""
            for curLine in overallBuffer:
                bufferString += str(curLine)
            returnCls = lib.returnStruct(returnCode=retCode, buffer=bufferString)
            return returnCls
        else:
            lib.LogOutput('debug', "Created LAG " + str(lagId) + " on device " + deviceObj.device)
        
        #exit LAG configuration context
        command = "exit\r"
        returnDevInt = deviceObj.DeviceInteract(command=command)
        retCode = returnDevInt['returnCode']
        overallBuffer.append(returnDevInt['buffer'])
        if retCode != 0:
            lib.LogOutput('error', "Failed to exit LAG " + str(lagId) + " configuration context")
            bufferString = ""
            for curLine in overallBuffer:
                bufferString += str(curLine)
            returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
            return returnCls
        
    else:
        #delete LAG
        command = "no interface lag %s\r" % str(lagId)
        returnDevInt = deviceObj.DeviceInteract(command=command)
        retCode = returnDevInt['returnCode']
        overallBuffer.append(returnDevInt['buffer'])
        if retCode != 0:
            lib.LogOutput('error', "Failed to delete LAG on device " + deviceObj.device)
            bufferString = ""
            for curLine in overallBuffer:
                bufferString += str(curLine)
            returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
            return returnCls
        else:
            lib.LogOutput('debug', "Deleted LAG context on device " + deviceObj.device)
    
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
    
    #Compile results to return
    bufferString = ""
    for curLine in overallBuffer:
            bufferString += str(curLine)
    returnCls = lib.returnStruct(returnCode=0, buffer=bufferString)
    return returnCls

    