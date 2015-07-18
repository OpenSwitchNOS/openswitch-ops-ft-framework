###PROC+#####################################################################
# Name:        switch.DeviceInteract
#
# Namespace:   switch
#
# Author:      Vince Mendoza
#
# Purpose:     Logic to interact with switch device
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
import switch
import time
import xml.etree.ElementTree
import pdb
def DeviceInteract(**kwargs):
  
   connection = kwargs.get('connection')
   command = kwargs.get('command')
   errorCheck = kwargs.get('errorCheck',True)
   ErrorFlag = kwargs.get('CheckError')   

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
   connectionBuffer = []
   #if errorCheck is True:
   #   common.LogOutput('debug', "Sending command {" + command + "} to device")
   
   while bailflag == 0:
       #DEBUG print connection
       index = connection.expect(['login:\s*$', 
                                  'root@\S+:.*#\s*$',
                                  '[A-Za-z]+[0-9]+#', 
                                  '\(config\)#',
                                  'ONIE:/\s+#\s*$', 
                                  'bash-\d+.\d+#\s*$',
                                  pexpect.EOF,
                                  pexpect.TIMEOUT], 
                                 timeout=70)
       #print "Index I got was ", index
       if index == 0:
           # Need to send login string
           connection.send("root \r")
           connectionBuffer.append(connection.before)
       elif index == 1:
           # Got prompt.  We should be good
           #print "Got prompt, we should be good"
           #print('Got prompt, we should be good')
           bailflag = 1
           connectionBuffer.append(connection.before)
       elif index == 2:
           # Got vtysh prompts
           ErrorFlag = "CLI"
           bailflag = 1
           connectionBuffer.append(connection.before)
           #$time.sleep(2)
       elif index == 3:
           # Got config prompts
           common.LogOutput('debug', "config prompt")
           ErrorFlag = "CLI"
           bailflag = 1
           connectionBuffer.append(connection.before)
       elif index == 4:
           # Got ONIE prompt - reboot and get to where we need to be
           #connection.send("reboot \r")
           ErrorFlag = "Onie"
           bailflag = 1
           connectionBuffer.append(connection.before)
       elif index == 5:
          # Got bash prompt - virtual
           bailflag = 1
           connectionBuffer.append(connection.before)
       elif index == 6:
          # got EOF
          bailflag = 1
          connectionBuffer.append(connection.before)
          common.LogOutput('error', "connection closed to console")
          returnCode = 1
       elif index == 7:
          # got Timeout
          bailflag = 1
          connectionBuffer.append(connection.before)
          common.LogOutput('error', "command timeout")
          returnCode = 1
       else :
           connectionBuffer.append(connection.before)
   #time.sleep(3)
   connectionBuffer.append(connection.after)
   connection.expect(['$'], timeout=1)
   # Now lets put in the topology the expect handle
   #print "command: " + command + "\nconn buffer:\n" + str(connectionBuffer)
   santString = ""
   for curLine in connectionBuffer:#
     santString += str(curLine)
   
   #Error Check routine identification
   #There are seperate Error check libraries for CLI,OVS and REST commands.
   #The following portion checks for Errors for OVS commands  
   if errorCheck is True and returnCode == 0 and ErrorFlag == None :
      errorCheckRetStruct = switch.ErrorCheck(connection=connection, buffer=santString)
      returnCode = errorCheckRetStruct['returnCode']
      # Dump the buffer the the debug log
      common.LogOutput('debug', "Sent and received from device: \n" + santString + "\n")
   
   #The following portion checks for Errors in CLI commands
   if ErrorFlag == 'CLI' :
      errorCheckRetStruct = switch.CLI.ErrorCheck(connection=connection, buffer=santString)
      returnCode = errorCheckRetStruct['returnCode']

   #The following file checks for errors in Onie prompts after analyzing Onie expect buffer
   if ErrorFlag == 'Onie' :
      errorCheckRetStruct = switch.ErrorCheckOnie(connection=connection, buffer=santString)
      returnCode = errorCheckRetStruct['returnCode']

   # Return dictionary
   common.LogOutput('debug', "Sent and received from device: \n" + santString + "\n")
   retStruct['returnCode'] = returnCode
   retStruct['buffer'] = santString
   return retStruct
