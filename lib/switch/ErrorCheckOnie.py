###PROC+#####################################################################
# Name:        switch.ErrorCheckOnie
#
# Namespace:   switch
#
# Author:      Payal Upadhyaya 
#
# Purpose:     Logic Check error after commands at Onie prompt run
#
# Params:      connection - expect connection handle
#              buffer     - expect buffer to check for errors
#
# Returns:     Dictionary with the following
#              returnCode = 0 for pass
#              Analyses the buffer & returns a different code for every failure 
#
##PROC-#####################################################################

import pexpect
import headers
import common
import switch
import re

#Add a unique error code  for every failure at Onie prompts 
def ErrorCheckOnie(**kwargs):
   connection = kwargs.get('connection')
   buffer = kwargs.get('buffer')
   # Local variables
   returnCode = 0
   
   returnDict= dict()
   returnDict['returnCode'] = returnCode
   
   bufferSplit = buffer.split("\n")
   for line in bufferSplit:
     #Enter a error code for every failure 
     #Error codes correspond to errors in expect buffer interactions with switch Onie prompt

     Error_Code101= re.match(".*(command not found)",line,re.I)
     if re.match(".*(command not found)",line,re.I) :
       common.LogOutput("error","Error detected--->"+Error_Code101.group(1))
       returnCode = 101

     Error_Code102= re.match(".*(Network is unreachable)",line,re.I)
     if re.match(".*(Network is unreachable)",line,re.I) :
       common.LogOutput("error","Error detected--->"+Error_Code102.group(1))
       common.LogOutput("error","DHCP network IP unreachable")
       returnCode = 102

     Error_Code103= re.match(".*(File not found)",line,re.I)
     if re.match(".*(File not found)",line,re.I) :
       common.LogOutput("error","Error detected--->"+Error_Code103.group(1))
       common.LogOutput("error","File not found")
       returnCode = 103

     Error_Code104 = re.match(".*(No such file or directory)",line,re.I)
     if re.match(".*(No such file or directory)",line,re.I) :
       common.LogOutput("error","Error detected--->"+Error_Code104.group(1))
       common.LogOutput("error","No such file or directory")
       returnCode = 104

     Error_Code105 = re.match(".*(not found)",line,re.I)
     if re.match(".*(not found)",line,re.I) :
       common.LogOutput("error","Error detected--->"+Error_Code105.group(1))
       common.LogOutput("error","Error::Not Found")
       returnCode = 105

     Error_Code106 = re.match(".*(bad address)",line,re.I)
     if re.match(".*(bad address)",line,re.I) :
       common.LogOutput("error","Error detected--->"+Error_Code106.group(1))
       common.LogOutput("error","Error::bad address")
       returnCode = 106

   returnDict['returnCode'] = returnCode 
   return returnDict

