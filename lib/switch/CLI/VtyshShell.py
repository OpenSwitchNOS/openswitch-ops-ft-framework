#####################################################################
# Name:        switch.CLI.VtyshShell
#
# Namespace:   switch.CLI
#
# Author:      Payal Upadhyaya
#
# Purpose:     Enter vtysh shell to run CLI commands
#              Exits vtysh shell if the configOption = unconfig
#
# Params:      connection - device connection
#              configOption - unconfig (to exit vtysh shell)
#                           - default (config) enter vtysh shell
#
# Returns:     JSON structure
#              returnCode - status of command
#                           (0 = pass , 1= fail)
#              data ::
#                     "vtyshPrompt": {"buffer"}
#
##PROC-#####################################################################

import switch
import re
import pexpect

def VtyshShell (**kwargs):
    #Parameters
    connection = kwargs.get('connection')
    configOption = kwargs.get('configOption',"config")

    if connection is None:
       return False

    returnDict = dict()
    if configOption == "config":
     #Enter vtysh shell when configOption is config
     command = "vtysh\r"
     common.LogOutput("info","Enter vtysh Shell***")
     #Get the device response buffer as json return structure here
     devIntRetStruct = switch.DeviceInteract(connection=connection, command=command,CheckError = 'CLI')
     returnCode = devIntRetStruct.get('returnCode')
     returnDict['vtyshPrompt'] = devIntRetStruct.get('buffer')
     if returnCode != 0:
        common.LogOutput('error', "Failed to get into the vtysh shell")
        returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=returnDict)
        return returnJson

     #Enter paging command for  switch (terminal length)
     command = "terminal length 0\r"
     devIntRetStruct = switch.DeviceInteract(connection=connection, command=command)
     returnCode = devIntRetStruct.get('returnCode')
     if returnCode != 0:
        common.LogOutput('error', "Failed to get into the vtysh shell")
        returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=devIntRetStruct)
        return returnJson
     else :
        returnDict['vtyshPrompt'] += devIntRetStruct.get('buffer')

     returnJson = common.ReturnJSONCreate(returnCode=0, data=returnDict)
     return returnJson
    else :
     #Exit vtysh shell
     common.LogOutput("debug","Vtysh shell Exit")
     command = "exit\r"
     #Get the device response buffer as json return structure here
     devIntRetStruct = switch.DeviceInteract(connection=connection, command=command,CheckError = 'CLI')
     returnCode = devIntRetStruct.get('returnCode')
     returnDict['vtyshPrompt'] = devIntRetStruct.get('buffer')
     if returnCode != 0:
        common.LogOutput('error', "Failed to exit the vtysh shell")
        returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=returnDict)
        return returnJson
     returnJson = common.ReturnJSONCreate(returnCode=0, data=returnDict)
     return returnJson




