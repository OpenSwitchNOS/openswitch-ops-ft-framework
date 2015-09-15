##########################################################################################
# Name:        	opstestfw.switch.cli.lag.lagpGlobalSystemShow
#
# Namespace:	opstestfw.switch.cli.lag
#
# Author:      	Pablo Araya M.
#
# Purpose:     	Function to extract Global LACP configuration
#
# Params:      	deviceObj         -    device object
#
# Returns:     	Dictionary with the following
#              	returnCode 	- 	0 for pass, 1 for fail
#              	buffer 		-   buffer of command
#              	data 		-   dictionary with the following keys/values
#              		System-id = <int>
#                   System-priority = <int> [0-65534]
#
##PROC-###################################################################################

import pexpect
from opstestfw import gbldata
import opstestfw.switch
import time
import re
import opstestfw


def lagpGlobalSystemShow(**kwargs):
        
    # Params
    deviceObj = kwargs.get('deviceObj', None)
      
    # Variables
    overallBuffer = []
    data = dict()
    bufferString = ""
    command = ""
        
    # Dictionary initialization
    data['System-id'] = 0
    data['System-priority'] = 0
        
    # If Device object is not passed, we need to error out
    if deviceObj is None:
        opstestfw.LogOutput('error', "Need to pass switch deviceObj to this routine")
        returnCls = opstestfw.returnStruct(returnCode=1)
        return returnCls
        
    # Get into vtysh
    returnStructure = deviceObj.VtyshShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        opstestfw.LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = opstestfw.returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls
        
    # Show command
    command += ("show lacp configuration")
    returnStructure = deviceObj.DeviceInteract(command=command)
    retCode = returnStructure['returnCode']
    overallBuffer.append(returnStructure['buffer'])
    if retCode != 0:
        opstestfw.LogOutput('error', "Failed to execute LACP configuration show")
    else:
        opstestfw.LogOutput('debug', "LACP configuration show succeeded")
        
    # Get out of vtyshell
    returnStructure = deviceObj.VtyshShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        opstestfw.LogOutput('error', "Failed to exit enable prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = opstestfw.retStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls
    
    #Return results
    for curLine in overallBuffer:
        bufferString += str(curLine)
            
    # Fill dictionary out
    for curLine in bufferString.split('\r\n'):
        print curLine
        showLine1 = re.match(r'System-id \s*:\s*(\d+)', curLine)
        if showLine1:
            data['System-id'] = int(showLine1.group(1))
            continue
                
        showLine2 = re.match(r'System-priority \s*:\s*(\d+)', curLine)
        if showLine2:
            data['System-priority'] = int(showLine2.group(1))
            continue
            
        
    returnCls = opstestfw.returnStruct(returnCode=0, buffer=bufferString, data=data)
    return returnCls