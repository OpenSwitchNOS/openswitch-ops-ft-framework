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
import opstestfw


def hostIperfClientStart(** kwargs):

    """
    Library function to generate traffic using iperf.

    :param deviceObj : Device object
    :type  deviceObj : object
    :param time    : amount of time in seconds where traffic will be sent
    :type  time    : integer
    :param protocol : UDP or TCP
    :type protocol  : string
    :param interval : Result reporting interval
    :type interval  : integer
    :param port   : server port number
    :type port    : integer

    :return: returnStruct Object
    :returnType: object
    """
    # Params
    deviceObj = kwargs.get('deviceObj', None)
    port = kwargs.get('port', 5001)
    serverIP = kwargs.get('serverIP', None)
    protocol = kwargs.get('protocol', 'TCP')
    interval = kwargs.get('interval', 1)
    rtime = kwargs.get('time', 10)

    # If device is not passed, we need error message
    if deviceObj is None or serverIP is None:
        opstestfw.LogOutput('error',
                            "Need to pass device to configure and server "
                            "IP address.")
        returnStruct = opstestfw.returnStruct(returnCode=1)
        return returnStruct

    command = 'iperf -c ' + str(serverIP) + ' -p ' + str(port)
    command = ' -i ' + str(interval)
    command = ' -t' + str(rtime)
    if protocol == 'UDP':
        command = command + ' -u'

    deviceObj.expectHndl.sendline(command)

    # Compile information to return
    returnCls = opstestfw.returnStruct(returnCode=0)
    return returnCls
