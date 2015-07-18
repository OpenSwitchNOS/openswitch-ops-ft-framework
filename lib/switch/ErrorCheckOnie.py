###PROC+#####################################################################
# Name:        switch.CLI.ErrorCheck
#
# Namespace:   switch.CLI
#
# Author:      Payal Upadhyaya 
#
# Purpose:     Logic Check error after a  CLI command has run
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
import pdb

def ErrorCheckOnie(**kwargs):
   connection = kwargs.get('connection')
   buffer = kwargs.get('buffer')
   # Local variables
   returnCode = 0
   
   returnDict= dict()
   returnDict['returnCode'] = returnCode
   
   bufferSplit = buffer.split("\n")
   pdb.set_trace()
   for line in bufferSplit:
     #Enter a error code for every failure 
     #Error codes correspond to errors in expect buffer interactions with switch 

     Error_Code1= re.match(".*(command not found)",line,re.I)
     if re.match(".*(command not found)",line,re.I) :
       common.LogOutput("error","Error detected--->"+Error_Code1.group(1))
       returnCode = 2 

   returnDict['returnCode'] = returnCode 
   return returnDict

