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
    
    #If device is not passed, we need error message
    if deviceObj is None:
        opstestfw.LogOutput('error', "Need to pass device to configure")
        returnJson = opstestfw.returnStruct(returnCode=1)
        return returnJson
    
    command = 'iperf -s -p ' + str(port)
    command += ' -i ' + str(interval)
    if protocol == 'UDP':
        command += ' -u'

    deviceObj.expectHndl.sendline(command)
    
    #Compile information to return
    bufferString = ""
    returnCls = opstestfw.returnStruct(returnCode=0)
    return returnCls
