#########################################################################################
# Name:        Traffic_Gen.ClientStop
#
# Namespace:   Traffic_Gen
#
# Author:      Diego Hurtado 
#
# Purpose:     Library function to stop and collect data after transmitting traffic using iperf
#
# Params:         deviceObj - Workstation identifier
#
# Returns:          returnCode :- status of command
#                   data: - Dictionary:
#                               'Client IP': Server IP address
#                               'Client port': Client port
#                               'Server IP': Server IP address
#                               'Server port': Server port
#                   buffer: - Raw output
##PROC-###################################################################################

import lib
import pexpect
import time
import re

def ClientStop(** kwargs):
    #Params
    deviceObj = kwargs.get('deviceObj', None)
    
    #If device is not passed, we need error message
    if deviceObj is None:
        lib.LogOutput('error', "Need to pass device to configure")
        returnStruct = lib.returnStruct(returnCode=1)
        return returnStruct
    
    deviceObj.expectHndl.expect(['\$', pexpect.TIMEOUT], timeout=1)

    ips_and_ports = re.search('local (.*) port (\d+) connected with (.*) port (\d+)', deviceObj.expectHndl.before)

    traffic_data = re.findall('sec  ([.\d]+ .*?)  ([.\d]+ .+)\r', deviceObj.expectHndl.before)

    # If client fails result is None and returnList == []

    server_ip = None
    server_port = None
    client_ip = None
    client_port = None

    if ips_and_ports is not None:
        server_ip = ips_and_ports.group(1)
        server_port = ips_and_ports.group(2)
        client_ip = ips_and_ports.group(3)
        client_port = ips_and_ports.group(4)

    data_dict = {}

    data_dict['Server IP'] = server_ip
    data_dict['Server port'] = server_port
    data_dict['Client IP'] = client_ip
    data_dict['Client port'] = client_port
    data_dict['Traffic data'] = traffic_data

    command = r'\003'
    deviceObj.expectHndl.send(command)
    deviceObj.expectHndl.expect('#')

    #Compile information to return
    returnCls = lib.returnStruct(returnCode=0, buffer=deviceObj.expectHndl.before, data=data_dict)
    return returnCls
