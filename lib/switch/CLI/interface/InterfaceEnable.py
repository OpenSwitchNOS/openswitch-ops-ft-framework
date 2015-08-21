##########################################################################################
# Name:        switch.CLI.interface.InterfaceEnable
#
# Namespace:   switch.CLI.interface
#
# Author:      Vince Mendoza
#
# Purpose:     Library function enable / disable interface
#
# Params:      deviceObj - device object
#              interface - interface number context
#              enable    - True to Enable, False to disable
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

def InterfaceEnable(**kwargs):
    deviceObj = kwargs.get('deviceObj', None)
    interface = kwargs.get('interface', None)
    enable = kwargs.get('enable', True)
    
    # If Device object is not passed, we need to error out
    if deviceObj is None or interface is None:
        common.LogOutput('error', "Need to pass switch device object deviceObj and interface to this routine")
        returnJson = common.ReturnJSONCreate(returnCode=1)
        return returnJson
    
    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell(enter=True)
    returnCode = common.ReturnJSONGetCode(json = returnStructure)
    if returnCode != 0:
        common.LogOutput('error', "Failed to get vtysh prompt")
        returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=returnStructure)
        return returnJson

    # Get into config context
    returnStructure = deviceObj.ConfigVtyShell(enter=True)
    returnCode = common.ReturnJSONGetCode(json=returnStructure)
    if returnCode != 0:
        common.LogOutput('error', "Failed to get vtysh config prompt")
        returnJson = common.ReturnJSONCreate(returnCode=1)
        return returnJson
    
    # Get into the interface context
    command = "interface " + str(interface)
    returnStructure = deviceObj.DeviceInteract(command=command)
    retCode = returnStructure['returnCode']
    if retCode != 0:
        common.LogOutput('error', "Failed to enter interface context for interface " + str(interface))
        returnJson = common.ReturnJSONCreate(returnCode=1)
        return returnJson

    # Need to get into the Interface context
    if enable is True:
        command = "no shutdown\r"
        returnStructure = deviceObj.DeviceInteract(command=command)
        retCode = returnStructure['returnCode']
        if retCode != 0:
            common.LogOutput('error', "Failed to enable interface " + str(interface))
        else:
            common.LogOutput('debug', "Enabled interface " + str(interface))
    else:
        command = "shutdown\r"
        returnStructure = deviceObj.DeviceInteract(command=command)
        retCode = returnStructure['returnCode']
        if retCode != 0:
            common.LogOutput('error', "Failed to disable interface " + str(interface))
        else:
            common.LogOutput('debug', "Disabled interface " + str(interface))
    
    # Get out of the interface context
    command = "exit \r"
    returnStructure = deviceObj.DeviceInteract(command=command)
    retCode = returnStructure['returnCode']
    if retCode != 0:
        common.LogOutput('error', "Failed to exit the interface context")
        
    
    # Get into config context
    returnStructure = deviceObj.ConfigVtyShell(enter=False)
    returnCode = common.ReturnJSONGetCode(json = returnStructure)
    if returnCode != 0:
        common.LogOutput('error', "Failed to exit vtysh config prompt")
        returnJson = common.ReturnJSONCreate(returnCode=returnCode)
        return returnJson
    
    # Get out of vtyshell
    returnStructure = deviceObj.VtyshShell(enter=False)
    returnCode = common.ReturnJSONGetCode(json = returnStructure)
    if returnCode != 0:
        common.LogOutput('error', "Failed to exit vtysh prompt")
        returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=returnStructure)
        return returnJson

    #Return results
    returnJson = common.ReturnJSONCreate(returnCode=0)
    return returnJson

