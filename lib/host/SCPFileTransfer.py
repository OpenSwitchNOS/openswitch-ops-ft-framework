###PROC+###################################################################################################
# Name:        switch.SCPFileTransfer
#
# Namespace:   switch
#
# Author:      Payal Upadhyaya 
#
# Purpose:     SCP files to local path 
#              Tranfers files from docker container in case of virtual topology
#
#
# Params:      connection - device :: Device name (as defined in headers.topology
#                         - filename :: name of the file to be transferred 
#                         - filepath :: Path of the file to be transferred from remote machine (absolute)
#                         - localpath :: Local absolute path wher ethe file should be copied
#
# Returns:     returnCode = 0 for pass, 1 for fail
#
#
###########################################################################################################
import common
import os
import paramiko
import headers 
import xml.etree.ElementTree

def SCPFileTransfer(device,filename,filepath,localpath) : 
  returnCode = 0
  paramiko.util.log_to_file('/tmp/paramiko.log')
  # Look up and see if we are physical or virtual
  xpathString = ".//reservation/id"
  rsvnEtreeElement = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
  if rsvnEtreeElement == None:
  # We are not in a good situation, we need to bail
    common.LogOutput('error', "Could not find reservation id tag in topology")
    return None
  rsvnType = rsvnEtreeElement.text

  if rsvnType != 'virtual':
   #Get the credentials of the workstation from XML file (physical devices) 
   xpathString = ".//device[name='" + device + "']/connection/ipAddr"
   ipNode = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
   if ipNode == None:
     common.LogOutput('error', "Failed to obtain IP address for device " + device )
     return None
   hostIP = ipNode.text
   common.LogOutput ('debug', device + " connection IP address:  " + hostIP)
   port = 22

   #Open a ssh connection to the host
   transport = paramiko.Transport((hostIP, port))

   #Extract username/password for logging in the workstation
   xpathString = ".//device[name='" + device + "']/login/adminPassword"
   password = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
   if password == None:
     common.LogOutput('error', "Failed to obtain password for device " + device )
     return None
   password = password.text
   xpathString = ".//device[name='" + device + "']/login/adminUser"
   username = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
   if username == None:
     common.LogOutput('error', "Failed to obtain username for device " + device )
     return None
   username = username.text

   transport.connect(username = username, password = password)
   sftp = paramiko.SFTPClient.from_transport(transport)
   #Transfer file
   try :
    sftp.get(filepath,localpath)
   except :
    common.LogOutput("error","Capture file not transferred to results directory")
    returnCode = 1
  #Close a connection
   sftp.close()
   transport.close()
   return returnCode
  else :
   common.LogOutput("info","Topology is virtual **")
   common.LogOutput("info","Copy the files from docker container to results directory")
   #Copy the pcap file from docker container to results directory
   command = "docker cp %s:%s %s"%(device,filepath,headers.ResultsDirectory['resultsDir'])
   returnCode = os.system(command)
   os.rename(filename,device+"--"+filename)
   if returnCode != 0:
      common.LogOutput('error', "Failed to copy pcap file to results directory from device --> "+self.device)
      returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=self.returnDict)
      return returnJson

