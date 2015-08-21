##########################################################################################
# Name:        switch.CLI.lldp.LldpInterfaceConfig
#
# Namespace:   switch.CLI.lldp
#
# Author:      Vince Mendoza
#
# Purpose:     Library function configure lldp interface context settings
#
# Params:      deviceObj - device object
#              interface - interface number context
#              transmission - True turns on transmission / False turns off transmission
#              reception - True turns on transmission / False turns off transmission
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

def LldpInterfaceConfig(**kwargs):
    deviceObj = kwargs.get('deviceObj', None)
    interface = kwargs.get('interface', None)
    transmission = kwargs.get('transmission', None)
    reception = kwargs.get('reception', None)
    
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
    if transmission is True:
        command = "lldp transmission\r"
        returnStructure = deviceObj.DeviceInteract(command=command)
        retCode = returnStructure['returnCode']
        if retCode != 0:
            common.LogOutput('error', "Failed to enable lldp tranmission on interface " + str(interface))
        else:
            common.LogOutput('debug', "Enabled lldp transmission on interface " + str(interface))

    if transmission is False:
        command = "no lldp transmission\r"
        returnStructure = deviceObj.DeviceInteract(command=command)
        retCode = returnStructure['returnCode']
        if retCode != 0:
            common.LogOutput('error', "Failed to disable lldp transmission on interface " + str(interface))
        else:
            common.LogOutput('debug', "Disabled lldp transmission on interface " + str(interface))
    
    if reception is True:
        command = "lldp reception\r"
        returnStructure = deviceObj.DeviceInteract(command=command)
        retCode = returnStructure['returnCode']
        if retCode != 0:
            common.LogOutput('error', "Failed to enable lldp reception on interface  " + str(interface))
        else:
            common.LogOutput('debug', "Enabled lldp reception on interface " + str(interface))
    
    if reception is False:
        command = "no lldp reception\r"
        returnStructure = deviceObj.DeviceInteract(command=command)
        retCode = returnStructure['returnCode']
        if retCode != 0:
            common.LogOutput('error', "Failed to disable lldp reception on interface  " + str(interface))
        else:
            common.LogOutput('debug', "Disabled lldp reception on interface " + str(interface))
    
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

