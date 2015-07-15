###PROC+#####################################################################
# Name:        common.ResultDirectoryCreate
#
# Namespace:   common
#
# Author:      Payal Upadhyaya
#
# Purpose:     Routines to carry out directory and file operations 
#q
# Params:      
#
# Returns:     retStruct (A dictionary which contains returnCode (0 for pass , 1 for fail)
#
##PROC-#####################################################################
__doc__ = "ResultDirectoryCreate documentation string"
import os
import common
import time
import datetime
import headers

#Local variables
returnCode = 0
retStruct = dict(returnCode = 1 , buffer = [])

#Result directory structure (string)
ts = time.time()
dateTimeString = datetime.datetime.fromtimestamp(ts).strftime('%Y-%b-%d_%H:%M:%S')

#Function to create a directory 
#Params ::  Directory Path to be created 
def CreateDirectory(dirName):
   dir = os.path.dirname(dirName)
   if not os.path.exists(dirName):
    os.makedirs(dir)
    if os.path.exists(dir) :
      retStruct['DirPath'] = os.getcwd()+dirName
      retStruct['returnCode'] = 0
    else :
      common.LogOutput('error',"Result Directory"+dir ,"not created")
      retStruct['returnCode'] = 1
   else :
    retStruct['returnCode'] = 1
   return retStruct
 
#Function to change directory path 
# Params  :: Destination Path 
def ChangeDirectory(path):
   try :
    os.chdir(path)	
    retStruct['returnCode'] = 0
   except :
    retStruct['returnCode'] = 1
   return retStruct

#Function to Get directory 
# Returns the current dir path on success
def GetCurrentDirectory():
    currentDir = os.getcwd()
    if currentDir is None:
     retStruct['returnCode'] = 1
     return retStruct
    else :
     return currentDir

#Creating new files 
#Params :: Filename , Directory path where file should exists. (Dir must exist)

def FileCreate(DirPath,fileName):
 filePath = os.path.join(DirPath,fileName)
 try :
  if not os.path.exists(fileName):
    #pdb.set_trace()
    file = open(filePath,'w')   # Trying to create a new file or open one
    #file.close()
    retStruct['returnCode'] = 0
  else :
    print "File already exists in this path" + DirPath
    #do nothing
 except Exception as Err:
   print Err
   raise Exception("FILE NOT CREATED:: "+fileName)
   retStruct['returnCode'] = 1
 return retStruct

