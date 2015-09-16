##########################################################################
# Name:        opstestfw.host.hostIperfClientStart
#
# Namespace:   host
#
# Author:      Diego Hurtado
#
# Purpose:     Library function to generate traffic using iperf.
#
# Params:         deviceObj - Workstation identifier
#                 serverIP - server IP address
#                 time - amount of time in seconds where traffic will be sent
#                 protocol - UDP or TCP
#                 interval - Result reporting interval
#                 port - server port number
#
# Returns:          returnCode :- status of command
##PROC-###################################################################

import opstestfw
import pexpect


def hostIperfClientStart(** kwargs):
    # Params
    deviceObj = kwargs.get('deviceObj', None)
    port = kwargs.get('port', 5001)
    serverIP = kwargs.get('serverIP', None)
    protocol = kwargs.get('protocol', 'TCP')
    interval = kwargs.get('interval', 1)
    time = kwargs.get('time', 10)
    # Variables
    bufferString = ''

    # If device is not passed, we need error message
    if deviceObj is None or serverIP is None:
        opstestfw.LogOutput(
            'error', "Need to pass device to configure and server IP address.")
        returnStruct = opstestfw.returnStruct(returnCode=1)
        return returnStruct

    # Verify if iperf is installed on host assuming it is Ubuntu and then
    # install it
    command = 'iperf'
    opstestfw.LogOutput(
        'debug', "Verifying if iperf is installed on device " +
        deviceObj.device)
    deviceObj.expectHndl.sendline(command)
    index = deviceObj.expectHndl.expect(
        ['Usage', '(command not found)|(install)'])
    bufferString += str(deviceObj.expectHndl.before)
    if index == 0:
        # In case iperf is installed
        index = deviceObj.expectHndl.expect(['# ', pexpect.TIMEOUT], timeout=5)
        bufferString += str(deviceObj.expectHndl.before)
        if index == 1:
            opstestfw.LogOutput(
                'error', "Error while verifying status of iperf on device " +
                deviceObj.device)
            return opstestfw.returnStruct(returnCode=1, buffer=bufferString)
    else:
        # In case iperf is not installed
        index = deviceObj.expectHndl.expect(['# ', pexpect.TIMEOUT], timeout=5)
        bufferString += str(deviceObj.expectHndl.before)
        if index == 1:
            opstestfw.LogOutput(
                'error', "Error while verifying status of iperf on device " +
                deviceObj.device)
            return opstestfw.returnStruct(returnCode=1, buffer=bufferString)
        opstestfw.LogOutput('debug', "Installing iperf")
        command = 'apt-get install iperf'
        deviceObj.expectHndl.sendline(command)
        index = deviceObj.expectHndl.expect(
            ['# ', pexpect.TIMEOUT], timeout=30)
        bufferString += str(deviceObj.expectHndl.before)
        if index == 1:
            opstestfw.LogOutput(
                'error', "Error while installing iperf on device " +
                deviceObj.device)
            return opstestfw.returnStruct(returnCode=1, buffer=bufferString)
        command = 'iperf'
        deviceObj.expectHndl.sendline(command)
        index = deviceObj.expectHndl.expect(
            ['Usage', '(command not found)|(install)', pexpect.TIMEOUT])
        bufferString += str(deviceObj.expectHndl.before)
        if index != 0:
            opstestfw.LogOutput('error', "Could not install iperf correctly")
            index = deviceObj.expectHndl.expect(
                ['# ', pexpect.TIMEOUT], timeout=5)
            bufferString += str(deviceObj.expectHndl.before)
            if index != 0:
                opstestfw.LogOutput('error', "Unknown error on device")
                return opstestfw.returnStruct(returnCode=1,
                                              buffer=bufferString)
        else:
            index = deviceObj.expectHndl.expect(
                ['# ', pexpect.TIMEOUT], timeout=5)
            bufferString += str(deviceObj.expectHndl.before)
            if index != 0:
                opstestfw.LogOutput('error', "Unknown error on device")
                return opstestfw.returnStruct(returnCode=1,
                                              buffer=bufferString)
        opstestfw.LogOutput('debug', "Successfully installed iperf on device")

    command = 'iperf -c ' + str(serverIP) + ' -p ' + str(port)
    command += ' -i ' + str(interval)
    command += ' -t ' + str(time)
    if protocol == 'UDP':
        command += ' -u'

    deviceObj.expectHndl.sendline(command)

    # Compile information to return
    bufferString = ""
    returnCls = opstestfw.returnStruct(returnCode=0, buffer=bufferString)
    return returnCls
