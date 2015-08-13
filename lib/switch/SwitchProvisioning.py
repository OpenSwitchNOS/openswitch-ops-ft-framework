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
import headers
import common
import time
import switch
#import topology
import os
import re

def SwitchProvisioning(**kwargs):
     returnDict = dict()
     common.LogOutput("info","PROVISIONING HALON Physical device")
     common.LogOutput("info","Enter the Onie rescue mode for provisioning the physical device")
     connection = kwargs.get('connection')
     if headers.TftpImage['ImageURL'] is None :
       common.LogOutput("error","TFTP image URL not specified **Exiting the provisioning module")
       returnJson = common.ReturnJSONCreate(returnCode=1, data=None)
       return returnJson

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
         common.LogOutput("error","Wget the tftp file --> "+headers.TftpImage['Image']+" to /warp/pub unsuccessful.Image not downloaded")
         returnJson = common.ReturnJSONCreate(returnCode=1, data=returnDict)
        else :
         common.LogOutput("debug","Wget the tftp file --> "+headers.TftpImage['Image']+" to /warp/pub successful")
      else :
        common.LogOutput("info",headers.TftpImage['Image']+"-->Image exists in /warp/pub")
     else :
      common.LogOutput("error","Cannot find any image file in the archive specified")
      returnJson = common.ReturnJSONCreate(returnCode=1, data=returnDict)
       
     #Instantiate the class TftpImageOnieDownload to initiate TFTP transfer of image from RTL uplink
     #This code can be extended to upload multiple targets with images from TFTP

     TftpInstance = switch.TftpImageOnieDownload(headers.topo['dut01']) 
     if TftpInstance.AddUplink != 1:
       common.LogOutput("info","Starting TFTP upload**")
       returnJson = TftpInstance.TftpOperation(connection=connection)
     else:
       common.LogOutput("error","Failed to add uplink to topology")
       returnJson = common.ReturnJSONCreate(returnCode=1, data=returnDict)
  
     #Return Results in JSON
     return returnJson



