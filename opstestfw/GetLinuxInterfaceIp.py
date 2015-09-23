##########################################################################
# Name:        opstestfw.GetLinuxInterfaceIp
#
# Namespace:   opstestfw
#
# Author:      Srinivasa Krishnappa
#
# Purpose:     Library function to get the IP address on an eth0 interface
#
# Params:      deviceObj - device object
#
# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data:
#
##PROC-###################################################################
from opstestfw import *
import re
import time


def GetLinuxInterfaceIp(**kwargs):
    deviceObj = kwargs.get('deviceObj', None)
    returnCode = 0
    ipAddr = None
    overallBuffer = []
    # If Device object is not passed, we need to error out
    if deviceObj is None:
        LogOutput('error', "Pass switch/wrkstn device object to this routine")
        returnCls = returnStruct(returnCode=1)
        return returnCls

    # Get the interface ip
    command = "ifconfig eth0 | grep 'inet addr'"
    returnStructure = deviceObj.DeviceInteract(command=command)
    retCode = returnStructure['returnCode']
    buf = returnStructure['buffer']

    overallBuffer.append(buf)
    if retCode != 0:
        LogOutput(
            'error',
            "Failed to ifconfig on eth0 interface for the device")
        returnCode = 1
    else:
        LogOutput(
            'info',
            "Success to ifconfig on eth0 interface for the device")
        print buf
        if buf.find("inet addr:") != -1:
            inetAddr = buf.split('\n')[1].split(' ')
            print inetAddr
            if len(inetAddr) > 10:
                ipAddr = inetAddr[11].split(':')[1]
        else:
            ipAddr="" 

    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = returnStruct(
        returnCode=returnCode,
        data=ipAddr,
        buffer=bufferString)
    return returnCls
