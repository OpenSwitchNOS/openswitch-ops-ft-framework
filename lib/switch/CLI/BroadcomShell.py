#####################################################################
# Name:        switch.CLI.BroadcomShell
#
# Namespace:   switch.CLI
#
# Author:      Srinivasa Krishnappa
#
# Purpose:     Enter broadcom shell to run CLI commands
#              Exits broadcom shell if the configOption = unconfig
#
# Params:      connection - device connection
#              configOption - unconfig (to exit broadcom shell)
#                           - default (config) enter broadcom shell
#                           - execute execute broadcom shell command
#              cmd          - broadcom command to be executed
#
# Returns:     JSON structure
#              returnCode - status of command
#                           (0 = pass , 1= fail)
#              data ::
#                     "drivshell>": {"buffer"}
#
##PROC-#####################################################################

import common
import switch
import re
import pexpect


def BroadcomShell(**kwargs):

    # Parameters

    connection = kwargs.get('connection')
    configOption = kwargs.get('configOption', 'config')
    cmd = kwargs.get('cmd')

    if connection is None:
        return False

    returnDict = dict()
    if configOption == 'config':

       # Enter broadcom shell when configOption is config

        command = 'ip netns exec swns telnet localhost 1943\r'
        common.LogOutput('info', 'Enter Broadcom Shell***')

       # Get the device response buffer as json return structure here

        devIntRetStruct = switch.DeviceInteract(connection=connection,
                command=command, CheckError='CLI')
        returnCode = devIntRetStruct.get('returnCode')
        returnDict['cmdPrompt'] = devIntRetStruct.get('buffer')
        if returnCode != 0:
            common.LogOutput('error',
                             'Failed to get into the broadcom shell')
    elif configOption == 'execute':

        common.LogOutput('info', 'Execute Broadcom Shell cmd :' + cmd)
        devIntRetStruct = switch.DeviceInteract(connection=connection,
                command=cmd, CheckError='CLI')
        returnCode = devIntRetStruct.get('returnCode')
        returnDict['cmdPrompt'] = devIntRetStruct.get('buffer')
        if returnCode != 0:
            common.LogOutput('error', 'Failed to execute the command : '
                              + cmd)
        else:
            common.LogOutput('info',
                             'Successfully executed the command : '
                             + cmd)
    elif configOption == 'unconfig':

       # Exit broadcom shell

        common.LogOutput('debug', 'Broadcom shell Exit')

       # ctrl a - z represented from ASCII numbers 1 - 26. and ctrl-d for exiting the shell.

        command = "\004\r"

       # Get the device response buffer as json return structure here

        devIntRetStruct = switch.DeviceInteract(connection=connection,
                command=command, CheckError='CLI')
        returnCode = devIntRetStruct.get('returnCode')
        returnDict['cmdPrompt'] = devIntRetStruct.get('buffer')
        if returnCode != 0:
            common.LogOutput('error',
                             'Failed to exit the broadcom shell')
    else:
        returnDict['cmdPrompt'] = 'Invalid config option passed :' \
            + configOption
        common.LogOutput('error', 'Invalid config option passed :'
                         + configOption)
        returnCode = FAILED
    returnJson = common.ReturnJSONCreate(returnCode=returnCode,
            data=returnDict)
    return returnJson
