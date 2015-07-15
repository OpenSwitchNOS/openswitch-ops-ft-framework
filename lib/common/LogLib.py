###PROC+#####################################################################
# Name:        logging.LogLib
#
# Namespace:   common
#
# Author:      Srinivasa Krishnappa
#
# Purpose:     Standard routine to print to logfiles.
#
# Params:      dest - destination handle
#              message - string to print out
#
# Returns:     None
#
##PROC-#####################################################################
__doc__ = "LogOutput documentation string"
import time
import datetime
import sys
import headers
import logging
import os

#library routine to write the logger message to summary and detail file based on the level
def LogOutputToFile(path, level, message):
   intResult = 1
   strSummaryFileName = path + "summary.log"
   strDetailedFileName = path + "detail.log"
   if (os.access(strSummaryFileName, os.W_OK)) :
        pass
   else :
        print("either file not exists for %s or no write permission" %strSummaryFileName)
        return intResult

   if (os.access(strDetailedFileName, os.W_OK)) :
        pass
   else :
        print("either file not exists for %s or no write permission" %strDetailedFileName)
        return intResult

   if (level == "debug"):
        writeLogFile(strDetailedFileName, level, message)
   else :
        writeLogFile(strSummaryFileName, level, message)
        writeLogFile(strDetailedFileName, level, message)
   intResult = 0
   return intResult

#internal routine to write the logger message to passed file

def writeLogFile(logfile, level, message) :

   logger = logging.getLogger()
   formatter = logging.Formatter('%(levelname)-5s - %(asctime)-6s - %(message)s','%H:%M:%S')
   fh = logging.FileHandler(logfile)
   if (level == "info"):
        fh.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.info(message)
   elif (level == "error"):
        fh.setLevel(logging.ERROR)
        logger.setLevel(logging.ERROR)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.error(message)
   elif (level == "debug"):
        fh.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.debug(message)
   logger.removeHandler(fh)
