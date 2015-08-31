###PROC+#####################################################################
# Name:        switch.PacketCapture
#
# Namespace:   switch
#
# Author:      Payal Upadhyaya 
#
# Purpose:     Capture packets on a connected worktsation using tshark and parse 
#              for packet specific information 
#
#              Pcap file exists in /tmp folder on the workstation which is 
#              transferred to the results folder
#               
# Methods:     - StartCapture
#              - ParseCapture
#
#
# Returns:     Dictionary with the following fields (JSON format)
#              returnCode = 0 for pass, 1 for fail
#              frameList = Two dimensional dictionary with frame numbers,
#                          and packet fields as the keys
#              Eg : 
#
##PROC-#####################################################################

import pexpect
import time
import switch
import host
import re
import os
import collections
from lib import *

class PacketCapture() :
  returnDict = dict()
  def __init__(self,device,filename):
    self.device = device
    self.filename = filename
   
  #Starts packet capture on workstation: 
  def StartCapture(self,**kwargs):
    #Start the tshark process to capture packets on eth1 interface of workstation
    connection = kwargs.get('connection')
    filter = kwargs.get('filter',None)
    LogOutput('info', "Start packet capture on the device->"+self.device)
    if filter is None :
     command = "tshark -l -i eth1 -V > /tmp/%s &"%(self.filename)
     #command = "tshark -l -i eth1 -F libpcap -V -w /tmp/capture.pcap"
    else :
     command = "tshark -l -i eth1 -V -f %s > /tmp/%s &"%(filter,self.filename)

    returnStruct = host.DeviceInteract(connection=connection, command=command)
    returnCode = returnStruct.get('returnCode')
    if returnCode != 0:
        LogOutput('error', "Failed to start capture on the device->"+self.device)
        returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=self.returnDict)
        return returnJson

  #Parse packets captured on the workstation
  def ParseCapture(self,connection,**kwargs) :
    FrameDetails = dict()
    FrameDetails = collections.defaultdict(dict)
    #Parse the captured output from the pcap files captured using tshark
    #Kill the tshark processes running on VM
    LogOutput('info', "Kill the tshark processes running on the workstation")
    command = "/usr/bin/killall -w \"tshark\""
    returnStruct = host.DeviceInteract(connection=connection, command=command)
    returnCode = returnStruct.get('returnCode')
    if returnCode != 0:
        LogOutput('error', "Failed to kill tshark processes on the device->"+self.device)
        returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=self.returnDict)
        return returnJson

    #Download the capture file to local results directory
    CaptureLog = "%s--%s"%(self.device,self.filename)
    filepath = '/tmp/%s'%(self.filename)
    localpath = headers.ResultsDirectory['resultsDir']+CaptureLog
    returnCode = host.SCPFileTransfer(self.device,self.filename,filepath,localpath)
    if returnCode != 0 :
        LogOutput('error', "Failed to transfer capture file to results directory")
        returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=self.returnDict)
        return returnJson
        
    #Read the capture file to parse for the protocol headers/packets 
    fileHandle = open(localpath,"r")
    captureBuffer = fileHandle.read()
    frameCount = 0
    FrameList = re.split(r'Frame \d+:',captureBuffer)
    #FrameList has the capture packet buffer as list
    FrameList = filter(None,FrameList)
    if len(FrameList) != 0 :
     for frame in FrameList:
        frameCount = frameCount + 1
        splitFrame = frame.split('\n') 
        for line in splitFrame :
         line = line.strip()

   #<This block needs to replicated for whichever protocol packets need to be parsed>
         #Regular expressions to parse the tshark output buffer frames
         #LLDP frame parsing begins here
         #Protocol
         Protocol = re.match(r'\[Protocols in frame:\s+([A-Za-z:0-9]+)\]',line)
         if Protocol:
          if not FrameDetails.get(frameCount, {}).has_key(Protocol):
           FrameDetails[frameCount]['Protocol'] =Protocol.group(1)
           LogOutput("info","LLDP protocol detected -->" + FrameDetails[frameCount]['Protocol'])
         #System Name
         LldpSystemName = re.match(r'System Name = ([A-Za-z1-9]+)',line)  
         if LldpSystemName:
          if not FrameDetails.get(frameCount, {}).has_key(LldpSystemName):
           FrameDetails[frameCount]['LldpSystemName'] = LldpSystemName.group(1)
         #Port ID:
         PortID = re.match(r'Port Id: (\d+)',line)
         if PortID:
          if not FrameDetails.get(frameCount, {}).has_key(PortID):
           FrameDetails[frameCount]['PortID'] = PortID.group(1)
         #Time To Live
         TimeToLive = re.match(r'Time To Live = (.*)',line)
         if TimeToLive:
          if not FrameDetails.get(frameCount, {}).has_key(TimeToLive):
           FrameDetails[frameCount]['TimeToLive'] = TimeToLive.group(1)      
         #System Description
         SystemDescription = re.match(r'System Description = (.*)',line)
         if SystemDescription :
          if not FrameDetails.get(frameCount, {}).has_key(SystemDescription ):
           FrameDetails[frameCount]['SystemDescription '] = SystemDescription.group(1)
         #Port Vlan Identifier
         PortVLanID = re.match(r'Port VLAN Identifier: (.*)',line)
         if PortVLanID  :
          if not FrameDetails.get(frameCount, {}).has_key(PortVLanID):
           FrameDetails[frameCount]['PortVLanID'] = PortVLanID.group(1)
         #Vlan Name
         VlanName = re.match(r'VLAN Name: (.*)',line)
         if VlanName :
          if not FrameDetails.get(frameCount, {}).has_key(VlanName):
           FrameDetails[frameCount]['VlanName'] =VlanName .group(1)
         #Port Description
         PortDescr = re.match(r'Port Description = (.*)',line)
         if PortDescr:
          if not FrameDetails.get(frameCount, {}).has_key(PortDescr):
           FrameDetails[frameCount]['PortDescr'] =PortDescr.group(1)
  #<Block ends here ***>>
     #Frame parsing ends
     #Dump the results in Dictionary(returnDict)
     self.returnDict = FrameDetails
    
     #Delete the pcap file from workstation in /tmp folder  
     filepath = "/tmp/"+self.filename
     command = "rm -f %s"%(filepath)
     returnStruct = host.DeviceInteract(connection=connection, command=command)
     returnCode = returnStruct.get('returnCode')
     if returnCode != 0:
        LogOutput('error', "Failed to remove capture file from workstation ->"+self.device)
        returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=self.returnDict)
        return returnJson

     #Return results(makes a json structure of the dictionary(returnDict) and return code) 
     returnJson = common.ReturnJSONCreate(returnCode=0, data=self.returnDict)
     return returnJson
    else :
     LogOutput("info","No Frames captured *** ")
     returnJson = common.ReturnJSONCreate(returnCode=1, data=self.returnDict)
     return returnJson
     #End of method ParseCapture

