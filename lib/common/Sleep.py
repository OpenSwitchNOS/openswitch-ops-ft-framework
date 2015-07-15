###PROC+#####################################################################
# Name:        common.Sleep
#
# Namespace:   common
#
# Author:      Vince Mendoza
#
# Purpose:     Routine to sleep a number of seconds and show time countdown 
#
# Params:      message 
#              seconds
#
# Returns:     None
#
##PROC-#####################################################################
__doc__ = "Sleep documentation string"
import common
import time
import datetime
import headers
import sys

#Params ::  Directory Path to be created 
def Sleep(**kwargs):
   message = kwargs.get('message')
   seconds = kwargs.get('seconds')
   
   message = message + " - Pausing for " + str(seconds) + " seconds"
   common.LogOutput('info', message)
   rangeUpper = seconds + 1
   for i in range(1, rangeUpper):
      time.sleep(1)
      #backspacestring = "\r"
      sys.stdout.write("\r")
      
      printstring = "\t\t%-2d of %-2d"%(i, seconds)
      printstringlen = len(printstring)
      sys.stdout.write(printstring)
      sys.stdout.flush()
   #print ""
   sys.stdout.write("\r")
   common.LogOutput('info', "Completed wait for %d seconds"%seconds)
