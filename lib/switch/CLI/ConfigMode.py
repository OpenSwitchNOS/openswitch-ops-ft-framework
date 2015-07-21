#####################################################################
# Name:        switch.CLI.ConfigMode
#
# Namespace:   switch.CLI
#
# Author:      Payal Upadhyaya
#
# Purpose:     Enter config mode command to run commands
#              Exits config mode if the configOption = unconfig
#
# Params:      connection - device connection
#              configOption - unconfig (to exit config mode)
#                           - default (config) enter config mode
#
# Returns:     JSON structure
#              returnCode - status of command
#                           (0 = pass , 1= fail)
#              data ::
#                     "configPrompt": {"Device Buffer"}
#
##PROC-#####################################################################
import common
import switch
import re
import pexpect

def ConfigMode (**kwargs):
    #Parameters
    connection = kwargs.get('connection')
    configOption = kwargs.get('configOption',"config")

    if connection is None:
       return False

    returnDict = dict()
    if configOption == "config":
     #Enter config mode when configOption is config(default)
     command = "config terminal\r"
     common.LogOutput("info","Enter config mode***")
     #Get the device response buffer as json return structure here
     devIntRetStruct = switch.DeviceInteract(connection=connection, command=command,CheckError = 'CLI')
     returnCode = devIntRetStruct.get('returnCode')
     returnDict['configPrompt'] = devIntRetStruct.get('buffer')
     if returnCode != 0:
        common.LogOutput('error', "Failed to enter the config mode ")
        returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=returnDict)
        return returnJson
    else :
     #Exit config mode
     common.LogOutput("debug","config shell Exit")
     command = "end\r"
     #Get the device response buffer as json return structure here
     devIntRetStruct = switch.DeviceInteract(connection=connection, command=command,CheckError = 'CLI')
     returnCode = devIntRetStruct.get('returnCode')
     returnDict['configPrompt'] = devIntRetStruct.get('buffer')
     if returnCode != 0:
        common.LogOutput('error', "Failed to exit the config mode")
        returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=returnDict)
        return returnJson
     returnJson = common.ReturnJSONCreate(returnCode=0, data=returnDict)
     return returnJson




