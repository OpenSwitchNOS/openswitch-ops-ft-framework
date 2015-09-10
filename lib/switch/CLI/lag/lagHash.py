##########################################################################################
# Name:        switch.CLI.lag.lagHash
#
# Namespace:   switch.CLI.lag
#
# Author:      Jose Pablo Hernandez 
#
# Purpose:     Library function to configure a LAGs hashing algortithm
#
# Params:         deviceObj - Switch identifier
#                 lagId - LAG identifier
#                 hashType - l2-src-dst/l3-dsrc-dst hashing algortihms
#
# Returns:     JSON structure
#                   returnCode :- status of command(0 for pass , gets errorcodes for failure)
#                   data: -            Dictionary as per manipulated expect data
#                                         rawBuffer(Device buffer)
#
##PROC-###################################################################################

import lib

def lagHash(**kwargs):
    #Params
    lagId = kwargs.get('lagId', None)
    deviceObj = kwargs.get('deviceObj', None)
    hashType = kwargs.get('hashType', 'l3-src-dst')
    
    #Variables
    overallBuffer = []
    
    #If deviceObj, lagId, hashType are not present, display an error
    if deviceObj is None or lagId is None:
        common.lib.LogOutput('error', "Need to pass deviceObj and lagId to use this routine")
        returnCls = lib.returnStruct(returnCode=1)
        return returnCls
    
    #If hashType is different from l2-src-dst and l3-src-dst throw an error
    if hashType != 'l2-src-dst' and hashType != 'l3-src-dst':
        common.lib.LogOutput('error', "hashType must be l2-src-dst or l3-src-dst")
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
     
    if hashType == 'l2-src-dst':
        command = "hash l2-src-dst"
        returnDevInt = deviceObj.DeviceInteract(command=command)
        retCode = returnDevInt['returnCode']
        overallBuffer.append(returnDevInt['buffer'])
        if retCode != 0:
            lib.LogOutput('error', "Failed to configure l2-src-dst hashing on interface lag " + str(lagId) + " on device " + deviceObj.device)
            bufferString = ""
            for curLine in overallBuffer:
                bufferString += str(curLine)
            returnCls = lib.returnStruct(returnCode=retCode, buffer=bufferString)
            return returnCls
        else:
            lib.LogOutput('debug', "Configured l2-src-dst hashing on interface lag " + str(lagId) + " on device " + deviceObj.device)
    else:
        if hashType == 'l3-src-dst':
            command = "no hash l2-src-dst"
            returnDevInt = deviceObj.DeviceInteract(command=command)
            retCode = returnDevInt['returnCode']
            overallBuffer.append(returnDevInt['buffer'])
            if retCode != 0:
                lib.LogOutput('error', "Failed to configure l3-src-dst hashing on interface lag " + str(lagId) + " on device " + deviceObj.device)
                bufferString = ""
                for curLine in overallBuffer:
                    bufferString += str(curLine)
                returnCls = lib.returnStruct(returnCode=retCode, buffer=bufferString)
                return returnCls
            else:
                lib.LogOutput('debug', "Configured l3-src-dst hashing on interface lag " + str(lagId) + " on device " + deviceObj.device)
        
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
