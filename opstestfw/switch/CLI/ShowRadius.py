# (C) Copyright 2015 Hewlett Packard Enterprise Development LP
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
import opstestfw.switch
from opstestfw import *
import re
import time
import pdb


def ShowRadius(**kwargs):
    deviceObj = kwargs.get('deviceObj')
    # if connection is None:
    #    return False

    returnDict = dict()
    overallBuffer = []
    returnStructure = deviceObj.VtyshShell()
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    # Pass Radius commands here
    command = "show radius-server"
    LogOutput("info", "show radius command ***" + command)
    devIntRetStruct = deviceObj.DeviceInteract(command=command)
    returnCode = devIntRetStruct.get('returnCode')
    overallBuffer.append(devIntRetStruct.get('buffer'))
    if returnCode != 0:
        LogOutput('error', "Failed to get show radius config command")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls
    else:
        rawBuffer = devIntRetStruct.get('buffer')
        bufferSplit = rawBuffer.split("\r\n")

        print rawBuffer

#
#        globalStatsDict = dict()
#        portDict = dict()
#
#            for line in bufferSplit:
#                portLine = re.match("^Port\s+:\s*(\d+)\s*$", line)
#                if portLine:
#                    curPort = portLine.group(1)
#                    portDict[curPort] = curport

        # pdb.set_trace()

    # Exit the vtysh shell
    # returnStructure = opstestfw.switch.CLI.VtyshShell(connection =
    # connection,configOption="unconfig")
    returnStructure = deviceObj.VtyshShell(configOption="unconfig")
    returnCode = returnStructure.returnCode()
    if returnCode != 0:
        LogOutput('error', "Failed to exit vtysh prompt")
        returnCls = returnStruct(returnCode=returnCode,)
        return returnCls

    # Return results
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = returnStruct(
        returnCode=0,
        buffer=bufferString,
        data=returnDict)
    return returnCls
