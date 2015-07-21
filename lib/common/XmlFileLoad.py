###PROC+#####################################################################
# Name:        common.XmlFileLoad
#
# Namespace:   common
#
# Author:      Vince Mendoza
#
# Purpose:     Routine to load an xml file in to an etree
#
# Params:      xmlFile
#
#
# Returns:     etree - This will be the etree pointer or None if no file exists
#
##PROC-#####################################################################
import xml.etree.ElementTree
import os
import common

def XmlFileLoad(xmlFile):
   # check and see if the file exists
   fileExists = os.path.exists(xmlFile)
   if fileExists == False:
      common.LogOutput('info', "File " + xmlFile + " does not exist.")
      return None

   eTree = xml.etree.ElementTree.parse(xmlFile)
   return eTree