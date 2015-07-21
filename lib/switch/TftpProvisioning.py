###PROC+#####################################################################
# Name:        switch.
#
# Namespace:   switch
#
# Author:
#
# Purpose:
#
# Params:      connection - expect connection handle
#
#
# Returns:     Dictionary with the following
#              returnCode = 0 for pass, 1 for fail
#              buffer - buffer of command
#
##PROC-#####################################################################

import pexpect
import headers
import common
import time
import switch
import pdb

def TftpProvisioning(**kwargs):
     returnDict = dict()
     common.LogOutput("info","PROVISIONING HALON Physical device")
     common.LogOutput("info","Enter the Onie rescue mode for provisioning the physical device")
     connection = kwargs.get('connection')
     if headers.TftpImage['Image'] is None :
       common.LogOutput("error","TFTP image not specified **Exiting the provisioning module")
       returnJson = common.ReturnJSONCreate(returnCode=0, data=None)
       return returnJson
     connection = switch.Reboot(connection=connection,onie=True,onieMode="rescue")
     #TFTP configurations in Onie Rescue
     command = "tftp -g -r %s 120.93.49.9"%(headers.TftpImage['Image'])
     common.LogOutput("info","TFTP download ***")

     #Get the device response buffer as json return structure here
     devIntRetStruct = switch.DeviceInteract(connection=connection, command=command)
     returnCode = devIntRetStruct.get('returnCode')
     returnDict['onieRescue'] = devIntRetStruct.get('buffer')
     pdb.set_trace()
     if returnCode != 0:
      common.LogOutput('error', "Failed to get TFTP image")
      returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=returnDict)
      return returnJson

     #Return results
     returnJson = common.ReturnJSONCreate(returnCode=0, data=returnDict)
     return returnJson


