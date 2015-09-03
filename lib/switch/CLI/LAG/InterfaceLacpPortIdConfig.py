##########################################################################################
# Name:        switch.CLI.LAG.InterfaceLacpPortIdConfig
#
# Namespace:   switch.CLI.LAG
#
# Author:      Randall Loaiza
#
# Purpose:     Library function to configure LAG parameters on an interface
#
# Params:      deviceObj - device object.
#              interface - interface to config   
#              lacpPortId - Range between 1 and 65535 to identify port in LACP
#              enable - True for configuration/false for removing LAG  
#
# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data:  {}
#
##PROC-###################################################################################

from lib import *
import re
import time

def InterfaceLacpPortIdConfig(**kwargs):

    deviceObj = kwargs.get('deviceObj', None)
    interface = kwargs.get('interface', None)
    lagId = kwargs.get('lagId', 1)
    lacpPortId = kwargs.get('lacpPortId', 1)
    lacpPortPriority = kwargs.get('lacpPortPriority', 1)
    lacpAggKey = kwargs.get('lacpAggKey', 1)
    enable  = kwargs.get('enable', None)





    ##############################################################################################
    # Assign a port-ID for lacp
    ##############################################################################################

    #if enable is True: Removing this part, because no matter if disable or enable always has to set the value
    command = "lacp port-id "+ lacpPortId +"\r"
    returnDict = deviceObj.DeviceInteract(command=command)
    retCode = returnDict['returnCode']
    overallBuffer.append(returnDict['buffer'])
    if retCode != 0:
        lib.LogOutput('error', "Failed to configure the LACP port ID" + str(interface))
    else:
        lib.LogOutput('debug', "LACP port ID assigned" + str(interface))
