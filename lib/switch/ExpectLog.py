###PROC+#####################################################################
# Name:        switch.ExpectLog
#
# Namespace:   switch
#
# Author:      Payal Upadhyaya
#
# Purpose:    Open pexpect device logs and log timestamped output
#
#
# Params:     Class which helps to log expect device logs in results directory
#
# Returns:
#
##PROC-#####################################################################

import datetime
import time
import headers
import common
import inspect

class DeviceLogger(object):
 #This function overrides the pexpect logger write function to add timestamps to device logs
   def __init__(self, file):
      self.file = file

   def write(self, data):
        # .. filter data however you like
      ts = time.time()
      ts = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
      data = data.strip()

      #Do not log blank spaces
      if data in [' ', '', '\n', '\r', '\r\n']:
        return
      if data: # non-blank
        #Inspect the stacktrace to get the called module
        #Module trace needs to be dumped to logging module
        #This code will not log unnecessary internal modules (so that log looks clean)
        stackTrace = inspect.stack()
        module = inspect.getmodule(stackTrace[4][0])
        if module <> None :
          modulename =  module.__name__
          if modulename == "pexpect" :
            modulename = None
          else :
            self.file.write("++++"+ts+"  "+"Module:"+"("+modulename+")"+"  "+"\n")
        return self.file.write(data+"\n")
       #return self.file.write("%s %s" % (ts, data))  # write to original file
   def flush(self):
        self.file.flush()

 #OpenExpectLog function opens a new file to log the expect buffer output
 #Return 1 in case of error (expect logfile not created) , expect file handle in case of success

   def OpenExpectLog(self,ExpectFileName) :
     retCode = common.FileCreate(headers.ResultsDirectory['resultsDir'],ExpectFileName)
     if retCode['returnCode'] == 0:
       headers.ResultsDirectory['ExpectFileName'] = headers.ResultsDirectory['resultsDir']+"/"+ExpectFileName
       expectLogfile = open(headers.ResultsDirectory['ExpectFileName'],'w')
       return expectLogfile
     else :
       returnCode = 1
     return returnCode


