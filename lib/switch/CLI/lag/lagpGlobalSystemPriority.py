########################################################################################
# Name:        switch.CLI.lag.lagpGlobalSystemPriority
#
# Namespace:   switch.CLI.lag
#
# Author:      Pablo Araya M.
#
# Purpose:     Function to configure Global LACP system Priority
#
# Params:      deviceObj         -    device object
#              systemPriority    -    Identification Default is system MAC address, can be changed for another one
#              configure         -    (Optional)    (Default is True)     True to configure, False to unconfigure
#
# Returns:     Dictionary with the following
#              returnCode -     0 for pass, 1 for fail
#              buffer -         buffer of command
#              data -           empty dictionary
#
##PROC-###################################################################################

import pexpect
from lib import gbldata
import switch
import time
import re
import lib


def lagpGlobalSystemPriority(**kwargs):
        
        
        # Params
        deviceObj = kwargs.get('deviceObj', None)
        systemPriority = kwargs.get('systemPriority', None)
        configure = kwargs.get('configure', True)
        
        # Variables
        overallBuffer = []
        data = dict()
        bufferString = ""
        command = ""
        
        # If Device object is not passed, we need to error out
        if deviceObj is None or systemPriority is None:
            lib.LogOutput('error', "Need to pass switch deviceObj and systemPriority to this routine")
            returnCls = lib.returnStruct(returnCode=1)
            return returnCls
        
        # Get into vtysh
        returnStructure = deviceObj.VtyshShell(enter=True)
        returnCode = returnStructure.returnCode()
        overallBuffer.append(returnStructure.buffer())
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
            returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
            return returnCls
    
        # Uconfigure system ID
        if configure is False:
            command = "no "
        
        # Normal configuration command
        command += ("lacp system-priority "+str(systemPriority))
        returnStructure = deviceObj.DeviceInteract(command=command)
        retCode = returnStructure['returnCode']
        overallBuffer.append(returnStructure['buffer'])
        if retCode != 0:
            lib.LogOutput('error', "Failed to configure LACP system priority: " + str(systemPriority))
        else:
            lib.LogOutput('debug', "LACP system priority configured: " + str(systemPriority))
        
    
        # Get out of config context
        returnStructure = deviceObj.ConfigVtyShell(enter=False)
        returnCode = returnStructure.returnCode()
        overallBuffer.append(returnStructure.buffer())
        if returnCode != 0:
            lib.LogOutput('error', "Failed to exit configure terminal prompt")
            bufferString = ""
            for curLine in overallBuffer:
                bufferString += str(curLine)
            returnCls = lib.retStruct(returnCode=returnCode, buffer=bufferString)
            return returnCls
        
        # Get out of vtyshell
        returnStructure = deviceObj.VtyshShell(enter=False)
        returnCode = returnStructure.returnCode()
        overallBuffer.append(returnStructure.buffer())
        if returnCode != 0:
            lib.LogOutput('error', "Failed to exit enable prompt")
            bufferString = ""
            for curLine in overallBuffer:
                bufferString += str(curLine)
            returnCls = lib.retStruct(returnCode=returnCode, buffer=bufferString)
            return returnCls
    
        #Return results
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=0, buffer=bufferString, data=data)
        return returnCls