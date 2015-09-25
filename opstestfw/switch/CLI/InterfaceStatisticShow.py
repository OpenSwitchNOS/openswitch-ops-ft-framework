##########################################################################
# Name:        switch.CLI.interface.InterfaceStatisticsShow
#
# Namespace:   switch.CLI.interface
#
# Author:      Randall Loaiza
#
# Purpose:     Library function get statistics for an specific interface
#
# Params:      deviceObj - device object
#              interface - interface number context
# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data:
#			   {RX:{inputPackets,inputErrors,shortFrame,CRC_FCS,bytes,dropped,overrun}
#				TX:{outputPackets,inputError,collision,bytes,dropped}}
#
##PROC-###################################################################

import opstestfw
import re
import time


def InterfaceStatisticsShow(**kwargs):

    # Params

    deviceObj = kwargs.get('deviceObj', None)
    interface = kwargs.get('inteface', None)

    # Variables
    overallBuffer = []
    data = dict()
    bufferString = ""
    command = ""
    returnCode = 0

    # Dictionary initialization
    data['RX'] = []
    data['TX'] = []

    if deviceObj is None:
        opstestfw.LogOutput('error', "Need to pass switch deviceObj to this routine")
        returnCls = opstestfw.returnStruct(returnCode=1)
        return returnCls

    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        opstestfw.LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = opstestfw.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    ###########################################################################
    # Send Command
    ###########################################################################
    command = "show interface"
    if interface != None:
        command += " " + str(interface)
    opstestfw.LogOutput('info', "Show interface statistics.*****" + command)
    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    temporaryBuffer = returnDevInt['buffer']

    if retCode != 0:
        opstestfw.LogOutput('error', "Failed to get information ." + command)

    ###########################################################################
    # Get out of the Shell
    ###########################################################################
    # Get out of vtyshell
    returnStructure = deviceObj.VtyshShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        opstestfw.LogOutput('error', "Failed to exit vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = opstestfw.returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    ###########################################################################
    # End Return Command
    ###########################################################################

    ###########################################################################
    # Return The Dict responds
    ###########################################################################

    for curLine in overallBuffer:
        bufferString += str(curLine)
    bufferSplit = bufferString.split("\r\n")

    rx = dict()
    tx = dict()
    rxExpress = "RX*\n\s*(\d*)\s*input packets\s*(\d*) bytes\s*\n\s*(\d*)\s*input error\s*(\d*)\s*dropped\s*\n\s*(\d*)\s*short frame\s*(\d*)\s*overrun\s*\n\s*(\d*)\s*CRC/FCS"
    txExpress = "TX*\n\s*(\d*)\s*output packets\s*(\d*)\s*bytes\s*\n\s*(\d*)\s*input error\s*(\d*)\s*dropped\s*\n\s*(\d*)\s*collision"

    # Filling up the dictionaries

    rxTokens = re.match(rxExpress, bufferString)
    txTokens = re.match(txExpress, bufferString)
    if rxTokens:
        rx['inputPackets'] = rxTokens.group(1)
        rx['bytes'] = rxTokens.group(2)
        rx['inputErrors'] = rxTokens.group(3)
        rx['dropped'] = rxTokens.group(4)
        rx['shortFrame'] = rxTokens.group(5)
        rx['overrun'] = rxTokens.group(6)
        rx['CRC_FCS'] = rxTokens.group(7)
    else:
        returnCode = 1
        opstestfw.LogOutput('error', "Failed to get information ." + command)

    if txTokens:
        rx['outputPackets'] = txTokens.group(1)
        rx['bytes'] = txTokens.group(2)
        rx['inputErrors'] = txTokens.group(3)
        rx['dropped'] = txTokens.group(4)
        rx['collision'] = txTokens.group(5)
    else:
        returnCode = 1
        opstestfw.LogOutput('error', "Failed to get information ." + command)

    # Return results
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = opstestfw.returnStruct(
        returnCode=returnCode, buffer=bufferString, data=data)
    return returnCls
