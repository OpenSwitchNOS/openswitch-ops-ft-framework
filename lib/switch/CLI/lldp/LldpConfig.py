##########################################################################################
# Name:        switch.CLI.lldp.lldpEnable
#
# Namespace:   switch.CLI.lldp
#
# Author:      Vince Mendoza
#
# Purpose:     Library function to enable / disable lldp
#
# Params:      deviceObj - device object
#              enable    - flag to enable True / Faluse
#
# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data: 
#
##PROC-###################################################################################
import common
import lib
import re
import time

def LldpConfig(**kwargs):
    deviceObj = kwargs.get('deviceObj', None)
    enable = kwargs.get('enable', True)
    
    # If Device object is not passed, we need to error out
    if deviceObj is None:
        common.LogOutput('error', "Need to pass switch device object deviceObj")
        returnJson = common.ReturnJSONCreate(returnCode=1)
        return returnJson
    
    #if enable is False and disable is False:
    #    common.LogOutput('error', "Need to pass either enable=True to enable lldp or disable=True to disable lldp")
    #    returnJson = common.ReturnJSONCreate(returnCode=1)
    #    return returnJson
    
    #if enable is True and disable is True:
    #    common.LogOutput('error', "Need to pass either enable=True to enable lldp or disable=True to disable lldp")
    #    returnJson = common.ReturnJSONCreate(returnCode=1)
    #    return returnJson
    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell()
    vtyshInfo = common.ReturnJSONGetData(json=returnStructure, dataElement='vtyshPrompt')
    returnCode = common.ReturnJSONGetCode(json = returnStructure)
    if returnCode != 0:
        common.LogOutput('error', "Failed to get vtysh prompt")
        returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=returnStructure)
        return returnJson
    
    # Get into config context
    returnStructure = deviceObj.ConfigVtyShell(enter=True)
    returnCode = common.ReturnJSONGetCode(json = returnStructure)
    if returnCode != 0:
        common.LogOutput('error', "Failed to get vtysh config prompt")
        returnJson = common.ReturnJSONCreate(returnCode=returnCode)
        return returnJson
    
    if enable is True:
        command = "feature lldp\r"
        returnStructure = deviceObj.DeviceInteract(command=command)
        retCode = returnStructure['returnCode']
        if retCode != 0:
            common.LogOutput('error', "Failed to enable lldp on device " + deviceObj.device)
        else:
            common.LogOutput('debug', "Enabled lldp on device " + deviceObj.device)
    else:
        command = "no feature lldp\r"
        returnStructure = deviceObj.DeviceInteract(command=command)
        retCode = returnStructure['returnCode']
        if retCode != 0:
            common.LogOutput('error', "Failed to disable lldp on device " + deviceObj.device)
        else:
            common.LogOutput('debug', "Disabled lldp on device " + deviceObj.device)
    
    # Get out of  config context
    returnStructure = deviceObj.ConfigVtyShell(enter=False)
    returnCode = common.ReturnJSONGetCode(json = returnStructure)
    if returnCode != 0:
        common.LogOutput('error', "Failed to get out of vtysh config context")
        returnJson = common.ReturnJSONCreate(returnCode=1)
        return returnJson
    
    # Get out of vtyshell
    returnStructure = deviceObj.VtyshShell(enter=False)
    retCode = common.ReturnJSONGetCode(json=returnStructure)
    if retCode != 0:
        common.LogOutput('error', "Failed to exit vty shell")
        returnJson = common.ReturnJSONCreate(returnCode=1)
        return returnJson

    returnJson = common.ReturnJSONCreate(returnCode=0)
    return returnJson

