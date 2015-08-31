##########################################################################################
# Name:        switch.CLI.interface.IpRouteConfig
#
# Namespace:   switch.CLI.interface
#
# Author:      Vince Mendoza
#
# Purpose:     Library function configure IPv4 or IPv6 address on an interface
#
# Params:      deviceObj - device object
#              route  - route address to configure
#              ipv6flag - True for IPv6, False is IPv4.  Default is False
#              mask - subnet mask bits
#              nexthop - Can be an ip address or a interface
#              config - True to configure, False to unconfigure
#              metric - Range between 1-255 for route metric

# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data: 
#
##PROC-###################################################################################

import lib
import re
import time

def IpRouteConfig(**kwargs):
    deviceObj = kwargs.get('deviceObj', None)
    ipv6flag = kwargs.get('ipv6flag', False)
    route = kwargs.get('route', None)
    mask = kwargs.get('mask', None)
    config = kwargs.get('config', True)
    nexthop = kwargs.get('nexthop', None)
    metric = kwargs.get('metric', None)
    
    overallBuffer = []
    # If Device object is not passed, we need to error out
    if deviceObj is None or route is None or mask is None or nexthop is None:
        common.LogOutput('error', "Need to pass switch device object deviceObj, route, mask, and nexthop to this routine")
        returnCls = lib.returnStruct(returnCode=1)
        return returnCls

    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        common.LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    # Get into config context
    returnStructure = deviceObj.ConfigVtyShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        common.LogOutput('error', "Failed to get vtysh config prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    
    # Build route command
    command = ""
    if config is False:
        command += "no "
    if ipv6flag is False:
        command += "ip "
    else:
        command += "ipv6 "
    command += "route "+ str(route) + "/" + str(mask) + " " + str(nexthop)
    
    if metric is not None:
        command += " " + str(metric)
        
    command += "\r"
    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        common.LogOutput('error', "Failed to configure route command "+ command)
    else:
        common.LogOutput('debug', "Configured route command " + command)
    
    # Get into config context
    returnStructure = deviceObj.ConfigVtyShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        common.LogOutput('error', "Failed to exit vtysh config prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls
    
    # Get out of vtyshell
    returnStructure = deviceObj.VtyshShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        common.LogOutput('error', "Failed to exit vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    #Return results
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = lib.returnStruct(returnCode=0, buffer=bufferString)
    return returnCls
    

