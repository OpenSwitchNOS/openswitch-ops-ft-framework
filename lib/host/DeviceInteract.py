###PROC+#####################################################################
# Name:        host.DeviceInteract
#
# Namespace:   host
#
# Author:      Srinivasa Krishnappa
#
# Purpose:     Logic to interact with host device
#
# Params:      connection - pexpect connection handle
#              command    - command to send to device
#              errorCheck - True or False - default is True
#                           If False, you will bypass running ErrorCheck Routine
#
# Returns:     Dictionary with the following
#              returnCode = 0 for pass, 1 for fail
#              buffer - buffer of command
#
##PROC-#####################################################################

import pexpect
import headers
import common
import host
import time
import xml.etree.ElementTree

def DeviceInteract(**kwargs):
  
   connection = kwargs.get('connection')
   command = kwargs.get('command')
   errorCheck = kwargs.get('errorCheck', True)

   # Local variables
   bailflag = 0
   returnCode = 0
   retStruct = dict()
   retStruct['returnCode'] = 1
   retStruct['buffer'] = []
   
   # Send the command
   connection.send(command)
   connection.send('\r')
   time.sleep(1)
   #connection.send('\r')
   connectionBuffer = []
   #if errorCheck is True:
   #   common.LogOutput('debug', "Sending command {" + command + "} to device")
   
   while bailflag == 0:
       #DEBUG print connection
       index = connection.expect(['login:', 'Password:', 'root@\S+\d+\d+.*#','Capturing on eth1',pexpect.EOF,pexpect.TIMEOUT], timeout=200)
       if index == 0:
           # Need to send login string
           connection.sendline("root")
           connectionBuffer.append(connection.before)
       elif index == 1:
           # Need to send password string
           connection.sendline("procurve")
           connectionBuffer.append(connection.before)
       elif index ==2:
           # Got prompt.  We should be good
           #print "Got prompt, we should be good"
           #print('Got prompt, we should be good')
           bailflag = 1
           connectionBuffer.append(connection.before)
       elif index ==3:
           common.LogOutput('info',"Started packet capture**")
           bailflag = 1
           connectionBuffer.append(connection.before)
       elif index == 3:
          # got EOF
          bailflag = 1
          connectionBuffer.append(connection.before)
          common.LogOutput('error', "reached EOF")
          returnCode = 1
       elif index == 4:
          # got Timeout
          bailflag = 1
          connectionBuffer.append(connection.before)
          common.LogOutput('error', "command timeout")
          returnCode = 1
       else :
           connectionBuffer.append(connection.before)
   #time.sleep(3)
   connectionBuffer.append(connection.after)
   connection.expect(['$'], timeout=2)
   #time.sleep(1)
   # Now lets put in the topology the expect handle
   #print "command: " + command + "\nconn buffer:\n" + str(connectionBuffer)
   santString = ""
   for curLine in connectionBuffer:#
     santString += str(curLine)
   
   returnCode = 0
   if errorCheck is True and returnCode == 0:
      errorCheckRetStruct = host.ErrorCheck(connection=connection, buffer=santString)
      returnCode = errorCheckRetStruct['returnCode']
      # Dump the buffer the the debug log
      common.LogOutput('debug', "Sent and received from device: \n" + santString + "\n")
   
   # Return dictionary
   retStruct['returnCode'] = returnCode
   retStruct['buffer'] = santString
   
   return retStruct
