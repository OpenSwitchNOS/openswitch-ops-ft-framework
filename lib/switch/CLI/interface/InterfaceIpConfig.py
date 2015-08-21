##########################################################################################
# Name:        switch.CLI.interface.InterfaceIpConfig
#
# Namespace:   switch.CLI.interface
#
# Author:      Vince Mendoza
#
# Purpose:     Library function configure IPv4 address on an interface
#
# Params:      deviceObj - device object
#              interface - interface number context
#              ipv6flag - default is False (ipv4 default).  set True for IPv6 
#              addr  - address string for Ipv4 address
#              mask - subnet mask bits
#              config - True to configure, False to unconfigure
#              secondary - True for secondary address, False for not

# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data: 
#
##PROC-###################################################################################
import common
import lib
import re
import time

def InterfaceIpConfig(**kwargs):
    deviceObj = kwargs.get('deviceObj', None)
    interface = kwargs.get('interface', None)
    ipv6flag = kwargs.get('ipv6flag', False)
    addr = kwargs.get('addr', None)
    mask = kwargs.get('mask', None)
    secondary = kwargs.get('secondary', False)
    config = kwargs.get('config', True)
    
    
    # If Device object is not passed, we need to error out
    if deviceObj is None or interface is None:
        common.LogOutput('error', "Need to pass switch device object deviceObj and interface to this routine")
        returnJson = common.ReturnJSONCreate(returnCode=1)
        return returnJson
    # Make sure type is ipv4 or ipv6
    
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
    if addr is not None and mask is not None:
        command = ""
        if config is False:
            command += "no "
        if ipv6flag is False:
            command += "ip "
        else:
            command += "ipv6 "
        
        command += "address "+ str(addr) + "/" + str(mask)
        if secondary is True:
            command += " secondary"
        command += "\r"
        returnStructure = deviceObj.DeviceInteract(command=command)
        retCode = returnStructure['returnCode']
        if retCode != 0:
            common.LogOutput('error', "Failed to configure address command "+ command + " on interface " + str(interface))
        else:
            common.LogOutput('debug', "Configured address command " + command + " on interface " + str(interface))
    
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

