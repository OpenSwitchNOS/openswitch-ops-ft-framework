##########################################################################################
# Name:        opstestfw.switch.CLI.lag.lagHash
#
# Namespace:   opstestfw.switch.CLI.lag
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

import opstestfw

def lagHash(**kwargs):
    #Params
    lagId = kwargs.get('lagId', None)
    deviceObj = kwargs.get('deviceObj', None)
    hashType = kwargs.get('hashType', 'l3-src-dst')
    
    #Variables
    overallBuffer = []
    finalReturnCode = 0
    
    #If deviceObj, lagId, hashType are not present, display an error
    if deviceObj is None or lagId is None:
        common.opstestfw.LogOutput('error', "Need to pass deviceObj and lagId to use this routine")
        returnCls = opstestfw.returnStruct(returnCode=1)
        return returnCls
    
    #If hashType is different from l2-src-dst and l3-src-dst throw an error
    if hashType != 'l2-src-dst' and hashType != 'l3-src-dst':
        common.opstestfw.LogOutput('error', "hashType must be l2-src-dst or l3-src-dst")
        returnJson = common.ReturnJSONCreate(returnCode=1)
        return returnJson
    
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
    
     #Generate command to query switch
    if hashType == 'l2-src-dst':
        command = "hash l2-src-dst"
    else:
        command = "hash l2-src-dst"
     
    finalReturnCode = deviceObj.DeviceInteract(command=command)
    finalReturnCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if finalReturnCode != 0:
        opstestfw.LogOutput('error', "Failed to configure " + hashType + " hashing on interface lag " + str(lagId) + " on device " + deviceObj.device)
    else:
        opstestfw.LogOutput('debug', "Configured l2-src-dst hashing on interface lag " + str(lagId) + " on device " + deviceObj.device)
        
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
        returnCls = opstestfw.returnStruct(returnCode=1, buffer=bufferString)
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
