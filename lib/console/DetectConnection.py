###PROC+#####################################################################
# Name:        console.DetectConnection
#
# Namespace:   console
#
# Author:      Vince Mendoza
#
# Purpose:     Logic to detect a connection and get us to a prompt
#
# Params:      connection - pexpect connection handle
#              username - username for login
#              password - password for login
#              adminPassword - administrative password for enable mode
#
# Returns:     connection or None
#
##PROC-#####################################################################

import pexpect
import headers
import common
import xml.etree.ElementTree

def DetectConnection(**kwargs):
    # Arguments
    connection = kwargs.get('connection')
    username = kwargs.get('username')
    password = kwargs.get('password')
    adminPassword = kwargs.get('adminPassword')
    
    bailflag = 0
    level = 0
    connection.send('\n')
    connectionBuffer = []
    sanitizedBuffer = ""
    expectMatchArray = ['Login:',
                        'Password:',
                        '\S+:\d+\s*>$',
                        '\S+:\d+\s*>>$',
                        pexpect.EOF,
                        pexpect.TIMEOUT]
    while bailflag == 0:
        index = connection.expect(expectMatchArray, timeout=200)
        #print "Index I got was ", index
        if index == 0:
            # Need to send login string
            connection.sendline(username)
            connectionBuffer.append(connection.before)
        elif index == 1:
            # Password Prompt
            if level == 0:
               connection.sendline(password)
               level = 1
            elif level == 1:
               connection.sendline(adminPassword)
            connectionBuffer.append(connection.before)
        elif index == 2:
            # First level prompt - get us to the enable mode
            connection.sendline("enable")
            connectionBuffer.append(connection.before)
        elif index == 3:
            # We are in the enabled prompt
            connectionBuffer.append(connection.before)
            bailflag = 1
        elif index == 4:
           # Got EOF
           common.LogOutput('error', "Telnet to switch failed")
           return None
        elif index == 5:
           # Got a Timeout
           common.LogOutput('error', "Connection timed out")
           return None
        else :
            #print "Got index ", index, " wainting again"
            print('Got index %d wainting again'.format(index))
            connectionBuffer.append(connection.before)
    # Append on buffer after
    connectionBuffer.append(connection.after)
    # Now lets put in the topology the expect handle
    for curLine in connectionBuffer:
       #common.LogOutput('debug', curLine)
       sanitizedBuffer += curLine
    common.LogOutput('debug', sanitizedBuffer)
    
    return connection
 
