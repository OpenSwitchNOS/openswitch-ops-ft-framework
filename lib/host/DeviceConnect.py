###PROC+#####################################################################
# Name:        host.DeviceConnect
#
# Namespace:   host
#
# Author:      Srinivasa Krishnappa
#
# Purpose:     Connect to device under test from work station
#
#
# Params:      device - device name
#              hostConnHandle - host connection handle if we need connection
#                                from host - optional
#              mgmtIpAddress - management IP (non console IP) -
#              connType      - connType ssh or telnet - optional default ssh
# Returns:     connectHandle - Connection handle or None if no connection is made
#
##PROC-#####################################################################

import pexpect
import switch
import xml.etree.ElementTree
import os
import socket
import time
from lib import *


def DeviceConnect(device, **kwargs):

    hostConnHandle = kwargs.get('hostConnHandle', None)
    mgmtIpAddress = kwargs.get('mgmtIpAddress', None)
    connType = kwargs.get('connType', 'ssh')

    if mgmtIpAddress == None or hostConnHandle == None:
        LogOutput('debug', device
                         + ' Invalid device management IP address or host connection handle'
                         )
        return None

    # Look up and see if we are physical or virtual

    xpathString = './/reservation/id'
    rsvnEtreeElement = common.XmlGetElementsByTag(headers.TOPOLOGY,
            xpathString)
    if rsvnEtreeElement == None:

        # We are not in a good situation, we need to bail

        LogOutput('error',
                         'Could not find reservation id tag in topology'
                         )
        return None

    rsvnType = rsvnEtreeElement.text

    # Look up the device name in the topology - grab connectivity information

    xpathString = ".//device[name='" + device + "']"
    etreeElement = common.XmlGetElementsByTag(headers.TOPOLOGY,
            xpathString)
    if etreeElement == None:

       # We are not in a good situation, we need to bail

        LogOutput('error', 'Could not find device ' + device
                         + ' in topology')
        return None
    try:
        socket.inet_pton(socket.AF_INET, mgmtIpAddress)
        LogOutput('debug', device + ' connection IP address:  '
                         + mgmtIpAddress)
    except socket.error:
        LogOutput('debug', device
                         + ' Invalid connection IP address:  '
                         + mgmtIpAddress)
        return None
    port = '22'

    # Grab a connetion element - not testing this since this should exist since we obtained
    # things before us

    xpathString = ".//device[name='" + device + "']/connection"
    connectionElement = common.XmlGetElementsByTag(headers.TOPOLOGY,
            xpathString)

    # Grab a connetion element - not testing this since this should exist since we obtained
    # things before us

    xpathString = ".//device[name='" + device + "']/connection"
    connectionElement = common.XmlGetElementsByTag(headers.TOPOLOGY,
            xpathString)

    # Create Telnet handle
    # Enable expect device Logging for every connection
    # Single Log file exists for logging device exchange using pexpect logger .
    # Device logger  name format :: devicename_IP-Port

    cmdString = 'ssh ' + mgmtIpAddress

    LogOutput('debug', 'Opening an host connection to the device'
                     )

    hostConnHandle.sendline(cmdString)
    bailflag = 0
    connectionBuffer = []
    sanitizedBuffer = ''
    while bailflag == 0:
        time.sleep(1)
        index = \
            hostConnHandle.expect(['Are you sure you want to continue connecting (yes/no)?'
                                  , 'root@\S+\d+\d+.*#', pexpect.EOF,
                                  pexpect.TIMEOUT], timeout=200)

        # print "got index %d"%index

        hostConnHandle.expect(['$'], timeout=2)
        if index == 0:

            # Need to send login string

            hostConnHandle.sendline('yes')
            connectionBuffer.append(hostConnHandle.before)
        elif index == 1:

            # Got prompt.  We should be good
            # print "Got prompt, we should be good"
            # print('Got prompt, we should be good')

            bailflag = 1
            connectionBuffer.append(hostConnHandle.before)
        elif index == 2:

           # Got EOF

            LogOutput('error', 'connection to host failed')
            return None
        elif index == 3:

           # Got a Timeout

            LogOutput('error', 'Connection timed out')
            return None
        else:

            # print "Got index ", index, " wainting again"
            # print('Got index %d wainting again'.format(index))

            connectionBuffer.append(hostConnHandle.before)

    # Append on buffer after

    connectionBuffer.append(hostConnHandle.after)

    # Now lets put in the topology the expect handle

    for curLine in connectionBuffer:

       # LogOutput('debug', curLine)

        sanitizedBuffer += curLine
    LogOutput('debug', sanitizedBuffer)

    # Lets go and detect our connection - this will get us to a context we know about

    retVal = switch.DetectConnection(hostConnHandle)
    if retVal is None:
        LogOutput('error',
                         'Failed to detect connection for device - looking to reset console'
                         )
        return None
    return hostConnHandle
