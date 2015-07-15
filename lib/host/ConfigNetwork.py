###PROC+#####################################################################
# Name:        host.ConfigNetwork
#
# Namespace:   host
#
# Author:      Srinivasa Krishnappa
#
# Purpose:     Library to configure host network IP
#
# Params:      connection - pexpect connection handle for host
#	       eth        - host eth interface to be configured for IP addr	
#              ipAddr     - ipAddr to be configured
#              netMask    - netmask to be configured
#              gateway    - gateway or broadcast to be configured
#	       clear      - clear the configured ip address by default it is False
# Returns:     
#              returnCode = 0 for pass, 1 for fail
#              
#
##PROC-#####################################################################

import headers
import common
import host
import re



LIST_ETH_INTERFACES_CMD ="ifconfig -a | grep Ethernet"
LIST_INTERFACE_IP_CMD ="ifconfig %s | grep inet"
ENABLE_ETH_INTERFACE_CMD ="ifconfig %s up"
ETH_INTERFACE_CFGIP_CMD ="ifconfig %s %s netmask %s broadcast %s"
ETH_INTERFACE_CFGIP_CLEAR_CMD ="ifconfig %s 0.0.0.0"

FAILED = 1
PASSED = 0

def ConfigNetwork(**kwargs):
  
   connection = kwargs.get('connection')
   eth = kwargs.get('eth')
   ipAddr = kwargs.get('ipAddr')
   netMask = kwargs.get('netMask')
   gateway = kwargs.get('gateway')
   clear = kwargs.get('clear',False)

   # Local variables
   bailflag = 0
   interfaceUpOption = 0
   returnCode = PASSED 
  
   retStruct = dict()
   retStruct['returnCode'] = FAILED
   retStruct['buffer'] = []

   if ipFormatChk(ipAddr) == False:
        common.LogOutput('error', "invalid ipaddress format :"+ipAddr)
	returnCode = FAILED
   	retStruct['buffer'] = "Invalid ip address passed"
   elif ipFormatChk(netMask) == False:
        common.LogOutput('error', "invalid netmask format :"+netMask)
	returnCode = FAILED
   	retStruct['buffer'] = "Invalid net mask passed"
   elif ipFormatChk(gateway) == False:
        common.LogOutput('error', "invalid gateway format :"+gateway)
	returnCode = FAILED
   	retStruct['buffer'] = "Invalid gateway passed"

   if returnCode:
        retStruct['returnCode'] = returnCode
	return retStruct 		

   while bailflag == 0: 
   # Send the command
   	retStruct = host.DeviceInteract(connection=connection, command=LIST_ETH_INTERFACES_CMD)
	retCode = retStruct.get('returnCode')
  	retBuff = retStruct.get('buffer')
	if retCode != 0:
   		common.LogOutput('error', "Failed to execute the command : " + LIST_ETH_INTERFACES_CMD)
        	bailflag = 1
                returnCode = FAILED
   		retStruct['buffer'] = "Failed to execute the command : " + LIST_ETH_INTERFACES_CMD
               
   	else:
        	common.LogOutput('info', "Successfully executed the command : " + LIST_ETH_INTERFACES_CMD)
   		if retBuff.find(eth)<> -1:
	        	common.LogOutput('info', "eth interface is validated for : " + eth)
			bailflag = 1
   		else:
        		common.LogOutput('info', "eth interface failed to validate for : " + eth)
   			retStruct['buffer'] = "eth interface failed to validate for : " + eth
			if interfaceUpOption:
				bailflag = 1
                                returnCode = FAILED
				break
			interfaceUpOption = 1
   			command = ENABLE_ETH_INTERFACE_CMD %eth 
			retStruct = host.DeviceInteract(connection=connection, command=command)
   			retCode = retStruct.get('returnCode')
			retBuff = retStruct.get('buffer')
			if retCode != 0:
			   	common.LogOutput('error', "Failed to execute the command : " + command)
        			bailflag = 1
                                returnCode = FAILED
   				retStruct['buffer'] = "Failed to execute the command : " + command
   			else:
        			common.LogOutput('info', "Successfully executed the command : " + command)


   if returnCode:
        retStruct['returnCode'] = returnCode
	return retStruct 		
	
   if clear:

   	command = ETH_INTERFACE_CFGIP_CLEAR_CMD %eth
   	returnStruct = host.DeviceInteract(connection=connection, command=command)
   	retCode = returnStruct.get('returnCode')
   	retBuff = returnStruct.get('buffer')
   	if retCode != 0:
       		common.LogOutput('error', "Failed to execute the command : " + command)
                returnCode = FAILED
   		retStruct['buffer'] = "Failed to execute the command : " + command
   	else:
       		common.LogOutput('info', "Successfully executed the command : " + command)

   else:

   	command = ETH_INTERFACE_CFGIP_CMD %(eth,ipAddr,netMask,gateway)
   	returnStruct = host.DeviceInteract(connection=connection, command=command)
   	retCode = returnStruct.get('returnCode')
   	retBuff = returnStruct.get('buffer')
   	if retCode != 0:
       		common.LogOutput('error', "Failed to execute the command : " + command)
                returnCode = FAILED
   		retStruct['buffer'] = "Failed to execute the command : " + command
  	else:
       		common.LogOutput('info', "Successfully executed the command : " + command)

        if returnCode != FAILED:
		command = LIST_INTERFACE_IP_CMD %(eth)
   		retStruct = host.DeviceInteract(connection=connection, command=command)
	   	retCode = retStruct.get('returnCode')
	   	retBuff = retStruct.get('buffer')
   		if retCode != 0:
       			common.LogOutput('error', "Failed to execute the command : " + command)
                	returnCode = FAILED
   			retStruct['buffer'] = "Failed to execute the command : " + command
   		else:
       			common.LogOutput('info', "Successfully executed the command : " + command)
   	
		if retBuff.find(ipAddr) == -1:
       			common.LogOutput('error', "IP addr %s is not configured successfully on interface %s : "%(ipAddr,eth))
   			retStruct['buffer'] = "Failed to execute the command : " + command
  	 	else:
       			common.LogOutput('info', "IP addr %s configured successfully on interface %s : "%(ipAddr,eth))

   retStruct['returnCode'] = returnCode
   return retStruct 		


def ipFormatChk(ip_str):
    pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    if re.match(pattern, ip_str):
       return True
    else:
       return False

