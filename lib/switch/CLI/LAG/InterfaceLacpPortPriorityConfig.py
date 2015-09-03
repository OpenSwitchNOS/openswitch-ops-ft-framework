##########################################################################################
# Name:        switch.CLI.LAG.InterfaceLacpPortPriorityConfig
#
# Namespace:   switch.CLI.LAG
#
# Author:      Randall Loaiza
#
# Purpose:     Library function to configure LAG parameters on an interface
#
# Params:      deviceObj - device object.
#              interface - interface to config   
#              lacpPortPriority - Range between 1 and 65535 to assign priority of interface between members of same dynamic LAG (LACP)
#
# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data:  {}
#
##PROC-###################################################################################

from lib import *
import re
import time

def InterfaceLacpPortPriorityConfig(**kwargs):
    
    deviceObj = kwargs.get('deviceObj', None)
    interface = kwargs.get('interface', None)
    lacpPortPriority = kwargs.get('lacpPortPriority', 1)


    ##############################################################################################
    # Assign a port-priority for lacp
    ##############################################################################################

    #if enable is True: Removing this part, because no matter if disable or enable always has to set the value
    command = "lacp port-priority "+ lacpPortPriority +"\r"
    returnDict = deviceObj.DeviceInteract(command=command)
    retCode = returnDict['returnCode']
    overallBuffer.append(returnDict['buffer'])
    if retCode != 0:
        lib.LogOutput('error', "Failed to configure the port-priority to the interface" + str(interface))
    else:
        lib.LogOutput('debug', "Port-priority assigned" + str(interface))       

    ##############################################################################################
    # End assign a port-priority for lacp
    ##############################################################################################