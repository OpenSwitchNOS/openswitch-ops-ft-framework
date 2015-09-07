#########################################################################################
# Name:        switch.CLI.lag.lacpAggregatesShow
#
# Namespace:   switch.CLI.lag
#
# Author:      Jose Pablo Hernandez 
#
# Purpose:     Library function to display settings configured on 1 or several LAGs
#
# Params:         deviceObj - Switch identifier
#                 lagId - LAG identifier
#
# Returns:     JSON structure
#                   returnCode :- status of command(0 for pass , 1 for incorrect LAG ID, 2 for unexpected EOF or timeout while reading output from switch, 3 switch does not recognize command)
#                   data: -            Dictionary as per manipulated expect data
#                                         Keys: LAG numeric identifier
#                                         Values:
#                                             interfaces: - List of interfaces part of LAG
#                                             lacpFastFlag: - True for fast heartbeat, False for slow heartbeat
#                                             fallbackFlag: - True when enabled, False otherwise
#                                             hashType: - l2-src-dst/l3-src-dst depending on configured settings on LAG
#                                             mode: - LAG configured mode: off for static and active/passive for dynamic
#                   buffer: -      CLI output encountered by the function while executing for debugging purposes
#
##PROC-###################################################################################

import lib
import pexpect
import re
import time

def lacpAggregatesShow(** kwargs):
    #Params
    lagId = kwargs.get('lagId', None)
    deviceObj = kwargs.get('deviceObj', None)
    
    #Variables
    overallBuffer = []
    retStruct = dict()
    index = 0
    helperLagId = ''
    finalReturnCode = 0
    
    #If device is not passed, we need error message
    if deviceObj is None:
        lib.LogOutput('error', "Need to pass device to configure")
        returnJson = lib.returnStruct(returnCode=1)
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
    
    #Create command to query switch
    command = 'show lacp aggregates'
    if lagId is not None:
        command += ' lag' + str(lagId)
    deviceObj.expectHndl.sendline(command)
    
    #Parse information incoming from switch according to predetermined format
    while True:
        index = deviceObj.expectHndl.expect(['Aggregate-name[ ]+: lag([0-9])+','Aggregated-interfaces[ ]+:[ ]?([ ][a-zA-Z0-9 \-]*)\r',
                                      'Heartbeat rate[ ]+: (slow|fast)\r','Fallback[ ]+: (true|false)\r',
                                      'Hash[ ]+: (l2-src-dst|l3-src-dst)\r','Aggregate mode[ ]+: (off|passive|active)\r',
                                      "Specified LAG port doesn[']t exist[.]\r",'% Unknown command.\r',pexpect.TIMEOUT,pexpect.EOF],timeout=20)
        overallBuffer.append(deviceObj.expectHndl.before)
        overallBuffer.append(deviceObj.expectHndl.after)
        if index == 0:
            #LAG id match
            helperLagId = str(deviceObj.expectHndl.match.group(1))
            retStruct[helperLagId] = dict()
        elif index == 1:
            #Match for interfaces
            retStruct[helperLagId]['interfaces'] = []
            for i in re.split(' ', deviceObj.expectHndl.match.group(1)):
                if i != '':
                    retStruct[helperLagId]['interfaces'].append(i)
        elif index == 2:
            #Match for Heartbeat speed
            if deviceObj.expectHndl.match.group(1) == 'fast':
                retStruct[helperLagId]['lacpFastFlag'] = True
            else:
                retStruct[helperLagId]['lacpFastFlag'] = False
        elif index == 3:
            #Match for fallback settings
            if deviceObj.expectHndl.match.group(1) == 'true':
                retStruct[helperLagId]['fallbackFlag'] = True
            else:
                retStruct[helperLagId]['fallbackFlag'] = False
        elif index == 4:
            #Match for Hashing algorithm
            retStruct[helperLagId]['hashType'] = deviceObj.expectHndl.match.group(1)
        elif index == 5:
            #Match for LAG mode
            retStruct[helperLagId]['mode'] = deviceObj.expectHndl.match.group(1)
        elif index == 6:
            #Match for when the LAG interface doesn't exist
            finalReturnCode = 1
        elif index == 7:
            #Match when CLI does not recognize command
            finalReturnCode = 3
        elif index == 8:
            #Verify if the command output has ended
            try:
                deviceObj.expectHndl.expect('# ',timeout=1)
                overallBuffer.append(deviceObj.expectHndl.before)
                overallBuffer.append(deviceObj.expectHndl.after)
                break
            except pexpect.TIMEOUT:
                overallBuffer.append(deviceObj.expectHndl.before)
                overallBuffer.append(deviceObj.expectHndl.after)
                bufferString = ""
                for curLin in overallBuffer:
                    bufferString += str(curLin)
                returnCls = lib.returnStruct(returnCode=2, buffer=bufferString, data=retStruct)
                return returnCls
        else:
            #Match other scenarios including EOF
            overallBuffer.append(deviceObj.expectHndl.before)
            overallBuffer.append(deviceObj.expectHndl.after)
            bufferString = ""
            for curLin in overallBuffer:
                bufferString += str(curLin)
            returnCls = lib.returnStruct(returnCode=2, buffer=bufferString, data=retStruct)
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
        returnCls = lib.returnStruct(returnCode=2, buffer=bufferString)
        return returnCls
    
    #Compile information to return
    bufferString = ""
    for curLin in overallBuffer:
        bufferString += str(curLin)
    returnCls = lib.returnStruct(returnCode=finalReturnCode, buffer=bufferString, data=retStruct)
    return returnCls
    