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
from lib import *
import re
import time

def InterfaceIpConfig(**kwargs):
    deviceObj = kwargs.get('deviceObj', None)
    interface = kwargs.get('interface', None)
    vlan = kwargs.get('vlan', None)
    lag = kwargs.get('lag', None)
    ipv6flag = kwargs.get('ipv6flag', False)
    addr = kwargs.get('addr', None)
    mask = kwargs.get('mask', None)
    secondary = kwargs.get('secondary', False)
    config = kwargs.get('config', True)
    
    overallBuffer = []
    # If Device object is not passed, we need to error out
    if deviceObj is None or interface is None:
        LogOutput('error', "Need to pass switch device object deviceObj and interface to this routine")
        returnCls = returnStruct(returnCode=1)
        return returnCls
    
    paramError = 0
    if interface is not None:
        if vlan is not None or lag is not None:
            paramError = 1
    if vlan is not None:
        if interface is not None or lag is not None:
            paramError = 1
    if lag is not None:
        if interface is not None or vlan is not None:
            paramError = 1
    if interface is None and vlan is None and lag is None:
        paramError = 1
    if paramError == 1:
        LogOutput('error', "Need to only pass interface, vlan or lag into this routine")
        returnCls = returnStruct(returnCode=1)
        return returnCls
    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls

    # Get into config context
    returnStructure = deviceObj.ConfigVtyShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to get vtysh config prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    
    # Get into the interface context
    if interface is not None:
        command = "interface " + str(interface)
    elif vlan is not None:
        command = "interface vlan" + str(vlan)
    elif lag is not None:
        command = "interface lag" + str(lag)
    returnStructure = deviceObj.DeviceInteract(command=command)
    retCode = returnStructure['returnCode']
    overallBuffer.append(returnStructure['buffer'])
    if retCode != 0:
        LogOutput('error', "Failed to enter interface context for interface " + str(interface))
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

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
        overallBuffer.append(returnStructure['buffer'])
        if retCode != 0:
            LogOutput('error', "Failed to configure address command "+ command + " on interface " + str(interface))
        else:
            LogOutput('debug', "Configured address command " + command + " on interface " + str(interface))
    
    # Get out of the interface context
    command = "exit \r"
    returnStructure = deviceObj.DeviceInteract(command=command)
    retCode = returnStructure['returnCode']
    overallBuffer.append(returnStructure['buffer'])
    if retCode != 0:
        LogOutput('error', "Failed to exit the interface context")
        
    
    # Get into config context
    returnStructure = deviceObj.ConfigVtyShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to exit vtysh config prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls
    
    # Get out of vtyshell
    returnStructure = deviceObj.VtyshShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to exit vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls

    #Return results
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = returnStruct(returnCode=0, buffer=bufferString)
    return returnCls

