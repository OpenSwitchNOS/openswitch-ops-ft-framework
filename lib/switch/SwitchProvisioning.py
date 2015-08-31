###PROC+#####################################################################
# Name:        switch.SwitchProvisioning
#
# Namespace:   switch
#
# Author:      Payal Upadhyaya 
#
# Purpose:     Provision the physical DUT with image from tftp server in RTL
#              Repository Location:/warp/pub
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


import time
import switch
#import topology
import os
import re
from lib import *

def SwitchProvisioning(**kwargs):
     #returnDict = dict()
     LogOutput("info","PROVISIONING HALON Physical device")
     LogOutput("info","Enter the Onie rescue mode for provisioning the physical device")
     connection = kwargs.get('connection')
     if headers.TftpImage['ImageURL'] is None :
       LogOutput("error","TFTP image URL not specified **Exiting the provisioning module")
       returnCls = returnStruct(returnCode=1)
       return returnCls

     #Wget the tftp file to /warp/pub (if the file does not exist in the repository)
     #Getting the image name from the archive specified
     #Example archive:
     #remote = "http://archive.hpnos.io/artifacts/0.1.0+2015070518/as5712/onie-installer-x86_64-as5712_54x-0.1.0+2015070518"
     remote = headers.TftpImage['ImageURL']
     image = re.match(r'.*(onie-installer-x86_64.*)',remote)
     headers.TftpImage['Image'] = image.group(1)
     if image:
      if not os.path.exists("/warp/pub/"+headers.TftpImage['Image']):
        returnCode = os.system('wget '+remote+' -P /warp/pub')
        if returnCode != 0:
         LogOutput("error","Wget the tftp file --> "+headers.TftpImage['Image']+" to /warp/pub unsuccessful.Image not downloaded")
         returnCls = returnStruct(returnCode=1, data=returnDict)
        else :
         LogOutput("debug","Wget the tftp file --> "+headers.TftpImage['Image']+" to /warp/pub successful")
      else :
        LogOutput("info",headers.TftpImage['Image']+"-->Image exists in /warp/pub")
     else :
      LogOutput("error","Cannot find any image file in the archive specified")
      returnCls = returnStruct(returnCode=1)
       
     #Instantiate the class TftpImageOnieDownload to initiate TFTP transfer of image from RTL uplink
     #This code can be extended to upload multiple targets with images from TFTP

     TftpInstance = switch.TftpImageOnieDownload(headers.topo['dut01']) 
     if TftpInstance.AddUplink != 1:
       LogOutput("info","Starting TFTP upload**")
       returnCls = TftpInstance.TftpOperation(connection=connection)
     else:
       LogOutput("error","Failed to add uplink to topology")
       returnCls = returnStruct(returnCode=1)
  
     #Return Results in JSON
     return returnCls



