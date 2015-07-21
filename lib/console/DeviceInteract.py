###PROC+#####################################################################
# Name:        console.DeviceInteract
#
# Namespace:   console
#
# Author:      Vince Mendoza
#
# Purpose:     Logic to interact with switch device
#
# Params:      connection - pexpect connection handle
#              command    - command to send to device
#
#
# Returns:     Dictionary with the following
#              returnCode = 0 for pass, 1 for fail
#              buffer - buffer of command
#
##PROC-#####################################################################

import pexpect
import headers
import common
import console
import switch
import xml.etree.ElementTree

def DeviceInteract(**kwargs):

   connection = kwargs.get('connection')
   command = kwargs.get('command')


   # Local variables
   bailflag = 0
   returnCode = 0
   retStruct = dict()
   retStruct['returnCode'] = 1
   retStruct['buffer'] = []

   # Send the command
   connection.send('\n')
   connection.send(command)
   connection.send('\n')

   #connection.send('\n')
   connectionBuffer = []
   expectMatchArray = ['InReach:\d+\s*>>$',
                       'Type a key',
                        pexpect.EOF,
                        pexpect.TIMEOUT]
   while bailflag == 0:
       index = connection.expect(expectMatchArray, timeout=20)
       #print "Index I got was ", index
       if index == 0:
           # Prompt
           connectionBuffer.append(connection.before)
           bailflag = 1
       elif index == 1:
           # We got a more prompt
           connection.send('\n')
           connectionBuffer.append(connection.before)
       elif index == 2:
           # EOF
           common.LogOutput('error', "Telnet to switch failed")
           returnCode = 1
       elif index == 3:
           common.LogOutput('error', "Telnet to switch timedout")
           returnCode = 1
       else :
           #print "Got index ", index, " wainting again"
           #print('Got index %d wainting again'.format(index))
           connectionBuffer.append(connection.before)
   connectionBuffer.append(connection.after)
   # Now lets put in the topology the expect handle
   santString = ""
   for curLine in connectionBuffer:#
     santString += curLine



   # Return dictionary
   retStruct['returnCode'] = returnCode
   retStruct['buffer'] = santString

   return retStruct
