###PROC+#####################################################################
# Name:        switch.ErrorCheck
#
# Namespace:   switch
#
# Author:      Vince Mendoza
#
# Purpose:     Logic Check error after a command has run
#
# Params:      connection - expect connection handle
#              buffer     - expect buffer to check for errors
#
# Returns:     Dictionary with the following
#              returnCode = 0 for pass, 1 for fail

#
##PROC-#####################################################################

import pexpect
import headers
import common
import switch
import re

def ErrorCheck(**kwargs):
   connection = kwargs.get('connection')
   buffer = kwargs.get('buffer')
   # Local variables
   returnCode = 0

   retStruct = dict()
   retStruct['returnCode'] = returnCode

   # Set up the command for error check
   command = "echo $?"
   buffer = ""
   connection.send(command)
   connection.send('\r\n')

   index = connection.expect(['root@\S+:.*#\s*$','bash-\d+.\d+#\s*$'], timeout=200)
   if index == 0 or index == 1:
      buffer += connection.before
      buffer += connection.after
   else:
      common.LogOutput('error', "Received timeout in switch.ErrorCheck")
      retStruct['returnCode'] = 1
      return retStruct


   bufferSplit = buffer.split("\n")
   for curLine in bufferSplit:
      testforValue = re.match("(^[0-9]+)\s*$", curLine)
      if testforValue:
         # Means we got a match
         exitValue = int(testforValue.group(1))
         if exitValue != 0:
            returnCode = exitValue
         else:
            returnCode = 0

   retStruct['returnCode'] = returnCode
   return retStruct
