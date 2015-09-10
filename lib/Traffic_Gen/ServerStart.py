#########################################################################################
# Name:        Traffic_Gen.ServerStart
#
# Namespace:   Traffic_Gen
#
# Author:      Diego Hurtado
#
# Purpose:     Library function to generate traffic using iperf.
#
# Params:         deviceObj - Workstation identifier
#                 protocol - UDP or TCP
#                 interval - Result reporting interval
#
# Returns:          returnCode :- status of command
##PROC-###################################################################################

import lib
import pexpect
import time

def ServerStart(** kwargs):
    #Params
    deviceObj = kwargs.get('deviceObj', None)
    port = kwargs.get('port', 5001)
    protocol = kwargs.get('protocol', 'TCP')
    interval = kwargs.get('interval', 1)
    
    #If device is not passed, we need error message
    if deviceObj is None:
        lib.LogOutput('error', "Need to pass device to configure")
        returnJson = lib.returnStruct(returnCode=1)
        return returnJson
    
    command = 'iperf -s -p ' + port
    command = ' -i ' + interval
    if protocol == 'UDP':
        command = command + ' -u'

    deviceObj.expectHndl.sendline(command)
    
    #Compile information to return
    bufferString = ""
    returnCls = lib.returnStruct(returnCode=0)
    return returnCls
