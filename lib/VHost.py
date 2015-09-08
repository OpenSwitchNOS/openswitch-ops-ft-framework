import pexpect
from lib import gbldata

import switch
import time
#import console
import xml.etree.ElementTree
import os
import re
from Topology import Topology
from Device import Device
from VSwitch import VSwitch
import socket
#from lib import *
import lib
import paramiko
import json

# This is the base class for any device - This gives the test case developer the ability to connect to the device
# along with interacting with the device
class VHost ( Device ):
    def __init__(self, **kwargs):
        self.topology = kwargs.get('topology', None)
        self.device = kwargs.get('device', None)
        # Bring in Default member values
        self.defaultMembers()
        self.expectDefaultPrompts = ['login:\s*$',
                               'Password:',
                               '\[root@\S+.*\]#',
                               'root@\S+#',
                               '\(yes/no\)?',
                               pexpect.EOF,
                               pexpect.TIMEOUT]
        self.initExtMembers()
        self.Connect()
        self.CreateHostRestInfra()

    def defaultMembers(self):
        self.expectHndl = ""
        self.connectStringBase = "docker exec -ti "

    def initExtMembers(self):
        self.LIST_ETH_INTERFACES_CMD = 'ifconfig -a | grep Ethernet'
        self.LIST_INTERFACE_IP_CMD = 'ifconfig %s | grep inet'
        self.ENABLE_ETH_INTERFACE_CMD = 'ifconfig %s up'
        self.ETH_INTERFACE_CFGIP_CMD = 'ip addr add %s/%d dev %s'
        self.ETH_INTERFACE_CFGIP_IFCFG_CMD = 'ifconfig %s %s netmask %s broadcast %s'
        self.ETH_INTERFACE_CFGIP_CLEAR_CMD = 'ip addr del %s/%d dev %s'
        self.ETH_INTERFACE_CFGIP_IFCFG_CLEAR_CMD = 'ifconfig %s 0.0.0.0'
        self.fwbase = os.environ['FT_FRAMEWORK_BASE']

    def Connect(self):
        # Look up the device name in the topology - grab connectivity information
        xpathString = ".//device[name='" + self.device + "']"
        etreeElement = lib.XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
        if etreeElement == None:
            # We are not in a good situation, we need to bail
            lib.LogOutput('error', "Could not find device " + self.device + " in topology")
            return None
        # Code for virtual
        # Go and grab the connection name
        xpathString = ".//device[name='" + self.device + "']/connection/name"
        virtualConn = lib.XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
        if virtualConn == None:
            lib.LogOutput('error', "Failed to virtual connection for " + self.device )
            return None
        telnetString = self.connectStringBase + self.device + " /bin/bash"
        self.expectHndl = pexpect.spawn(telnetString,echo=False)
        #self.expectHndl.delaybeforesend = .5
        expectFileString  = self.device + ".log"
        
        # VINCE TODO - Move ExpectLog to Common Class
        ExpectInstance = lib.DeviceLogger(expectFileString)
        expectLogFile = ExpectInstance.OpenExpectLog(expectFileString)
        if expectLogFile == 1 :
            lib.LogOutput('error', "Unable to create expect log file")
            exit(1)
        #Opening an expect connection to the device with the specified log file
        lib.LogOutput('debug', "Opening an expect connection to the device with the specified log file"+expectFileString)
        self.expectHndl = pexpect.spawn(telnetString, echo=False, logfile=lib.DeviceLogger(expectLogFile))
        self.expectHndl.delaybeforesend = .05
        
        # Lets go and detect our connection - this will get us to a context we know about
        retVal = self.DetectConnection()
    
        if retVal is None:
            return None
        return self.expectHndl
    
    
    def DetectConnection(self):
        bailflag = 0

        self.expectHndl.send('\r')
        connectionBuffer = []
        sanitizedBuffer = ""
        while bailflag == 0:
            time.sleep(1)
            index = self.expectHndl.expect(self.expectDefaultPrompts, timeout=30)
            
            if index == 0:
                # Need to send login string
                connectionBuffer.append(self.expectHndl.before)
                self.expectHndl.send("root")
                self.expectHndl.send("\r")
                #connectionBuffer.append(self.expectHndl.before)
            elif index == 1:
                # Need to send password string
                connectionBuffer.append(self.expectHndl.before)
                self.expectHndl.send("procurve")
                self.expectHndl.send("\r")
                #connectionBuffer.append(self.expectHndl.before)
            elif index == 2:
                # Got prompt.  We should be good
                #print "Got prompt, we should be good"
                #print('Got prompt, we should be good')
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
            elif index == 3:
                # Got prompt.  We should be good
                #print "Got prompt, we should be good"
                #print('Got prompt, we should be good')
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
            elif index == 4:
                # Got yes / no prompt.  We should be good
                #print "Got prompt, we should be good"
                #print('Got prompt, we should be good')
                self.expectHndl.send("yes")
                self.expectHndl.send("\r")
                connectionBuffer.append(self.expectHndl.before)
            elif index == 5:
                # Got EOF
                lib.LogOutput('error', "Telnet to host failed")
                return None
            elif index == 6:
                # Got a Timeout
                lib.LogOutput('error', "Connection timed out")
                return None
            else :
                #print "Got index ", index, " wainting again"
                #print('Got index %d wainting again'.format(index))
                connectionBuffer.append(self.expectHndl.before)
        # Append on buffer after
        connectionBuffer.append(self.expectHndl.after)
        # Now lets put in the topology the expect handle
        self.expectHndl.expect(['$'], timeout=2)
        for curLine in connectionBuffer:
            #lib.LogOutput('debug', curLine)
            sanitizedBuffer += curLine
        lib.LogOutput('debug', sanitizedBuffer)

        return self.expectHndl
    
    
    def DeviceInteract(self, **kwargs):
        command = kwargs.get('command')
        yesPromptResp = kwargs.get('yesPrompt', "yes")
        errorCheck = kwargs.get('errorCheck', True)

        # Local variables
        bailflag = 0
        retStruct = dict()
        retStruct['returnCode'] = 1
        retStruct['buffer'] = []

        # Send the command
        self.expectHndl.send(command)
        self.expectHndl.send('\r')
        #time.sleep(1)
        connectionBuffer = []

        while bailflag == 0:
            #DEBUG print connection
            index = self.expectHndl.expect(self.expectDefaultPrompts, timeout=30)
            if index == 0:
                # Need to send login string
                self.expectHndl.send("root")
                self.expectHndl.send("\r")
                connectionBuffer.append(self.expectHndl.before)
            elif index == 1:
                # Need to send password string
                self.expectHndl.send("procurve")
                self.expectHndl.send("\r")
                connectionBuffer.append(self.expectHndl.before)
            elif index == 2:
                # Got prompt.  We should be good
                #print "Got prompt, we should be good"
                #print('Got prompt, we should be good')
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
            elif index == 3:
                # Got prompt.  We should be good
                #print "Got prompt, we should be good"
                #print('Got prompt, we should be good')
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
            elif index == 4:
                # Got yes / no prompt.  We should be good
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
                if yesPromptResp == "yes":
                    self.expectHndl.send("yes")
                else:
                    self.expectHndl.send("no")
                self.expectHndl.send("\r")
            elif index == 5:
                # got EOF
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
                lib.LogOutput('error', "reached EOF")
                returnCode = 1
            elif index == 6:
                # got Timeout
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
                lib.LogOutput('error', "command timeout")
                returnCode = 1
            else :
                tmpBuffer = self.expectHndl.before
                # Pull out the \r\n of the buffer
                tmpBuffer = re.sub('\r\r\n', '', tmpBuffer)
                print "tmpbuffer = " + tmpBuffer
                
                if tmpBuffer != command:
                    connectionBuffer.append(self.expectHndl.before)

        connectionBuffer.append(self.expectHndl.after)
        self.expectHndl.expect(['$'], timeout=1)
        santString = ""
        for curLine in connectionBuffer:#
            santString += str(curLine)

        returnCode = 0
        if errorCheck is True and returnCode == 0:
            errorCheckRetStruct = self.ErrorCheck(buffer=santString)
            returnCode = errorCheckRetStruct['returnCode']
        # Dump the buffer the the debug log
        lib.LogOutput('debug', "Sent and received from device: \n" + santString + "\n")

        # Return dictionary
        retStruct['returnCode'] = returnCode
        retStruct['buffer'] = santString

        return retStruct
    
    
    def ErrorCheck(self, **kwargs):
        buffer = kwargs.get('buffer')
        # Local variables
        returnCode = 0
        exitValue = 0
        retStruct = dict()
        retStruct['returnCode'] = returnCode

        # Set up the command for error check
        command = "echo $?"
        buffer = ""
        self.expectHndl.send(command)
        self.expectHndl.send('\r\n')
        #time.sleep(1)
        #index = self.expectHndl.expect(['root@\S+.*#'], timeout=200)
        index = self.expectHndl.expect(['\[root@.*\]#',
                                        'root@.*#',
                                        pexpect.EOF,
                                        pexpect.TIMEOUT], timeout=30)
        #index = self.expectHndl.expect(self.expectList, timeout=20)
        if index == 0 or index == 1:
            buffer += self.expectHndl.before
            buffer += self.expectHndl.after
        else:
            lib.LogOutput('error', "Received timeout in ErrorCheck " + str(index))
            retStruct['returnCode'] = 1
            return retStruct


        bufferSplit = buffer.split("\n")
        for curLine in bufferSplit:
            testforValue = re.match("(^[0-9]+)\s*$", curLine)
            if testforValue:
                # Means we got a match
                exitValue = int(testforValue.group(1))
            if exitValue != 0:
                returnCode = exitValue
            else:
                returnCode = 0
        retStruct['returnCode'] = returnCode
        return retStruct

    def NetworkConfig(self, **kwargs):
        eth = kwargs.get('interface')
        ipAddr = kwargs.get('ipAddr')
        netMask = kwargs.get('netMask')
        broadcast = kwargs.get('broadcast')
        config = kwargs.get('config', True)

        bailflag = 0
        interfaceUpOption = 0
        returnCode = 0

        retStruct = dict()

        if self.ipFormatChk(ipAddr) == False:
            lib.LogOutput('error', 'invalid ipaddress format :' + ipAddr)
            returnCode = 1
            #retStruct['buffer'] = 'Invalid ip address passed'
        elif self.ipFormatChk(netMask) == False:
            lib.LogOutput('error', 'invalid netmask format :' + netMask)
            returnCode = 1
            #retStruct['buffer'] = 'Invalid net mask passed'
        elif self.ipFormatChk(broadcast) == False:
            lib.LogOutput('error', 'invalid broadcast format :'
                             + broadcast)
            returnCode = 1
            #retStruct['buffer'] = 'Invalid broadcast passed'

        if returnCode:
            #retStruct['returnCode'] = returnCode
            returnCls = lib.returnStruct(returnCode=1)
            return returnCls

        overallBuffer = []
        # Validate that the interface exists
        while bailflag == 0:
            # Send the command
            retDeviceInt = self.DeviceInteract(command=self.LIST_ETH_INTERFACES_CMD)
            retCode = retDeviceInt.get('returnCode')
            retBuff = retDeviceInt.get('buffer')
            overallBuffer.append(retBuff)
            if retCode != 0:
                lib.LogOutput('error', 'Failed to execute the command : '
                                  + self.LIST_ETH_INTERFACES_CMD)
                bailflag = 1
                returnCode = 1
            else:
                lib.LogOutput('debug',
                                 'Successfully executed the command : '
                                 + self.LIST_ETH_INTERFACES_CMD)
                if retBuff.find(eth) != -1:
                    lib.LogOutput('debug','eth interface is validated for : '
                                    + eth)
                    bailflag = 1
                else:
                    lib.LogOutput('debug', 'eth interface failed to validate for : '
                                        + eth)
                    #retStruct['buffer'] = \
                    #        'eth interface failed to validate for : ' + eth
                    if interfaceUpOption:
                        bailflag = 1
                        returnCode = 1
                        break
                    interfaceUpOption = 1
                    command = self.ENABLE_ETH_INTERFACE_CMD % eth
                    retDevInt = self.DeviceInteract(command=command)
                    retCode = retDevInt.get('returnCode')
                    retBuff = retDevInt.get('buffer')
                    overallBuffer.append(retBuff)
                    if retCode != 0:
                        lib.LogOutput('error',
                                        'Failed to execute the command : '
                                        + command)
                        bailflag = 1
                        returnCode = 1
                        #retStruct['buffer'] = \
                        #        'Failed to execute the command : ' + command
                    else:
                        lib.LogOutput('debug',
                                         'Successfully executed the command : '
                                         + command)

                    if returnCode:
                        bufferString = ""
                        for curLine in overallBuffer:
                            bufferString += str(curLine)
                        returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
                        return returnCls

        if config is False:
            command = self.ETH_INTERFACE_CFGIP_IFCFG_CLEAR_CMD % eth
            retDevInt = self.DeviceInteract(command=command)
            retCode = retDevInt.get('returnCode')
            retBuff = retDevInt.get('buffer')
            overallBuffer.append(retBuff)
            if retCode != 0:
                lib.LogOutput('error', 'Failed to execute the command : '
                              + command)
                returnCode = 1
                #retStruct['buffer'] = 'Failed to execute the command : ' + command
            else:
                lib.LogOutput('info','Successfully executed the command : '
                                 + command)
        else:
            # Here we are configuring the interface
            command = self.ETH_INTERFACE_CFGIP_IFCFG_CMD % (eth, ipAddr, netMask,
                broadcast)
            retDevInt = self.DeviceInteract(command=command)
            retCode = retDevInt.get('returnCode')
            retBuff = retDevInt.get('buffer')
            overallBuffer.append(retBuff)
            if retCode != 0:
                lib.LogOutput('error', 'Failed to execute the command : '
                            + command)
                returnCode = 1
                #retStruct['buffer'] = 'Failed to execute the command : ' \
                #+ command
            else:
                lib.LogOutput('debug','Successfully executed the command : '+ command)
            
            if returnCode != 1: 
                command = self.LIST_INTERFACE_IP_CMD % eth
                retDevInt = self.DeviceInteract(command=command)
                retCode = retDevInt.get('returnCode')
                retBuff = retDevInt.get('buffer')
                overallBuffer.append(retBuff)
                if retCode != 0:
                    lib.LogOutput('error',
                                 'Failed to execute the command : '
                                 + command)
                    returnCode = 1
                    #retStruct['buffer'] = 'Failed to execute the command : ' + command
                else:
                    lib.LogOutput('debug','Successfully executed the command : '
                                     + command)
 
            if retBuff.find(ipAddr) == -1:
                lib.LogOutput('error',
                                 'IP addr %s is not configured successfully on interface %s : '
                                  % (ipAddr, eth))
                #retStruct['buffer'] = 'Failed to execute the command : ' + command
            else:
                lib.LogOutput('info','IP addr %s configured successfully on interface %s : '
                                 % (ipAddr, eth))

        #retStruct['returnCode'] = returnCode
        # Fill out buffer
        bufferString = ""
        for curLin in overallBuffer:
            bufferString += str(curLin)
            #print curLin
        #retStruct['buffer'] = bufferString
        returnCls = lib.returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls


    def ipFormatChk(self, ip_str):
        pattern = \
         r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        if re.match(pattern, ip_str):
            return True
        else:
            return False

    def Network6Config(self,**kwargs):
        eth = kwargs.get('interface')
        ipAddr = kwargs.get('ipAddr')
        netMask = kwargs.get('netMask')
        config = kwargs.get('config', True)

        # Local variables
        bailflag = 0
        interfaceUpOption = 0
        returnCode = 0
        retStruct = dict()
        overallBuffer = []
        #retStruct['buffer'] = []

        try:
            socket.inet_pton(socket.AF_INET6, ipAddr)
        except socket.error:
            returnCode = 1

        if netMask > 128 and netMask < 1:
            returnCode = 1

        if returnCode:
            #retStruct['returnCode'] = returnCode
            lib.LogOutput('error',
                         'Invalid ipv6 address or netMask passed ')
            #retStruct['buffer'] = 'Invalid ipv6 address or netMask passed '
            returnCls = lib.returnStruct(returnCode=returnCode)
            return returnCls

        while bailflag == 0:
            # Send the command
            retDevInt = self.DeviceInteract(command=self.LIST_ETH_INTERFACES_CMD)
            retCode = retDevInt.get('returnCode')
            retBuff = retDevInt.get('buffer')
            overallBuffer.append(retBuff)
            if retCode != 0:
                lib.LogOutput('error', 'Failed to execute the command : '
                              + self.LIST_ETH_INTERFACES_CMD)
                bailflag = 1
                returnCode = 1
                #retStruct['buffer'] = 'Failed to execute the command : ' \
                # + self.LIST_ETH_INTERFACES_CMD
            else:
                lib.LogOutput('debug',
                             'Successfully executed the command : '
                             + self.LIST_ETH_INTERFACES_CMD)
                if retBuff.find(eth) != -1:
                    lib.LogOutput('info',
                                 'eth interface is validated for : '
                                 + eth)
                    bailflag = 1
                else:
                    lib.LogOutput('error',
                                 'eth interface failed to validate for : '
                                  + eth)
                    #retStruct['buffer'] = \
                    #'eth interface failed to validate for : ' + eth
                    if interfaceUpOption:
                        bailflag = 1
                        returnCode = 1
                        break
                    interfaceUpOption = 1
                    command = self.ENABLE_ETH_INTERFACE_CMD % eth
                    retDevInt = self.DeviceInteract(command=command)
                    retCode = retDevInt.get('returnCode')
                    retBuff = retDevInt.get('buffer')
                    overallBuffer.append(retBuff)
                    if retCode != 0:
                        lib.LogOutput('error',
                            'Failed to execute the command : '
                            + command)
                        bailflag = 1
                        returnCode = 1
                        #retStruct['buffer'] = \
                        #'Failed to execute the command : ' + command
                    else:
                        lib.LogOutput('debug',
                            'Successfully executed the command : '
                            + command)

        if returnCode:
            bufferString = ""
            for curLin in overallBuffer:
                bufferString += str(curLin)

            #retStruct['buffer'] = bufferString
            returnCls = lib.returnStruct(returnCode=1, buffer=bufferString)
            return returnCls

        if config is False:
            command = self.ETH_INTERFACE_CFGIP_CLEAR_CMD % (ipAddr, netMask, eth)
            retDevInt = self.DeviceInteract(command=command)
            retCode = retDevInt.get('returnCode')
            retBuff = retDevInt.get('buffer')
            overallBuffer.append(retBuff)
            if retCode != 0:
                lib.LogOutput('error', 'Failed to execute the command : '
                              + command)
                returnCode = 1
                #retStruct['buffer'] = 'Failed to execute the command : ' \
                #+ command
            else:
                lib.LogOutput('debug',
                             'Successfully executed the command : '
                             + command)
        else:
            command = self.ETH_INTERFACE_CFGIP_CMD % (ipAddr, netMask, eth)
            retDevInt = self.DeviceInteract(command=command)
            retCode = retDevInt.get('returnCode')
            retBuff = retDevInt.get('buffer')
            overallBuffer.append(retBuff)
            if retCode != 0:
                lib.LogOutput('error', 'Failed to execute the command : '
                              + command)
                returnCode = 1
                #retStruct['buffer'] = 'Failed to execute the command : ' \
                #+ command
            else:
                lib.LogOutput('debug',
                             'Successfully executed the command : '
                             + command)

            if returnCode != 1:
                command = self.LIST_INTERFACE_IP_CMD % eth
                retDevInt = self.DeviceInteract(command=command)
                retCode = retDevInt.get('returnCode')
                retBuff = retDevInt.get('buffer')
                overallBuffer.append(retBuff)
                if retCode != 0:
                    lib.LogOutput('error',
                                 'Failed to execute the command : '
                                 + command)
                    returnCode = 1
                    #retStruct['buffer'] = \
                    #'Failed to execute the command : ' + command
                else:
                    lib.LogOutput('debug',
                                 'Successfully executed the command : '
                                 + command)

            if retBuff.find(ipAddr) == -1:
                lib.LogOutput('error',
                                 'IP addr %s is not configured successfully on interface %s : '
                                  % (ipAddr, eth))
                #retStruct['buffer'] = \
                #    'Failed to execute the command : ' + command
            else:
                lib.LogOutput('info',
                                 'IP addr %s configured successfully on interface %s : '
                                  % (ipAddr, eth))

        bufferString = ""
        for curLin in overallBuffer:
            bufferString += str(curLin)
            #print curLin
        #retStruct['buffer'] = bufferString
        returnCls = lib.returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls

    def Ping(self, **kwargs):

        ipAddr = kwargs.get('ipAddr')
        ipv6Flag = kwargs.get('ipv6Flag', False)
        packetCount = kwargs.get('packetCount', 10)
        packetSize = kwargs.get('packetSize', 128)
        eth = kwargs.get('interface', 'eth1')

        retStruct = dict()
        #retStruct['returnCode'] = 1
        #retStruct['buffer'] = ""
        retStruct['packets_transmitted'] = 0
        retStruct['packets_received'] = 0
        retStruct['packet_loss'] = 0
        retStruct['time'] = 0
        retStruct['rtt_min'] = 0
        retStruct['rtt_avg'] = 0
        retStruct['rtt_max'] = 0
        retStruct['rtt_mdev'] = 0
        overallBuffer = []
        returnCode = 0
        command = ''
        if ipv6Flag:
            try:
                socket.inet_pton(socket.AF_INET6, ipAddr)
                if ipAddr.find('fe80') == -1:
                    command = 'ping6 %s -c %d -s %d' % (ipAddr, packetCount, 
                                                        packetSize)
                else:
                    command = 'ping6 -I %s %s -c %d -s %d' % (eth, ipAddr,
                                                              packetCount, 
                                                              packetSize)
            except socket.error:
                returnCode = 1
        else:
            try:
                socket.inet_pton(socket.AF_INET, ipAddr)
                command = 'ping %s -c %d -s %d' % (ipAddr, packetCount,
                                                   packetSize)
            except socket.error:
                returnCode = 1

        if returnCode == 0:
            # Send the command
            retDevInt = self.DeviceInteract(command=command)
            retCode = retDevInt.get('returnCode')
            retBuff = retDevInt.get('buffer')
            overallBuffer.append(retBuff)
            if retCode != 0:
                lib.LogOutput('error', 'Failed to execute the command : '
                                 + command)
            else:
                lib.LogOutput('info', 'Successfully executed the command : '
                                 + command)

            if retBuff.find('bytes from') == -1:
                returnCode = 1
            else:
                returnCode = 0
                #retStruct['buffer'] = retBuff
        else:
            returnCode = 1
            #retStruct['buffer'] = 'Invalid ip address'

        # Fill out buffer
        bufferString = ""
        for curLin in overallBuffer:
            bufferString += str(curLin)
            #print curLin
        #retStruct['buffer'] = bufferString

        # Carve the buffer up to get statistics
        #10 packets transmitted, 10 received, 0% packet loss, time 8997ms
        #rtt min/avg/max/mdev = 0.342/0.456/0.693/0.096 ms

        for curLine in bufferString.split('\r\n'):
            print curLine
            statsLine1 = re.match(r'(\d+) packets transmitted, (\d+) received, (\d+)% packet loss, time (\d+)ms', curLine)
            if statsLine1:
                retStruct['packets_transmitted'] = int(statsLine1.group(1))
                retStruct['packets_received'] = int(statsLine1.group(2))
                retStruct['packet_loss'] = int(statsLine1.group(3))
                retStruct['time'] = int(statsLine1.group(4))
                continue
                
            statsLine2 = re.match(r'rtt min/avg/max/mdev = ([0-9]+\.[0-9]+)/([0-9]\.[0-9]+)/([0-9]+\.[0-9]+)/([0-9]+\.[0-9]+) ms', curLine)
            if statsLine2:
                retStruct['rtt_min'] = float(statsLine2.group(1))
                retStruct['rtt_avg'] = float(statsLine2.group(2))
                retStruct['rtt_max'] = float(statsLine2.group(3))
                retStruct['rtt_mdev'] = float(statsLine2.group(4))
                continue
                
        returnCls = lib.returnStruct(returnCode=returnCode, buffer=bufferString, data=retStruct)
        return returnCls

    def IPRoutesConfig(self, **kwargs):
        config = kwargs.get('config', True)
        destNetwork = kwargs.get('destNetwork')
        netMask = kwargs.get('netMask')
        #via = kwargs.get('via')
        gateway = kwargs.get('gateway', None)
        eth = kwargs.get('interface', 'eth1')
        metric = kwargs.get('metric', None)
        ipv6Flag = kwargs.get('ipv6Flag', False)

        defaultRoute = 0

        retStruct = dict()
        overallBuffer = []
        # Local variables
        #connection = self.expectHndl

        returnCode = 0

        if config is True:
            routeOperation = "add"
        else:
            routeOperation = "del"

        if routeOperation != 'add' and routeOperation != 'del':
            #retStruct['buffer'] = 'Invalid routeOperation : %s' \
            #% routeOperation
            lib.LogOutput('error', "Invalid route operation : " + routeOperation)
            returnCode = 1

        if ipv6Flag:
            try:
                socket.inet_pton(socket.AF_INET6, destNetwork)
                if destNetwork == '::':
                    defaultRoute = 1
                    route_command = \
                    'ip -6 route %s %s via %s' % (routeOperation, 'default', gateway)
                else:
                    route_command = \
                    'ip -6 route %s %s/%d via %s' % (
                    routeOperation,
                    destNetwork,
                    netMask,
                    gateway)
                if metric is not None:
                    route_command += " metric "+ metric
            except socket.error:
                #retStruct['buffer'] = 'Invalid destination : %s' \
                #% destNetwork
                lib.LogOutput('error', "Invalid destination " + destNetwork)
                returnCode = 1
        else:
            try:
                socket.inet_pton(socket.AF_INET, destNetwork)
                if destNetwork == '0.0.0.0':
                    defaultRoute = 1
                    route_command = 'route %s %s gw %s dev %s metric %d' \
                    % (routeOperation, 'default', gateway, eth, metric)
                else:
                    route_command = 'route %s -net %s/%d gw %s' \
                    % (routeOperation, destNetwork, netMask, gateway)
                if metric is not None:
                    route_command += ' metric ' + metric
            except socket.error:
                #retStruct['buffer'] = 'Invalid destination : %s' \
                #% destNetwork
                lib.LogOutput('error', "Invalid destination : " + destNetwork)
                returnCode = 1

        if returnCode == 0:
            # Send the command
            retDevInt = self.DeviceInteract(command=route_command)
            retCode = retDevInt.get('returnCode')
            retBuff = retDevInt.get('buffer')
            overallBuffer.append(retBuff)
            if retCode != 0:
                lib.LogOutput('error', 'Failed to execute the command : '
                              + route_command)
                returnCode = 1
            else:
                lib.LogOutput('info','Successfully executed the command : '
                                 + route_command)
                #retStruct['buffer'] = retBuff
        else:
            #retStruct['buffer'] = 'Invalid ip address'
            lib.LogOutput('error', "Invalid IP address")

        #retStruct['returnCode'] = returnCode
        #return retStruct
        bufferString = ""
        for curLin in overallBuffer:
            bufferString += str(curLin)
            #print curLin
        #retStruct['buffer'] = bufferString
        returnCls = lib.returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls

    def GetDirectLocalLinkAddresses(self):

        localLinkDict = dict()
        localLinkElements = []
        command = 'ip -6 neighbour show'

        # Send the command
        # Local variables
        retDevInt = self.DeviceInteract(command=command)
        retCode = retDevInt.get('returnCode')
        retBuff = retDevInt.get('buffer')
        if retCode != 0:
            lib.LogOutput('error', 'Failed to execute the command : '
                         + command)
            retBuff = retBuff.split('\n')
        for output in retBuff:
            if re.search('^fe80', output):
                localLinkDict['address'] = output.split(' ')[0]
                localLinkDict['eth'] = output.split(' ')[2]
                localLinkElements.append(localLinkDict.copy())
        return localLinkElements


    def FileTransfer(self,filepath,localpath,direction):

        returnCode = 0
        paramiko.util.log_to_file('/tmp/paramiko.log')
        # Look up and see if we are physical or virtual
        xpathString = ".//reservation/id"
        rsvnEtreeElement = lib.XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
        if rsvnEtreeElement == None:
        # We are not in a good situation, we need to bail
            lib.LogOutput('error', "Could not find reservation id tag in topology")
            return None
        rsvnType = rsvnEtreeElement.text
        if rsvnType != 'virtual':
            #Get the credentials of the workstation from XML file (physical devices)
            xpathString = ".//device[name='" + self.device + "']/connection/ipAddr"
            ipNode = lib.XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
            if ipNode == None:
                lib.LogOutput('error', "Failed to obtain IP address for device " + device )
                return None
            hostIP = ipNode.text
            lib.LogOutput ('debug', self.device + " connection IP address:  " + hostIP)
            port = 22

            #Open a ssh connection to the host
            transport = paramiko.Transport((hostIP, port))

            #Extract username/password for logging in the workstation
            xpathString = ".//device[name='" + self.device + "']/login/adminPassword"
            password = lib.XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
            if password == None:
                lib.LogOutput('error', "Failed to obtain password for device " + self.device )
                return None
            password = password.text
            xpathString = ".//device[name='" + self.device + "']/login/adminUser"
            username = lib.XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
            if username == None:
                lib.LogOutput('error', "Failed to obtain username for device " + self.device )
                return None
            username = username.text

            transport.connect(username = username, password = password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            #Transfer file
            try:
                sftp.mkdir("/root/rest")
            except IOError, e:
                print '(assuming ', "/root/rest", 'exists)', e

            try :
                print filepath
                print localpath
                if direction == "get":
                    sftp.get(filepath,localpath)
                else:
                    sftp.put(filepath,localpath)
            except IOError, e:
                lib.LogOutput("error","file not transferred to workstation")
                returnCode = 1
                print e
            #Close a connection
            sftp.close()
            transport.close()
            return returnCode
        else :
            lib.LogOutput("info","Topology is virtual **")
            lib.LogOutput("info","Copy the files from docker container to results directory")
            #Copy the pcap file from docker container to results directory
            #command = "docker cp %s:%s %s"%(self.device,filepath,lib.gbldata.ResultsDirectory)
            #lib.LogOutput('info', command)
            #returnCode = os.system(command)
            #os.rename(filename,self.device+"--"+filename)
            returnCode = 0
            if returnCode != 0:
                lib.LogOutput('error', "Failed to copy pcap file to results directory from device --> "+self.device)
#                returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=self.returnDict)
                return returnJson


    def CreateHostRestInfra(self):
        lib.LogOutput("info","Creating HostRestInfra")
        self.DeviceInteract(command="mkdir /root/rest")
#        self.FileTransfer("/ws/skrishn1/dev/openSwitchFW/ops-ft-framework/rest.tar.gz", "/root/rest/rest.tar.gz", "put")
        self.FileTransfer(self.fwbase+"/rest.tar.gz", "/root/rest/rest.tar.gz", "put")
        tarCommand = "tar -xvzf /root/rest/rest.tar.gz"
        retDeviceInt = self.DeviceInteract(command=tarCommand)
        retCode = retDeviceInt.get('returnCode')
        retBuff = retDeviceInt.get('buffer')
        if retCode != 0:
            lib.LogOutput('error', 'Failed to execute the command : '
                                 + tarCommand)
            returnCode = 1
        else:
            lib.LogOutput('info',
                                 'Successfully executed the command : '
                                 + tarCommand)
        lib.LogOutput("info","Successful in CreateHostRestInfra")

    def RestCmd(self,**kwargs):
        ip = kwargs.get('switch_ip')
        url = kwargs.get('url')
        method = kwargs.get('method')
        data    = kwargs.get('data', None)
        returnCode = 0
        overallBuffer = []
        bufferString = ""
        retStruct = dict()
        try:
            socket.inet_pton(socket.AF_INET, ip)
        except socket.error:
            returnCode = 1
        if returnCode <> 1:
            if data <> None:
                with open(self.fwbase+'/restdata', 'wb') as f:
                   f.write(str(data))
#                    json.dump(data,f)
                   f.close()
                   self.FileTransfer(self.fwbase+"/restdata", "/root/rest/restdata", "put")
            restCmd = "python /root/rest/resttest.py --ip=%s --url=%s --method=%s" %(ip,url,method)
            retDeviceInt = self.DeviceInteract(command=restCmd)
            retCode = retDeviceInt.get('returnCode')
            retBuff = retDeviceInt.get('buffer')
            overallBuffer.append(retBuff)
            if retCode != 0:
                lib.LogOutput('error', 'Failed to execute the command : '
                                  + restCmd)
                returnCode = 1
            else:
                lib.LogOutput('info',
                                 'Successfully executed the command : '
                                 + restCmd)
            for curLin in overallBuffer:
                bufferString += str(curLin)

            output = bufferString.split("\n")
            retStruct['http_retcode'] = output[1]
#            retStruct['http_retcode'] = int(output[1])
            print "Http Returned Code "+retStruct['http_retcode']
            retStruct['response_body'] = output[4]

        returnCls = lib.returnStruct(returnCode=returnCode, buffer=bufferString, data=retStruct)
        return returnCls

