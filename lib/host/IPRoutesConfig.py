###PROC+#####################################################################
# Name:        host.IPRoutesConfig
#
# Namespace:   host
#
# Author:      Srinivasa Krishnappa
#
# Purpose:     Library to configure ip routes on a  host
#
# Params:      connection - pexpect host connection handle
#              routeOperation     - add or delete
#              destNetwork        - destination IP network
#              netMask            - netmask
#              via                - via local link if any optional
#              eth                - device or interface
#              metric             - route metric
#              ipv6Flag   - ipv6 flag option if True else ipv4 and is by default
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
import pprint

PASSED = 0
FAILED = 1


def IPRoutesConfig(**kwargs):

    connection = kwargs.get('connection')
    routeOperation = kwargs.get('routeOperation')
    destNetwork = kwargs.get('destNetwork')
    netMask = kwargs.get('netMask')
    via = kwargs.get('via')
    eth = kwargs.get('eth', 'eth1')
    metric = kwargs.get('metric', 1024)
    ipv6Flag = kwargs.get('ipv6Flag', False)

    defaultRoute = 0

    retStruct = dict()
    retStruct['returnCode'] = 1
    retStruct['buffer'] = []

   # Local variables

    returnCode = PASSED

    if routeOperation != 'add' and routeOperation != 'delete':
        retStruct['buffer'] = 'Invalid routeOperation : %s' \
            % routeOperation
        returnCode = FAILED

    if ipv6Flag:
        try:
            socket.inet_pton(socket.AF_INET6, destNetwork)
            if destNetwork == '::':
                defaultRoute = 1
                route_command = \
                    'ip -6 route %s %s via %s dev %s metric %d' \
                    % (routeOperation, 'default', via, eth, metric)
            else:
                route_command = \
                    'ip -6 route %s %s/%d via %s dev %s metric %d' % (
                    routeOperation,
                    destNetwork,
                    netMask,
                    via,
                    eth,
                    metric,
                    )
        except socket.error:
            retStruct['buffer'] = 'Invalid destination : %s' \
                % destNetwork
            returnCode = FAILED
    else:
        try:
            socket.inet_pton(socket.AF_INET, destNetwork)
            if destNetwork == '0.0.0.0':
                defaultRoute = 1
                route_command = 'route %s %s gw %s dev %s metric %d' \
                    % (routeOperation, 'default', via, eth, metric)
            else:
                route_command = 'route %s -net %s/%d gw %s metric %d' \
                    % (routeOperation, destNetwork, netMask, via,
                       metric)
        except socket.error:
            retStruct['buffer'] = 'Invalid destination : %s' \
                % destNetwork
            returnCode = FAILED

    if returnCode == PASSED:

      # Send the command

        returnStruct = host.DeviceInteract(connection=connection,
                command=route_command)
        retCode = returnStruct.get('returnCode')
        retBuff = returnStruct.get('buffer')
        if retCode != 0:
            common.LogOutput('error', 'Failed to execute the command : '
                              + route_command)
            returnCode = FAILED
        else:
            common.LogOutput('info',
                             'Successfully executed the command : '
                             + route_command)
            retStruct['buffer'] = retBuff
    else:
        retStruct['buffer'] = 'Invalid ip address'

    retStruct['returnCode'] = returnCode
    return retStruct


def GetDirectLocalLinkAddresses(**kwargs):

    connection = kwargs.get('connection')
    localLinkDict = dict()
    localLinkElements = []
    command = 'ip -6 neighbour show'

   # Send the command

    returnStruct = host.DeviceInteract(connection=connection,
            command=command)
    retCode = returnStruct.get('returnCode')
    retBuff = returnStruct.get('buffer')
    if retCode != 0:
        common.LogOutput('error', 'Failed to execute the command : '
                         + command)
    retBuff = retBuff.split('\n')
    for output in retBuff:
        if re.search('^fe80', output):
            localLinkDict['address'] = output.split(' ')[0]
            localLinkDict['eth'] = output.split(' ')[2]
            localLinkElements.append(localLinkDict.copy())
    return localLinkElements
