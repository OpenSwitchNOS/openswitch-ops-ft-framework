###PROC+#####################################################################
# Name:        switch.DetectConnection
#
# Namespace:   switch
#
# Author:      Vince Mendoza
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
import time
import xml.etree.ElementTree

def DetectConnection(connection):
    bailflag = 0
    #print "In detect " 
    
    connection.send('\r')
    time.sleep(2)
    connectionBuffer = []
    sanitizedBuffer = ""
    while bailflag == 0:
        index = connection.expect(['login:\s*$', 
                                   'root@\S+:.*#\s*$',
                                   '\(config\)#',
                                   '[A-Za-z]+[0-9]+#',
                                   'ONIE:/\s+#', 
                                   'bash-\d+.\d+#', 
                                   pexpect.EOF,
                                   pexpect.TIMEOUT], 
                                   timeout=200)
        #print "Index I got was ", index
        if index == 0:
            # Need to send login string
            common.LogOutput("debug","Login required::")
            connection.sendline("root")
            connectionBuffer.append(connection.before)
        elif index == 1:
            # Got prompt.  We should be good
            #print('Got prompt, we should be good')
            bailflag = 1
            common.LogOutput("debug","Root prompt detected:")
            connectionBuffer.append(connection.before)
        elif index == 2:
            common.LogOutput("debug","vtysh config prompt detected: Revert to root")
            connection.send ('end \r')
            connectionBuffer.append(connection.before)
        elif index == 3:
            common.LogOutput("debug","vtysh prompt detected: Revert to root")
            connection.send ('exit \n')
            connectionBuffer.append(connection.before)
        elif index == 4:
            # Got ONIE prompt - reboot and get to where we need to be
            connection.sendline("reboot")
            connectionBuffer.append(connection.before)
        elif index == 5:
            # Got prompt.  We should be good
            bailflag = 1
            common.LogOutput("debug","Root prompt detected: Virtual")
            connectionBuffer.append(connection.before)
        elif index == 6:
           # Got EOF
           common.LogOutput('error', "Telnet to switch failed")
           return None
        elif index == 7:
           # Got a Timeout
           common.LogOutput('error', "Connection timed out")
           return None
        else :
            #print "Got index ", index, " wainting again"
            #print('Got index %d wainting again'.format(index))
            connectionBuffer.append(connection.before)
    # Append on buffer after
    connectionBuffer.append(connection.after)
    connection.expect(['$'], timeout=2)
    # Now lets put in the topology the expect handle
    for curLine in connectionBuffer:
       sanitizedBuffer += curLine
    common.LogOutput('debug', sanitizedBuffer)
    return connection
 
