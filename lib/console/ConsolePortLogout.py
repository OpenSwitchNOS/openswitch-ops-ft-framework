###PROC+#####################################################################
# Name:        console.ConsolePortLogout
#
# Namespace:   console
#
# Author:      Vince Mendoza
#
# Purpose:     Queries for port needed and logs out that port
#
# Params:      connection - device connection
#              tcpPort    - tcpPort
#
# Returns:     returnCode
#
##PROC-#####################################################################
import common
import console
import re

def ConsolePortLogout(**kwargs):
    connection = kwargs.get('connection')
    tcpPort = kwargs.get('port')

    if connection is None:
       return 1

    retStruct = dict()
    retStruct['returnCode'] = 0

    command = "show port async summary"

    devIntRetStruct = console.DeviceInteract(connection=connection, command=command)
    retCode = devIntRetStruct.get('returnCode')
    if retCode != 0:
       common.LogOutput('error', "Failed run " + command + " on console")
       retStruct['returnCode'] = 1
       return retStruct

    buffer = devIntRetStruct.get('buffer')
    physicalPort = 10000
    for curLine in buffer.split('\n'):
       # Match Line of output for show port async summary
       # Port       - group 1
       # Port Name  - group 2
       # Access
       # Speed      - group 3
       # TCP Port   - group 4
       # SSH Port   - group 5
       testForLine = re.match("^\s*([0-9a-f-]+)\s+(\S+)\s+Remote\s+(\d+)\s+(\d+)\s+(\d+)\s+\S+\s*$", curLine)
       if testForLine:
          # Check and see if our TCP / SSH port matches what we have passed in
          if tcpPort == testForLine.group(4) or tcpPort == testForLine.group(5):
             # This means we matched a port.  Save the port off to a variable
             physicalPort = testForLine.group(1)
             # We found our port, no need to go on...
             break


    # Now send in the command for killing the port
    if physicalPort == 10000:
       return 1
    common.LogOutput('debug', "Disconnecting console port " + str(physicalPort))
    command = "logout port async " + str(physicalPort)
    devIntRetStruct = console.DeviceInteract(connection=connection, command=command)
    retCode = devIntRetStruct.get('returnCode')
    if retCode != 0:
       common.LogOutput('error', "Failed to send command " + command)
       retStruct['returnCode'] = 1
       return retStruct

    return 0
