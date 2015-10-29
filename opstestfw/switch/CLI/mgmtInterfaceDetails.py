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


def mgmtInterfaceGetDetails(**kwargs):
    """
    Library function to show management interface details in CLI/Kernel
    :param deviceObj	: Device object
    :param mode		: CLI or Kernel
    :type mode		: string
    :return: returnStruct Object
    :returnType: object
    """

    deviceObj = kwargs.get('deviceObj')
    mode = kwargs.get('mode', 'CLI')
    ipv6 = kwargs.get('ipv6', False)

    overallBuffer = []
    # If Device object is not passed, we need to error out
    if deviceObj is None:
        LogOutput('error', "Need to pass switch device object to this routine")
        returnCls = returnStruct(returnCode=1)
        return returnCls

    paramError = 0

    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls

    if mode is "CLI":
        # Pass show commands here
        command = "show interface mgmt"
        returnStructure = deviceObj.DeviceInteract(command=command)
        retCode = returnStructure['returnCode']
        overallBuffer.append(returnStructure['buffer'])

    else:

        # Pass show commands here
        command = "start-shell"
        returnStructure = deviceObj.DeviceInteract(command=command)
        retCode = returnStructure['returnCode']
        overallBuffer.append(returnStructure['buffer'])

        if ipv6 is True:
            command = "/sbin/ip -6 route show dev eth0"
        else:
            command = "ifconfig eth0"
        returnStructure = deviceObj.DeviceInteract(command=command)
        retCode = returnStructure['returnCode']
        overallBuffer.append(returnStructure['buffer'])
        command = " exit \r"

    # Exit the vtysh shell
    returnStructure = deviceObj.VtyshShell(configOption="unconfig")
    returnCode = returnStructure.returnCode()
    if returnCode != 0:
        LogOutput('error', "Failed to exit vtysh prompt")
    returnCls = returnStruct(returnCode=returnCode,)
    return returnCls

    # Return results
   # Return results
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = returnStruct(returnCode=0, buffer=bufferString)
    return returnCls
