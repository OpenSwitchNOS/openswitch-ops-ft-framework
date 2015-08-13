###PROC+#####################################################################
# Name:        switch.TftpImageOnieDownload
#
# Namespace:   switch
#
# Author:      Payal Upadhyaya 
#
# Purpose:     Provision the physical DUT with image from tftp server in RTL
#              Repository Location:/warp/pub
#              This class provides support for image upgrade/downgrade operation done at Onie 
#              prompt of the physical Openswitch 
#               
# Params:      connection - expect connection handle
#
#
# Returns:     Dictionary with the following fields (JSON format)
#              returnCode = 0 for pass, 1 for fail
#              buffer - buffer of command
#
##PROC-#####################################################################

import pexpect
import headers
import common
import time
import switch
#import topology
import RTL
import os
import re

class TftpImageOnieDownload() :
  returnDict = dict()
  def __init__(self,device):
      self.device = device
      self.AddUplink = 0
      #Add the Tftp uplink port to  device(DUT)
      #The constructor returns AddUplink = 1 if no uplink gets added to the DUT
      common.LogOutput("info","Dynamically add the Tftp uplink port to  device(DUT)")
      returnJson = RTL.UplinkPortAdd(device=device)
      returnCode = common.ReturnJSONGetCode(json=returnJson) 
      TftpUplinkIP = common.ReturnJSONGetData(json=returnJson,dataElement="IP")
      if TftpUplinkIP is None :
       common.LogOutput('error', "Failed to get the TFTP IP for the uplink")
       self.AddUplink = 1
      else :
       self.TftpUplinkIP = TftpUplinkIP.replace("\"","")
      if returnCode != 0:
        common.LogOutput('error', "Failed to add TFTP uplink to device")
        self.AddUplink = 1

  def  TftpOperation(self,**kwargs):
     #Exit flags in case if failure
     ExitFlag1 = 0
     ExitFlag2 = 0
     ExitFlag3 = 0
     ExitFlag4 = 0
     self.returnCode = 0

     common.LogOutput("info","PROVISIONING HALON Physical device")
     connection = kwargs.get('connection')
 
     #Reboot the switch to Onie rescue mode in order to install image 
     common.LogOutput("info","Enter the Onie rescue mode for provisioning the physical device")
     connection = switch.Reboot(connection=connection,onie=True,onieMode="rescue")
     if connection:
       common.LogOutput("info","Switch rebooted to Onie prompt for image upgrade")
     else :
       common.LogOutput("error","Switch not rebooted to Onie prompt for image upgrade")
       self.returnDict = "None"       
       self.returnCode = 1
       ExitFlag1 = 1

     #TFTP configurations in Onie Rescue prompt
     if ExitFlag1 == 0 and ExitFlag2 == 0 and ExitFlag3 == 0 and ExitFlag4 ==0 :
      command = "tftp -g -r %s %s"%(headers.TftpImage['Image'],self.TftpUplinkIP)
      #command = "tftp -g -r %s 120.93.49.9"%(headers.TftpImage['Image'])
      common.LogOutput("info","TFTP download ***")
      #Get the device response buffer as json return structure here(At Onie prompt) 
      devIntRetStruct = switch.DeviceInteract(connection=connection, command=command)
      self.returnCode = devIntRetStruct.get('returnCode')
      self.returnDict['onieRescue'] = devIntRetStruct.get('buffer')
      if self.returnCode != 0:
       common.LogOutput('error', "Failed to get TFTP image")
       ExitFlag2 = 1

     #Change the permissions of the image and run the image executable file to install Halon
     if ExitFlag1 == 0 and ExitFlag2 == 0 and ExitFlag3 == 0 and ExitFlag4 ==0 :
      command = "chmod 777 %s"%(headers.TftpImage['Image'])
      common.LogOutput("info","Change the permissions of the image and run the image executable file***")
      devIntRetStruct = switch.DeviceInteract(connection=connection, command=command)
      self.returnCode = devIntRetStruct.get('returnCode')
      self.returnDict['ImageState'] = devIntRetStruct.get('buffer')
      if self.returnCode != 0:
       common.LogOutput('error', "Failed to change permissions of the image and run the image executable file")
       ExitFlag3 = 1
     
     if ExitFlag1 == 0 and ExitFlag2 == 0 and ExitFlag3 == 0 and ExitFlag4 ==0 :
      command = "./"+headers.TftpImage['Image']
      devIntRetStruct = switch.DeviceInteract(connection=connection, command=command) 
      self.returnCode = devIntRetStruct.get('returnCode')
      self.returnDict['ImageRun'] = devIntRetStruct.get('buffer')
      if self.returnCode != 0:
       common.LogOutput('error', "Failed to  run the image executable file")
       ExitFlag4 = 1
     #Reboot the switch again to install the image 
     common.LogOutput("info","Reboot the switch again to install the image::")
     connection = switch.Reboot(connection=connection)
     if connection:
       common.LogOutput("info","Switch rebooted for image upgrade")
     else :
       common.LogOutput("error","Switch not rebooted for image upgrade")
       self.returnDict = "None"
       self.returnCode = 1
       ExitFlag1 = 1   
 
     #Remove the TFTP uplink after rebooting the device to the new image
     returnJson = self.RemoveUplink(device=self.device) 
     returnCode = common.ReturnJSONGetCode(json=returnJson)
     if returnCode != 0:
        common.LogOutput('error', "Failed to remove TFTP uplink to device")
        return returnJson
 
     #Return results
     returnJson = common.ReturnJSONCreate(returnCode=self.returnCode, data=self.returnDict)
     return returnJson 
     
  def RemoveUplink(self,device): 
     common.LogOutput('info',"Removing the TFTP uplink")
     returnCode = RTL.UplinkPortRemove(device=device) 
     return returnCode
