#########################################################################################
# Name:        opstestfw.host.hostIperfServerStart
#
# Namespace:   host
#
# Author:      Diego Hurtado
#
# Purpose:     Library function to receive traffic using iperf.
#
# Params:         deviceObj - Workstation identifier
#                 port     - Port number to listen
#                 protocol - UDP or TCP
#                 interval - Result reporting interval
#
# Returns:          returnCode :- status of command
##PROC-###################################################################################

import opstestfw
import pexpect
import time

def hostIperfServerStart(** kwargs):
    #Params
    deviceObj = kwargs.get('deviceObj', None)
    port = kwargs.get('port', 5001)
    protocol = kwargs.get('protocol', 'TCP')
    interval = kwargs.get('interval', 1)
    #Variables
    bufferString = ''
    
    #If device is not passed, we need error message
    if deviceObj is None:
        opstestfw.LogOutput('error', "Need to pass device to configure")
        returnJson = opstestfw.returnStruct(returnCode=1)
        return returnJson
    
    #Verify if iperf is installed on host assuming it is Ubuntu and then install it
    command='iperf'
    opstestfw.LogOutput('debug', "Verifying if iperf is installed on device " + deviceObj.device)
    deviceObj.expectHndl.sendline(command)
    index = deviceObj.expectHndl.expect(['Usage','command not found'])
    bufferString += str(deviceObj.expectHndl.before)
    if index == 0:
        #In case iperf is installed
        index = deviceObj.expectHndl.expect(['# ',pexpect.TIMEOUT],timeout=5)
        bufferString += str(deviceObj.expectHndl.before)
        if index == 1:
            opstestfw.LogOutput('error', "Error while verifying status of iperf on device " + deviceObj.device)
            return opstestfw.returnStruct(returnCode=1, buffer=bufferString)
    else:
        #In case iperf is not installed
        index = deviceObj.expectHndl.expect(['# ',pexpect.TIMEOUT],timeout=5)
        bufferString += str(deviceObj.expectHndl.before)
        if index == 1:
            opstestfw.LogOutput('error', "Error while verifying status of iperf on device " + deviceObj.device)
            return opstestfw.returnStruct(returnCode=1, buffer=bufferString)
        opstestfw.LogOutput('debug', "Installing iperf")
        command = 'apt-get install'
        index = deviceObj.expectHndl.expect(['# ',pexpect.TIMEOUT],timeout=30)
        bufferString += str(deviceObj.expectHndl.before)
        if index == 1:
            opstestfw.LogOutput('error', "Error while installing iperf on device " + deviceObj.device)
            return opstestfw.returnStruct(returnCode=1, buffer=bufferString)
        index = deviceObj.expectHndl.expect(['Usage','command not found',pexpect.Timeout],timeout=5)
        bufferString += str(deviceObj.expectHndl.before)
        if index != 0:
            opstestfw.LogOutput('error', "Could not install iperf correctly")
            index = deviceObj.expectHndl.expect(['# ',pexpect.TIMEOUT],timeout=5)
            bufferString += str(deviceObj.expectHndl.before)
            if index != 0:
                opstestfw.LogOutput('error', "Unknown error on device")
                return opstestfw.returnStruct(returnCode=1, buffer=bufferString)
        else:
            index = deviceObj.expectHndl.expect(['# ',pexpect.TIMEOUT],timeout=5)
            bufferString += str(deviceObj.expectHndl.before)
            if index != 0:
                opstestfw.LogOutput('error', "Unknown error on device")
                return opstestfw.returnStruct(returnCode=1, buffer=bufferString)
        opstestfw.LogOutput('debug', "Successfully installed iperf on device")
    
    command = 'iperf -s -p ' + str(port)
    command += ' -i ' + str(interval)
    if protocol == 'UDP':
        command += ' -u'

    deviceObj.expectHndl.sendline(command)
    
    #Compile information to return
    bufferString = ""
    returnCls = opstestfw.returnStruct(returnCode=0, buffer=bufferString)
    return returnCls
