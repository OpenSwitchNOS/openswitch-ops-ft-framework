#########################################################################################
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
##PROC-###################################################################################
import opstestfw
import pexpect
import time

def hostIperfClientStart(** kwargs):
    #Params
    deviceObj = kwargs.get('deviceObj', None)
    port = kwargs.get('port', 5001)
    serverIP = kwargs.get('serverIP', None)
    protocol = kwargs.get('protocol', 'TCP')
    interval = kwargs.get('interval', 1)
    time = kwargs.get('time', 10)
    
    #If device is not passed, we need error message
    if deviceObj is None or serverIP is None:
        opstestfw.LogOutput('error', "Need to pass device to configure and server IP address.")
        returnStruct = opstestfw.returnStruct(returnCode=1)
        return returnStruct
    
    command = 'iperf -c ' + str(serverIP) + ' -p ' + str(port)
    command += ' -i ' + str(interval)
    command += ' -t ' + str(time)
    if protocol == 'UDP':
        command += ' -u'

    deviceObj.expectHndl.sendline(command)
    
    #Compile information to return
    bufferString = ""
    returnCls = opstestfw.returnStruct(returnCode=0)
    return returnCls
