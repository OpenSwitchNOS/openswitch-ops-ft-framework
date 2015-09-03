##########################################################################################
# Name:        switch.CLI.LAG.InterfaceLacpAggKeyConfig
#
# Namespace:   switch.CLI.LAG
#
# Author:      Randall Loaiza
#
# Purpose:     Library function to configure LAG parameters on an interface
#
# Params:      deviceObj - device object.
#              interface - interface to config   
#              lacpAggKey - Range betwen 1 and 65535. Key used to identify all members of LAG to be of the same 2 switches. Will probably not be added in Basil
#              enable - True for configuration/false for removing LAG   
#
# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data: {}
#
##PROC-###################################################################################

from lib import *
import re
import time

def InterfaceLacpAggKeyConfig(**kwargs):

    deviceObj = kwargs.get('deviceObj', None)
    interface = kwargs.get('interface', None)
    lagId = kwargs.get('lagId', 1)
    lacpPortId = kwargs.get('lacpPortId', 1)
    lacpPortPriority = kwargs.get('lacpPortPriority', 1)
    lacpAggKey = kwargs.get('lacpAggKey', 1)
    enable  = kwargs.get('enable', None)


    ##############################################################################################
    # Assign a aggregation-key for lacp
    ##############################################################################################

    #if enable is True: Removing this part, because no matter if disable or enable always has to set the value
    command = "lacp aggregation-key "+ lacpAggKey +"\r"
    returnDict = deviceObj.DeviceInteract(command=command)
    retCode = returnDict['returnCode']
    overallBuffer.append(returnDict['buffer'])
    if retCode != 0:
        lib.LogOutput('error', "Failed to configure the aggregation-key to the interface" + str(interface))
    else:
        lib.LogOutput('debug', "Aggregation-key assigned" + str(interface))   

    ##############################################################################################
    # End Assign a aggregation-key for lacp
    ##############################################################################################