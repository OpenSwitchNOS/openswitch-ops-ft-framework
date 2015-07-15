##########################################################################################
# This is an example template to write show <feature> libraries 
# Name:        switch.CLI.<name>
#
# Namespace:   switch.CLI
#
# Author:      Payal Upadhyaya 
#
# Purpose:     Run the show commands in vtysh shell
#
# Params:      connection - device connection
#                     port  - Ethernet port
#                     (Add more parameters)
#
# Returns:     JSON structure
#                   returnCode :- status of command(0 for pass , gets errorcodes for failure)
#                   data: -            Dictionary as per manipulated expect data
#                                         rawBuffer(Device buffer)
#
##PROC-###################################################################################
#import required packages 
import common
import switch
import re
import time

def <name>(**kwargs):
    #Add more parameters you want to pass to the device here
    connection = kwargs.get('connection')
    port = kwargs.get('port')

    if connection is None:
       return False

    returnDict = dict()
    #Enter the vtysh shell to access LLDP commands
    returnStructure = switch.CLI.VtyshShell(connection = connection)
    vtyshInfo = common.ReturnJSONGetData(json=returnStructure, dataElement='vtyshPrompt')
    common.LogOutput("debug","vtysh shell buffer: \n"+vtyshInfo)
    returnCode = common.ReturnJSONGetCode(json = returnStructure)
    if returnCode != 0:
       common.LogOutput('error', "Failed to get vtysh prompt")
       returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=returnStructure)
       return returnJson

    #Pass show command here as the eg below
    command = "show lldp neighbor-info %d"%(port)
    common.LogOutput("info","Show command  ***"+command)
    devIntRetStruct = switch.DeviceInteract(connection=connection, command=command)
    returnCode = devIntRetStruct.get('returnCode')
    if returnCode != 0:
       common.LogOutput('error', "Failed to get show command")
       returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=devIntRetStruct)
       return returnJson
    else :
       rawBuffer = devIntRetStruct.get('buffer')
       bufferSplit  = rawBuffer.split("\r\n")
       #<Manipulate the expect buffer here to generate dynamic dictionary keys using regular expressions>
       #<Dump the dynamic key value pairs in the dictionary --- returnDict which will be used to create JSON output
       returnDict['rawBuffer'] = rawBuffer

    #Exit the vtysh shell 
    returnStructure = switch.CLI.VtyshShell(connection = connection,configOption="unconfig")
    vtyshExitInfo = common.ReturnJSONGetData(json=returnStructure, dataElement='vtyshPrompt')
    common.LogOutput("debug","vtysh shell buffer: \n"+vtyshExitInfo) 
    returnCode = common.ReturnJSONGetCode(json = returnStructure)
    if returnCode != 0:
       common.LogOutput('error', "Failed to exit vtysh prompt")
       returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=returnStructure)
       return returnJson

    #Return results(makes a json structure of the dictionary(returnDict) and return code)
    returnJson = common.ReturnJSONCreate(returnCode=0, data=returnDict)
    return returnJson
    
