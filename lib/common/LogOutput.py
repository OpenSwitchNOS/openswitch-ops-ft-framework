###PROC+#####################################################################
# Name:        common.LogOutput
#
# Namespace:   common
#
# Author:      Vince Mendoza
#
# Purpose:     Standard routine to print to standard out.
#q
# Params:      dest - destination handle
#              message - string to print out
#              datestamp - push datastamp
#
# Returns:     None
#
##PROC-#####################################################################
__doc__ = "LogOutput documentation string"
import time
import datetime
import sys
import headers
import inspect
import common

def LogOutput(dest, message, **kwargs):  
   datestamp = kwargs.get('datastamp', False)  
   logType = str(dest)


   if datestamp is True:
      timestring = time.strftime("%m/%d/%y %H:%M:%S", time.localtime())
   else:
      timestring = time.strftime("%H:%M:%S", time.localtime())
   messageSpl = message.split("\n")
   timestampSent = 0
   for msgLine in messageSpl:
       if timestampSent:
          #print '\t' + logType + '  ' + msgLine
          print('%s'%msgLine)
       else:
          # examine the callstack to print out.  
          mystack = inspect.stack()
          #print mystack
          mystacklen = len(mystack)
          stackstring = ""
          i = mystacklen - 1
          while i > 0:
             curMod = mystack[i][3]
             if curMod == "<module>":
                # Need to skip module
                i -= 1
                continue
             stackstring += curMod
             i -= 1
             if i > 0:
                stackstring += "->"
             #Inspect the stacktrace to get the called module 
             #Module trace needs to be dumped to logging module
             stackTrace = inspect.stack()
             module = inspect.getmodule(stackTrace[1][0])
             len1 = len(stackTrace)
             if len1 >= 4:
              if module <> None :
                modulename =  module.__name__

       # = inspect.stack()[1][3]
       if logType == 'info' or logType == 'error':
          print("%s %-6s\t%s"%(timestring,logType,msgLine))
       #else:
       #   print("%s %-5s\t[%s] %s"%(timestring,logType,stackstring,msgLine))
          #print(timestring, " ", logType, " ", msgLine)
       #   timestampSent = 1

 #Logging messages to Log files based on severity 
   try :
    if modulename <> "common.tcAction":
     message = "::%-30s\t%s"%(modulename,message)
   except NameError:
    #message = message
    blankString = ""
    if logType == 'info':
       message = "%s"%(message)
    else:
       message = "::%s"%(message) 
   common.LogLib.LogOutputToFile(headers.ResultsDirectory['resultsDir'], dest, message)
