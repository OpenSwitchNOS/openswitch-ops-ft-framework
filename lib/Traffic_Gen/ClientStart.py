#########################################################################################
# Name:        Traffic_Gen.ClientStart
#
# Namespace:   Traffic_Gen
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
import lib
import pexpect
import time

def ClientStart(** kwargs):
    #Params
    deviceObj = kwargs.get('deviceObj', None)
    port = kwargs.get('port', 5001)
    serverIP = kwargs.get('serverIP', None)
    protocol = kwargs.get('protocol', 'TCP')
    interval = kwargs.get('interval', 1)
    time = kwargs.get('time', 10)
    
    #If device is not passed, we need error message
    if deviceObj is None or serverIP is None:
        lib.LogOutput('error', "Need to pass device to configure and server IP address.")
        returnStruct = lib.returnStruct(returnCode=1)
        return returnStruct
    
    command = 'iperf -c ' + serverIP + ' -p ' + port
    command = ' -i ' + interval
    command = ' -t' + time 
    if protocol == 'UDP':
        command = command + ' -u'

    deviceObj.expectHndl.sendline(command)
    
    #Compile information to return
    bufferString = ""
    returnCls = lib.returnStruct(returnCode=0)
    return returnCls
