import pexpect
import headers
import common
import switch
import time
#import console
import xml.etree.ElementTree
import os
import re
from Topology import Topology
from Device import Device
import socket

PASSED=0
FAILED=1

# This is the base class for any device - This gives the test case developer the ability to connect to the device
# along with interacting with the device
class VHost ( Device ):
    def __init__(self, **kwargs):
        self.topology = kwargs.get('topology', None)
        self.device = kwargs.get('device', None)
        # Bring in Default member values
        self.defaultMembers()
        self.initExtMembers()
        self.Connect()
    
    def defaultMembers(self):
        self.expectHndl = ""
        self.connectStringBase = "docker exec -ti "
        self.expectDefaultPrompts = ['login:\s*$',
                               'Password:',
                               '\[root@\S+.*\]#',
                               'root@\S+#',
                               pexpect.EOF,
                               pexpect.TIMEOUT]
    def initExtMembers(self):
	self.LIST_ETH_INTERFACES_CMD = 'ifconfig -a | grep Ethernet'
	self.LIST_INTERFACE_IP_CMD = 'ifconfig %s | grep inet'
	self.ENABLE_ETH_INTERFACE_CMD = 'ifconfig %s up'
	self.ETH_INTERFACE_CFGIP_CMD = 'ip addr add %s/%d dev %s'
	self.ETH_INTERFACE_CFGIP_IFCFG_CMD = 'ifconfig %s %s netmask %s broadcast %s'
	self.ETH_INTERFACE_CFGIP_CLEAR_CMD = 'ip addr del %s/%d dev %s'
	self.ETH_INTERFACE_CFGIP_IFCFG_CLEAR_CMD = 'ifconfig %s 0.0.0.0'

    def Connect(self):
        # Look up the device name in the topology - grab connectivity information
        xpathString = ".//device[name='" + self.device + "']"
        etreeElement = common.XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
        if etreeElement == None:
            # We are not in a good situation, we need to bail
            common.LogOutput('error', "Could not find device " + self.device + " in topology")
            return None
        # Code for virtual
        # Go and grab the connection name
        xpathString = ".//device[name='" + self.device + "']/connection/name"
        virtualConn = common.XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
        if virtualConn == None:
            common.LogOutput('error', "Failed to virtual connection for " + self.device )
            return None
        telnetString = self.connectStringBase + self.device + " /bin/bash"
        self.expectHndl = pexpect.spawn(telnetString,echo=False)
        self.expectHndl.delaybeforesend = .5
        expectFileString  = self.device + ".log"
        
        # VINCE TODO - Move ExpectLog to Common Class
        ExpectInstance = switch.ExpectLog.DeviceLogger(expectFileString)
        expectLogFile = ExpectInstance.OpenExpectLog(expectFileString)
        if expectLogFile == 1 :
            common.LogOutput('error', "Unable to create expect log file")
            exit(1)
        #Opening an expect connection to the device with the specified log file
        common.LogOutput('debug', "Opening an expect connection to the device with the specified log file"+expectFileString)
        self.expectHndl = pexpect.spawn(telnetString, echo=False, logfile=switch.ExpectLog.DeviceLogger(expectLogFile))
        self.expectHndl.delaybeforesend = 1
        
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
                # Got EOF
                common.LogOutput('error', "Telnet to host failed")
                return None
            elif index == 5:
                # Got a Timeout
                common.LogOutput('error', "Connection timed out")
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
            #common.LogOutput('debug', curLine)
            sanitizedBuffer += curLine
        common.LogOutput('debug', sanitizedBuffer)

        return self.expectHndl
    
    
    def DeviceInteract(self, **kwargs):
        command = kwargs.get('command')
        errorCheck = kwargs.get('errorCheck', True)

        # Local variables
        bailflag = 0
        retStruct = dict()
        retStruct['returnCode'] = 1
        retStruct['buffer'] = []

        # Send the command

        self.expectHndl.send(command)
        self.expectHndl.send('\r')
        time.sleep(1)
        connectionBuffer = []

        while bailflag == 0:
            #DEBUG print connection
            index = self.expectHndl.expect(self.expectDefaultPrompts, timeout=30)

            #print "Index I got was ", index
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
                # got EOF
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
                common.LogOutput('error', "reached EOF")
                returnCode = 1
            elif index == 5:
                # got Timeout
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
                common.LogOutput('error', "command timeout")
                returnCode = 1
            else :
                tmpBuffer = self.expectHndl.before
                # Pull out the \r\n of the buffer
                tmpBuffer = re.sub('\r\r\n', '', tmpBuffer)
                print "tmpbuffer = " + tmpBuffer
                
                if tmpBuffer != command:
                    connectionBuffer.append(self.expectHndl.before)
        santString = ""
        for curLine in connectionBuffer:#
            santString += str(curLine)

        returnCode = 0
        if errorCheck is True and returnCode == 0:
            errorCheckRetStruct = self.ErrorCheck(buffer=santString)
            returnCode = errorCheckRetStruct['returnCode']
        # Dump the buffer the the debug log
        common.LogOutput('debug', "Sent and received from device: \n" + santString + "\n")

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
            common.LogOutput('error', "Received timeout in ErrorCheck " + str(index))
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

        eth = kwargs.get('eth')
        ipAddr = kwargs.get('ipAddr')
        netMask = kwargs.get('netMask')
        broadcast = kwargs.get('broadcast')
        clear = kwargs.get('clear', False)

        # Local variables
        connection = self.expectHndl

        bailflag = 0
        interfaceUpOption = 0
        returnCode = PASSED

        retStruct = dict()
        retStruct['returnCode'] = FAILED
        retStruct['buffer'] = []

        if self.ipFormatChk(ipAddr) == False:
            common.LogOutput('error', 'invalid ipaddress format :' + ipAddr)
            returnCode = FAILED
            retStruct['buffer'] = 'Invalid ip address passed'
        elif self.ipFormatChk(netMask) == False:
            common.LogOutput('error', 'invalid netmask format :' + netMask)
            returnCode = FAILED
            retStruct['buffer'] = 'Invalid net mask passed'
        elif self.ipFormatChk(broadcast) == False:
            common.LogOutput('error', 'invalid broadcast format :'
                         + broadcast)
            returnCode = FAILED
            retStruct['buffer'] = 'Invalid broadcast passed'

        if returnCode:
            retStruct['returnCode'] = returnCode
            return retStruct

        while bailflag == 0:

            # Send the command

            retStruct = self.DeviceInteract(command=self.LIST_ETH_INTERFACES_CMD)
            retCode = retStruct.get('returnCode')
            retBuff = retStruct.get('buffer')
            if retCode != 0:
                common.LogOutput('error', 'Failed to execute the command : '
                              + self.LIST_ETH_INTERFACES_CMD)
                bailflag = 1
                returnCode = FAILED
                retStruct['buffer'] = 'Failed to execute the command : ' \
                + self.LIST_ETH_INTERFACES_CMD
            else:

                common.LogOutput('info',
                             'Successfully executed the command : '
                             + self.LIST_ETH_INTERFACES_CMD)
                if retBuff.find(eth) != -1:
                    common.LogOutput('info',
                                 'eth interface is validated for : '
                                 + eth)
                    bailflag = 1
                else:
                    common.LogOutput('info',
                                 'eth interface failed to validate for : '
                                  + eth)
                    retStruct['buffer'] = \
                    'eth interface failed to validate for : ' + eth
                    if interfaceUpOption:
                        bailflag = 1
                        returnCode = FAILED
                        break
                    interfaceUpOption = 1
                    command = self.ENABLE_ETH_INTERFACE_CMD % eth
                    retStruct = self.DeviceInteract(command=command)
                    retCode = retStruct.get('returnCode')
                    retBuff = retStruct.get('buffer')
                    if retCode != 0:
                        common.LogOutput('error',
                            'Failed to execute the command : '
                            + command)
                        bailflag = 1
                        returnCode = FAILED
                        retStruct['buffer'] = \
                        'Failed to execute the command : ' + command
                    else:
                        common.LogOutput('info',
                            'Successfully executed the command : '
                            + command)

        if returnCode:
            retStruct['returnCode'] = returnCode
            return retStruct

        if clear:

            command = self.ETH_INTERFACE_CFGIP_IFCFG_CLEAR_CMD % eth
            returnStruct = self.DeviceInteract(connection=connection,
                command=command)
            retCode = returnStruct.get('returnCode')
            retBuff = returnStruct.get('buffer')
            if retCode != 0:
                common.LogOutput('error', 'Failed to execute the command : '
                              + command)
                returnCode = FAILED
                retStruct['buffer'] = 'Failed to execute the command : ' + command
            else:
                common.LogOutput('info',
                             'Successfully executed the command : '
                             + command)
        else:

            command = self.ETH_INTERFACE_CFGIP_IFCFG_CMD % (eth, ipAddr, netMask,
                broadcast)
            returnStruct = self.DeviceInteract(connection=connection,
                command=command)
            retCode = returnStruct.get('returnCode')
            retBuff = returnStruct.get('buffer')
            if retCode != 0:
                common.LogOutput('error', 'Failed to execute the command : '
                            + command)
                returnCode = FAILED
                retStruct['buffer'] = 'Failed to execute the command : ' \
                + command
            else:
                common.LogOutput('info',
                             'Successfully executed the command : '
                             + command)

            if returnCode != FAILED:
                command = self.LIST_INTERFACE_IP_CMD % eth
                retStruct = self.DeviceInteract(connection=connection,
                    command=command)
                retCode = retStruct.get('returnCode')
                retBuff = retStruct.get('buffer')
                if retCode != 0:
                    common.LogOutput('error',
                                 'Failed to execute the command : '
                                 + command)
                    returnCode = FAILED
                    retStruct['buffer'] = \
                       'Failed to execute the command : ' + command
                else:
                    common.LogOutput('info',
                                 'Successfully executed the command : '
                                 + command)

            if retBuff.find(ipAddr) == -1:
                common.LogOutput('error',
                                 'IP addr %s is not configured successfully on interface %s : '
                                  % (ipAddr, eth))
                retStruct['buffer'] = \
                       'Failed to execute the command : ' + command
            else:
                common.LogOutput('info',
                                 'IP addr %s configured successfully on interface %s : '
                                  % (ipAddr, eth))

        retStruct['returnCode'] = returnCode
        return retStruct

    def ipFormatChk(self, ip_str):
        pattern = \
         r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        if re.match(pattern, ip_str):
            return True
        else:
            return False
   
    def Network6Config(self,**kwargs):

        eth = kwargs.get('eth')
        ipAddr = kwargs.get('ipAddr')
        netMask = kwargs.get('netMask')
        clear = kwargs.get('clear', False)

        # Local variables
        connection = self.expectHndl
        bailflag = 0
        interfaceUpOption = 0
        returnCode = PASSED

        retStruct = dict()
        retStruct['returnCode'] = FAILED
        retStruct['buffer'] = []

        try:
            socket.inet_pton(socket.AF_INET6, ipAddr)
        except socket.error:
            returnCode = FAILED

        if netMask > 128 and netMask < 1:
            returnCode = FAILED

        if returnCode:
            retStruct['returnCode'] = returnCode
            common.LogOutput('error',
                         'Invalid ipv6 address or netMask passed ')
            retStruct['buffer'] = 'Invalid ipv6 address or netMask passed '
            return retStruct

        while bailflag == 0:

            # Send the command

            retStruct = self.DeviceInteract(command=self.LIST_ETH_INTERFACES_CMD)
            retCode = retStruct.get('returnCode')
            retBuff = retStruct.get('buffer')
            if retCode != 0:
                common.LogOutput('error', 'Failed to execute the command : '
                              + self.LIST_ETH_INTERFACES_CMD)
                bailflag = 1
                returnCode = FAILED
                retStruct['buffer'] = 'Failed to execute the command : ' \
                 + self.LIST_ETH_INTERFACES_CMD
            else:

                common.LogOutput('info',
                             'Successfully executed the command : '
                             + self.LIST_ETH_INTERFACES_CMD)
                if retBuff.find(eth) != -1:
                    common.LogOutput('info',
                                 'eth interface is validated for : '
                                 + eth)
                    bailflag = 1
                else:
                    common.LogOutput('info',
                                 'eth interface failed to validate for : '
                                  + eth)
                    retStruct['buffer'] = \
                    'eth interface failed to validate for : ' + eth
                    if interfaceUpOption:
                        bailflag = 1
                        returnCode = FAILED
                        break
                    interfaceUpOption = 1
                    command = self.ENABLE_ETH_INTERFACE_CMD % eth
                    retStruct = self.DeviceInteract(connection=connection,
                        command=command)
                    retCode = retStruct.get('returnCode')
                    retBuff = retStruct.get('buffer')
                    if retCode != 0:
                        common.LogOutput('error',
                            'Failed to execute the command : '
                            + command)
                        bailflag = 1
                        returnCode = FAILED
                        retStruct['buffer'] = \
                        'Failed to execute the command : ' + command
                    else:
                        common.LogOutput('info',
                            'Successfully executed the command : '
                            + command)

        if returnCode:
            retStruct['returnCode'] = returnCode
            return retStruct

        if clear:

            command = self.ETH_INTERFACE_CFGIP_CLEAR_CMD % (ipAddr, netMask, eth)
            returnStruct = self.DeviceInteract(connection=connection,
                command=command)
            retCode = returnStruct.get('returnCode')
            retBuff = returnStruct.get('buffer')
            if retCode != 0:
                common.LogOutput('error', 'Failed to execute the command : '
                              + command)
                returnCode = FAILED
                retStruct['buffer'] = 'Failed to execute the command : ' \
                + command
            else:
                common.LogOutput('info',
                             'Successfully executed the command : '
                             + command)
        else:

            command = self.ETH_INTERFACE_CFGIP_CMD % (ipAddr, netMask, eth)
            returnStruct = self.DeviceInteract(connection=connection,
                command=command)
            retCode = returnStruct.get('returnCode')
            retBuff = returnStruct.get('buffer')
            if retCode != 0:
                common.LogOutput('error', 'Failed to execute the command : '
                              + command)
                returnCode = FAILED
                retStruct['buffer'] = 'Failed to execute the command : ' \
                + command
            else:
                common.LogOutput('info',
                             'Successfully executed the command : '
                             + command)

            if returnCode != FAILED:
                command = self.LIST_INTERFACE_IP_CMD % eth
                retStruct = self.DeviceInteract(connection=connection,
                    command=command)
                retCode = retStruct.get('returnCode')
                retBuff = retStruct.get('buffer')
                if retCode != 0:
                    common.LogOutput('error',
                                 'Failed to execute the command : '
                                 + command)
                    returnCode = FAILED
                    retStruct['buffer'] = \
                    'Failed to execute the command : ' + command
                else:
                    common.LogOutput('info',
                                 'Successfully executed the command : '
                                 + command)

            if retBuff.find(ipAddr) == -1:
                common.LogOutput('error',
                                 'IP addr %s is not configured successfully on interface %s : '
                                  % (ipAddr, eth))
                retStruct['buffer'] = \
                    'Failed to execute the command : ' + command
            else:
                common.LogOutput('info',
                                 'IP addr %s configured successfully on interface %s : '
                                  % (ipAddr, eth))

        retStruct['returnCode'] = returnCode
        return retStruct

    def DevicePing(self, **kwargs):

        ipAddr = kwargs.get('ipAddr')
        ipv6Flag = kwargs.get('ipv6Flag', False)
        packetCount = kwargs.get('packetCount', 10)
        packetSize = kwargs.get('packetSize', 128)
        eth = kwargs.get('eth', 'eth1')

        retStruct = dict()
        retStruct['returnCode'] = 1
        retStruct['buffer'] = []

        # Local variables
        connection = self.expectHndl

        returnCode = PASSED
        command = ''
        if ipv6Flag:
            try:
                socket.inet_pton(socket.AF_INET6, ipAddr)
                if ipAddr.find('fe80') == -1:
                    command = 'ping6 %s -c %d -s %d' % (ipAddr,
                        packetCount, packetSize)
                else:
                    command = 'ping6 -I %s %s -c %d -s %d' % (eth, ipAddr,
                        packetCount, packetSize)
            except socket.error:
                returnCode = FAILED
        else:
            try:
                socket.inet_pton(socket.AF_INET, ipAddr)
                command = 'ping %s -c %d -s %d' % (ipAddr, packetCount,
                    packetSize)
            except socket.error:
                returnCode = FAILED

        if returnCode == PASSED:

            # Send the command

            returnStruct = self.DeviceInteract(connection=connection,
                command=command)
            retCode = returnStruct.get('returnCode')
            retBuff = returnStruct.get('buffer')
            if retCode != 0:
                common.LogOutput('error', 'Failed to execute the command : '
                              + command)
            else:
                common.LogOutput('info',
                             'Successfully executed the command : '
                             + command)

            if retBuff.find('bytes from') == -1:
                returnCode = FAILED
            else:
                returnCode = PASSED
                retStruct['buffer'] = retBuff
        else:
            retStruct['buffer'] = 'Invalid ip address'

        retStruct['returnCode'] = returnCode
        return retStruct

    def IPRoutesConfig(self, **kwargs):

        routeOperation = kwargs.get('routeOperation')
        destNetwork = kwargs.get('destNetwork')
        netMask = kwargs.get('netMask')
        via = kwargs.get('via')
        eth = kwargs.get('eth', 'eth1')
        metric = kwargs.get('metric', 1024)
        ipv6Flag = kwargs.get('ipv6Flag', False)

        defaultRoute = 0

        retStruct = dict()
        retStruct['returnCode'] = 1
        retStruct['buffer'] = []

        # Local variables
        connection = self.expectHndl

        returnCode = PASSED

        if routeOperation != 'add' and routeOperation != 'delete':
            retStruct['buffer'] = 'Invalid routeOperation : %s' \
            % routeOperation
            returnCode = FAILED

        if ipv6Flag:
            try:
                socket.inet_pton(socket.AF_INET6, destNetwork)
                if destNetwork == '::':
                    defaultRoute = 1
                    route_command = \
                    'ip -6 route %s %s via %s dev %s metric %d' \
                    % (routeOperation, 'default', via, eth, metric)
                else:
                    route_command = \
                    'ip -6 route %s %s/%d via %s dev %s metric %d' % (
                    routeOperation,
                    destNetwork,
                    netMask,
                    via,
                    eth,
                    metric,
                    )
            except socket.error:
                retStruct['buffer'] = 'Invalid destination : %s' \
                % destNetwork
                returnCode = FAILED
        else:
            try:
                socket.inet_pton(socket.AF_INET, destNetwork)
                if destNetwork == '0.0.0.0':
                    defaultRoute = 1
                    route_command = 'route %s %s gw %s dev %s metric %d' \
                    % (routeOperation, 'default', via, eth, metric)
                else:
                    route_command = 'route %s -net %s/%d gw %s metric %d' \
                    % (routeOperation, destNetwork, netMask, via,
                       metric)
            except socket.error:
                retStruct['buffer'] = 'Invalid destination : %s' \
                % destNetwork
                returnCode = FAILED

        if returnCode == PASSED:

            # Send the command

            returnStruct = self.DeviceInteract(connection=connection,
                command=route_command)
            retCode = returnStruct.get('returnCode')
            retBuff = returnStruct.get('buffer')
            if retCode != 0:
                common.LogOutput('error', 'Failed to execute the command : '
                              + route_command)
                returnCode = FAILED
            else:
                common.LogOutput('info',
                             'Successfully executed the command : '
                             + route_command)
                retStruct['buffer'] = retBuff
        else:
            retStruct['buffer'] = 'Invalid ip address'

        retStruct['returnCode'] = returnCode
        return retStruct


    def GetDirectLocalLinkAddresses(self):

        localLinkDict = dict()
        localLinkElements = []
        command = 'ip -6 neighbour show'

        # Send the command
        # Local variables
        connection = self.expectHndl

        returnStruct = self.DeviceInteract(connection=connection,
            command=command)
        retCode = returnStruct.get('returnCode')
        retBuff = returnStruct.get('buffer')
        if retCode != 0:
            common.LogOutput('error', 'Failed to execute the command : '
                         + command)
            retBuff = retBuff.split('\n')
        for output in retBuff:
            if re.search('^fe80', output):
                localLinkDict['address'] = output.split(' ')[0]
                localLinkDict['eth'] = output.split(' ')[2]
                localLinkElements.append(localLinkDict.copy())
        return localLinkElements

