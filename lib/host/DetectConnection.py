###PROC+#####################################################################
# Name:        host.DetectConnection
#
# Namespace:   host
#
# Author:      Srinivasa Krishnappa
#
# Purpose:     Logic to detect a connection and get us to a prompt
#
# Params:      connection - pexpect connection handle
#
# Returns:     connection or None
#
##PROC-#####################################################################

import pexpect
import headers
import common
import xml.etree.ElementTree

def DetectConnection(connection):
    bailflag = 0
    #print "In detect " 
    
    connection.send('\r')
    connectionBuffer = []
    sanitizedBuffer = ""
    while bailflag == 0:
        index = connection.expect(['login:', 'Password:', 'root@\S+\d+\d+.*#', pexpect.EOF,pexpect.TIMEOUT], timeout=200)
        #print "Index I got was ", index
        if index == 0:
            # Need to send login string
            connection.sendline("root")
            connectionBuffer.append(connection.before)
        elif index == 1:
            # Need to send password string
            connection.sendline("procurve")
            connectionBuffer.append(connection.before)
        elif index == 2:
            # Got prompt.  We should be good
            #print "Got prompt, we should be good"
            #print('Got prompt, we should be good')
            bailflag = 1
            connectionBuffer.append(connection.before)
           
        elif index == 3:
           # Got EOF
           common.LogOutput('error', "Telnet to host failed")
           return None
           
        elif index == 4:
           # Got a Timeout
           common.LogOutput('error', "Connection timed out")
           return None
        else :
            #print "Got index ", index, " wainting again"
            #print('Got index %d wainting again'.format(index))
            connectionBuffer.append(connection.before)
    # Append on buffer after
    connectionBuffer.append(connection.after)
    # Now lets put in the topology the expect handle
    for curLine in connectionBuffer:
       #common.LogOutput('debug', curLine)
       sanitizedBuffer += curLine
    common.LogOutput('debug', sanitizedBuffer)
    
    return connection
 
