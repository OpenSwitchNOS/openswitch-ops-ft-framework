##PROC+#####################################################################
# Name:        host.DevicePing
#
# Namespace:   host
#
# Author:      Srinivasa Krishnappa
#
# Purpose:     Library to ping a destination from a  host
#
# Params:      connection - pexpect host connection handle
#              ipAddr     - ipAddr of the destination device
#              ipv6Flag   - ipv6 flag option if True else ipv4 and is by default
#              packetCount - Echo packets count is -c option of the ping/6 cmd
#              packetSize  - Echo packets size is -s option and 128 bytes default
# Returns:
#              returnCode = 0 for pass, 1 for fail
#
#
##PROC-#####################################################################

import headers
import common
import host
import re
import socket

PASSED = 0
FAILED = 1


def DevicePing(**kwargs):

    connection = kwargs.get('connection')
    ipAddr = kwargs.get('ipAddr')
    ipv6Flag = kwargs.get('ipv6Flag', False)
    packetCount = kwargs.get('packetCount', 10)
    packetSize = kwargs.get('packetSize', 128)
    eth = kwargs.get('eth', 'eth1')

    retStruct = dict()
    retStruct['returnCode'] = 1
    retStruct['buffer'] = []

   # Local variables

    returnCode = PASSED
    command = ''
    if ipv6Flag:
        try:
            socket.inet_pton(socket.AF_INET6, ipAddr)
            if ipAddr.find('fe80') == -1:
                command = 'ping6 %s -c %d -s %d' % (ipAddr,
                        packetCount, packetSize)
            else:
                command = 'ping6 -I %s %s -c %d -s %d' % (eth, ipAddr,
                        packetCount, packetSize)
        except socket.error:
            returnCode = FAILED
    else:
        try:
            socket.inet_pton(socket.AF_INET, ipAddr)
            command = 'ping %s -c %d -s %d' % (ipAddr, packetCount,
                    packetSize)
        except socket.error:
            returnCode = FAILED

    if returnCode == PASSED:

           # Send the command

        returnStruct = host.DeviceInteract(connection=connection,
                command=command)
        retCode = returnStruct.get('returnCode')
        retBuff = returnStruct.get('buffer')
        if retCode != 0:
            common.LogOutput('error', 'Failed to execute the command : '
                              + command)
        else:
            common.LogOutput('info',
                             'Successfully executed the command : '
                             + command)

        if retBuff.find('bytes from') == -1:
            returnCode = FAILED
        else:
            returnCode = PASSED

        retStruct['buffer'] = retBuff
    else:
        retStruct['buffer'] = 'Invalid ip address'

    retStruct['returnCode'] = returnCode
    return retStruct



			
