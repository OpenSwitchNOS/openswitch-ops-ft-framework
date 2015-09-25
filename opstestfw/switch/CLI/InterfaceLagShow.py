##########################################################################################
# Name:        opstestfw.switch.CLI.LAG.InterfaceShow
#
# Namespace:   opstestfw.switch.CLI.LAG
#
# Author:      Randall Loaiza
#
# Purpose:     Library function to configure LAG parameters on an interface
#
# Params:      deviceObj - device object.
#              interface - interface to config   
#
# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data: {"localPort":{"lagId","systemId","portId","key","activeFlag","shortTimeFlag","collectingFlag","stateExpiredFlag","passiveFlag",
#                                  "longTimeOutFlag","distributingFlag","aggregableFlag","inSyncFlag","neighborStateFlag","individualFlag","outSyncFlag"},
#                     "remotePort":{"lagId","systemId","portId","key","activeFlag","shortTimeFlag","collectingFlag","stateExpiredFlag","passiveFlag",
#                                   "longTimeOutFlag","distributingFlag","aggregableFlag","inSyncFlag","neighborStateFlag","individualFlag","outSyncFlag"}
#                    }
#
##PROC-###################################################################################

import opstestfw      
import pexpect  
import re       
import time     
import pdb

def InterfaceLagShow(** kwargs):   
    deviceObj = kwargs.get('deviceObj', None)
    interface = kwargs.get('interface', None)
    
    overallBuffer = []
    bufferString = ""
    data = dict()
    # If Device object is not passed, we need to error out
    if deviceObj is None:
        opstestfw.LogOutput('error', "Need to pass switch device object deviceObj to this routine")
        returnCls = opstestfw.returnStruct(returnCode=1)
        return returnCls

    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        opstestfw.LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = opstestfw.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    ###########################################################################
    #Send Command
    ###########################################################################
    command = "show lacp interface"
    if interface != None:
        command += " " + str(interface)
    opstestfw.LogOutput('info', "Show lacp interface.*****"+ command)    
    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    temporaryBuffer = returnDevInt['buffer']

    if retCode != 0:
        opstestfw.LogOutput('error', "Failed to get information ."+ command)
    

    ###########################################################################
    # Get out of the Shell
    ###########################################################################
    # Get out of vtyshell
    returnStructure = deviceObj.VtyshShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        opstestfw.LogOutput('error', "Failed to exit vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = opstestfw.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    ###########################################################################
    # End Return Command
    ###########################################################################

    ###########################################################################
    # Return The Dict responds
    ###########################################################################

    for curLine in overallBuffer:
        bufferString += str(curLine)
    bufferSplit  = bufferString.split("\r\n")

    data['localPort'] =  []
    data['remotePort'] = []
    localPort = dict()
    remotePort = dict()
    
    for curLine in bufferSplit:
        # Search System id



        lagIdLine = re.match("Aggregate-name\s* :\s*lag(\w*)",curLine)
        if lagIdLine:
            curLocalLagId = lagIdLine.group(1)
            curRemoteLagId = lagIdLine.group(1)
            localPort['lagId'] = curLocalLagId
            remotePort['lagId'] = curRemoteLagId

        systemIdLine = re.match("System-id\s*\|(.*)\|(.*)", curLine)
        if systemIdLine:
            curLocalSystemId = systemIdLine.group(1)
            curRemoteSystemId = systemIdLine.group(2)
            localPort['systemId'] = curLocalSystemId
            remotePort['systemId'] = curRemoteSystemId

        portIdLine = re.match("Port-id\s*\|(.*)\|(.*)", curLine)
        if portIdLine:
            curLocalPort = portIdLine.group(1)
            curRemotePort = portIdLine.group(1)
            localPort['portId'] = curLocalPort
            remotePort['portId'] = curRemotePort

        keyLine = re.match("Key\s*\|(.*)\|(.*)", curLine)
        if keyLine:
            curLocalKey = keyLine.group(1)
            curRemoteKey = keyLine.group(2)
            localPort['key'] = curLocalKey
            remotePort['key'] = curRemoteKey

        stateLine = re.match("State\s*\|(.*)\|(.*)", curLine)
        if stateLine:
            #Catch from local
            activeFlag = re.match("A", stateLine.group(1))
            if activeFlag:
                localPort['activeFlag'] = True
            else:
                localPort['activeFlag'] = False
            
            shortTimeFlag = re.match("S", stateLine.group(1))
            if shortTimeFlag:
                localPort['shortTimeFlag'] = True
            else:
                localPort['shortTimeFlag'] = False
            
            collectingFlag = re.match("C", stateLine.group(1))
            if collectingFlag:
                localPort['collectingFlag'] = True
            else:
                localPort['collectingFlag'] = False
            
            stateExpiredFlag = re.match("X", stateLine.group(1))
            if stateExpiredFlag:
                localPort['stateExpiredFlag'] = True
            else:
                localPort['stateExpiredFlag'] = False
            
            passiveFlag = re.match("P", stateLine.group(1))
            if passiveFlag:
                localPort['passiveFlag'] = True
            else:
                localPort['passiveFlag'] = False  
            
            longTimeOutFlag = re.match("L", stateLine.group(1))
            if longTimeOutFlag:
                localPort['longTimeOutFlag'] = True
            else:
                localPort['longTimeOutFlag'] = False 
            
            distributingFlag = re.match("D", stateLine.group(1))
            if distributingFlag:
                localPort['distributingFlag'] = True
            else:
                localPort['distributingFlag'] = False 
            
            aggregableFlag = re.match("F", stateLine.group(1))
            if aggregableFlag:
                localPort['aggregableFlag'] = True
            else:
                localPort['aggregableFlag'] = False 
            
            inSyncFlag = re.match("N", stateLine.group(1))
            if inSyncFlag:
                localPort['inSyncFlag'] = True
            else:
                localPort['inSyncFlag'] = False
            
            neighborStateFlag = re.match("E", stateLine.group(1))
            if neighborStateFlag:
                localPort['neighborStateFlag'] = True
            else:
                localPort['neighborStateFlag'] = False

            
            individualFlag = re.match("I", stateLine.group(1))
            if individualFlag:
                localPort['individualFlag'] = True
            else:
                localPort['individualFlag'] = False
            
            outSyncFlag = re.match("O", stateLine.group(1))
            if outSyncFlag:
                localPort['outSyncFlag'] = True
            else:
                localPort['outSyncFlag'] = False

            #Cath from remote  *****************************************************

            activeFlag = re.match("A", stateLine.group(1))
            if activeFlag:
                remotePort['activeFlag'] = True
            else:
                remotePort['activeFlag'] = False
            
            shortTimeFlag = re.match("S", stateLine.group(1))
            if shortTimeFlag:
                remotePort['shortTimeFlag'] = True
            else:
                remotePort['shortTimeFlag'] = False
            
            collectingFlag = re.match("C", stateLine.group(1))
            if collectingFlag:
                remotePort['collectingFlag'] = True
            else:
                remotePort['collectingFlag'] = False
            
            stateExpiredFlag = re.match("X", stateLine.group(1))
            if stateExpiredFlag:
                remotePort['stateExpiredFlag'] = True
            else:
                remotePort['stateExpiredFlag'] = False
            
            passiveFlag = re.match("P", stateLine.group(1))
            if passiveFlag:
                remotePort['passiveFlag'] = True
            else:
                remotePort['passiveFlag'] = False  
            
            longTimeOutFlag = re.match("L", stateLine.group(1))
            if longTimeOutFlag:
                remotePort['longTimeOutFlag'] = True
            else:
                remotePort['longTimeOutFlag'] = False 
            
            distributingFlag = re.match("D", stateLine.group(1))
            if distributingFlag:
                remotePort['distributingFlag'] = True
            else:
                remotePort['distributingFlag'] = False 
            
            aggregableFlag = re.match("F", stateLine.group(1))
            if aggregableFlag:
                remotePort['aggregableFlag'] = True
            else:
                remotePort['aggregableFlag'] = False 
            
            inSyncFlag = re.match("N", stateLine.group(1))
            if inSyncFlag:
                remotePort['inSyncFlag'] = True
            else:
                remotePort['inSyncFlag'] = False
            
            neighborStateFlag = re.match("E", stateLine.group(1))
            if neighborStateFlag:
                remotePort['neighborStateFlag'] = True
            else:
                remotePort['neighborStateFlag'] = False

            
            individualFlag = re.match("I", stateLine.group(1))
            if individualFlag:
                remotePort['individualFlag'] = True
            else:
                remotePort['individualFlag'] = False
            
            outSyncFlag = re.match("O", stateLine.group(1))
            if outSyncFlag:
                remotePort['outSyncFlag'] = True
            else:
                remotePort['outSyncFlag'] = False

        data['localPort'] =  localPort
        data['remotePort'] = remotePort

            
    #Return results
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = opstestfw.returnStruct(returnCode=0, buffer=overallBuffer, data=data)
    return returnCls