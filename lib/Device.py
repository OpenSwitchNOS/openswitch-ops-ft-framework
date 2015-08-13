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

# This is the base class for any device - This gives the test case developer the ability to connect to the device
# along with interacting with the device
class Device ():
    def __init__(self, **kwargs):
        self.topology = kwargs.get('topology', None)
        self.device = kwargs.get('device', None)
        self.expectHndl = None
        self.expectList = ['login:\s*$',
                           'root@\S+:.*#\s*$',
                           'bash-\d+.\d+#',
                           pexpect.EOF,
                           pexpect.TIMEOUT]
        self.Connect()
        
        
    def cmd(self, cmd):
        retStruct = self.DeviceInteract(command=cmd)
        returnCode = retStruct.get('returnCode')
        if returnCode != 0:
            common.LogOutput('error', "Failed to send command " + cmd +" to device " + self.device)
            return None
        returnBuffer = retStruct.get('buffer')
        return returnBuffer
    
    # Device Connect Method
    def Connect(self):
        # Look up and see if we are physical or virtual
        xpathString = ".//reservation/id"
        rsvnEtreeElement = common.XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
        if rsvnEtreeElement == None:
            # We are not in a good situation, we need to bail
            common.LogOutput('error', "Could not find reservation id tag in topology")
            return None

        rsvnType = rsvnEtreeElement.text

        # Look up the device name in the topology - grab connectivity information
        xpathString = ".//device[name='" + self.device + "']"
        etreeElement = common.XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
        if etreeElement == None:
            # We are not in a good situation, we need to bail
            common.LogOutput('error', "Could not find device " + self.device + " in topology")
            return None
        if rsvnType == 'virtual':
            # Code for virtual
            # Go and grab the connection name
            xpathString = ".//device[name='" + self.device + "']/connection/name"
            virtualConn = common.XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
            if virtualConn == None:
                common.LogOutput('error', "Failed to virtual connection for " + self.device)
                return None
            telnetString = "docker exec -ti " + self.device + " /bin/bash"
            #self.expectHndl = pexpect.spawn(telnetString, echo=False)
            #self.expectHndl.delaybeforesend = .5
            #expectFileString = self.device + ".log"
        else:
            # Code for physical
            # Grab IP from etree
            xpathString = ".//device[name='" + self.device + "']/connection/ipAddr"
            ipNode = common.XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
            if ipNode == None:
                common.LogOutput('error', "Failed to obtain IP address for device " + self.device)
                return None

            self.ipAddress = ipNode.text
            common.LogOutput ('debug', self.device + " connection IP address:  " + self.ipAddress)

            # Grab Port from etree
            xpathString = ".//device[name='" + self.device + "']/connection/port"
            portNode = common.XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
            if portNode == None:
                common.LogOutput('error', "Failed to obtain Port for device " + self.device)
                return None

            self.port = portNode.text
            common.LogOutput ('debug', self.device + " connection port:  " + self.port)

            # Grab a connetion element - not testing this since this should exist since we obtained
            # things before us
            xpathString = ".//device[name='" + self.device + "']/connection"
            connectionElement = common.XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)

            # Grab a connetion element - not testing this since this should exist since we obtained
            # things before us
            xpathString = ".//device[name='" + self.device + "']/connection"
            connectionElement = common.XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
            # Create Telnet handle
            # Enable expect device Logging for every connection
            # Single Log file exists for logging device exchange using pexpect logger .
            # Device logger  name format :: devicename_IP-Port

            telnetString = "telnet " + self.ipAddress + " " + self.port
            expectFileString = self.device + "_" + self.ipAddress + "--" + self.port + ".log"


            ExpectInstance = switch.ExpectLog.DeviceLogger(expectFileString)
            expectLogFile = ExpectInstance.OpenExpectLog(expectFileString)
            if expectLogFile == 1 :
                common.LogOutput('error', "Unable to create expect log file")
                exit(1)
            # Opening an expect connection to the device with the specified log file
            common.LogOutput('debug', "Opening an expect connection to the device with the specified log file" + expectFileString)
            if rsvnType == 'virtual':
                self.expectHndl = pexpect.spawn(telnetString, echo=False, logfile=switch.ExpectLog.DeviceLogger(expectLogFile))
                self.expectHndl.delaybeforesend = 1
            else:
                self.expectHndl = pexpect.spawn (telnetString, echo=False, logfile=switch.ExpectLog.DeviceLogger(expectLogFile))

            # Lets go and detect our connection - this will get us to a context we know about
            retVal = self.DetectConnection()
            if retVal is None:
                common.LogOutput('error', "Failed to detect connection for device - looking to reset console")
                # Connect to the console
                conDevConn = console.Connect(self.ipAddress)
                # now lets logout the port we are trying to connect to
                # print("send logout seq")
                retCode = console.ConsolePortLogout(connection=conDevConn, port=self.port)
                if retCode != 0:
                    return None
                console.ConnectionClose(connection=conDevConn)
                # Now retry the connect & detect connection
                self.expectHndl = pexpect.spawn (telnetString, echo=False, logfile=switch.ExpectLog.DeviceLogger(expectLogFile))
                retVal = self.DetectConnection()

            if retVal is None:
                return None
            
    # DetectConnection - This will get the device in the proper context state
    def DetectConnection(self):
        bailflag = 0
        # print "In detect "
        
        self.expectHndl.send('\r')
        time.sleep(2)
        connectionBuffer = []
        sanitizedBuffer = ""
        while bailflag == 0:
            index = self.expectHndl.expect(self.expectList,
                                           timeout=200)
            if index == 0:
                # Need to send login string
                common.LogOutput("debug", "Login required::")
                self.expectHndl.sendline("root")
                connectionBuffer.append(self.expectHndl.before)
            elif index == 1:
                bailflag = 1
                common.LogOutput("debug", "Root prompt detected:")
                connectionBuffer.append(self.expectHndl.before)
            elif index == 2:
                # Got prompt.  We should be good
                bailflag = 1
                common.LogOutput("debug", "Root prompt detected: Virtual")
                connectionBuffer.append(self.expectHndl.before)
            elif index == 3:
                # Got EOF
                common.LogOutput('error', "Telnet to switch failed")
                return None
            elif index == 4:
                # Got a Timeout
                common.LogOutput('error', "Connection timed out")
                return None
            else :
                # print "Got index ", index, " wainting again"
                # print('Got index %d wainting again'.format(index))
                connectionBuffer.append(self.expectHndl.before)
                                    # Append on buffer after
        connectionBuffer.append(self.expectHndl.after)
        self.expectHndl.expect(['$'], timeout=2)
        # Now lets put in the topology the expect handle
        for curLine in connectionBuffer:
            sanitizedBuffer += curLine
        common.LogOutput('debug', sanitizedBuffer)
        return self.expectHndl
        
    # Routine allows the user to interact with a device and get appropriate output
    def DeviceInteract(self, **kwargs):
        command = kwargs.get('command')
        errorCheck = kwargs.get('errorCheck',True)
        ErrorFlag = kwargs.get('CheckError')
        
        # Local variables
        bailflag = 0
        returnCode = 0
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
            index = self.expectHndl.expect(self.expectList,
                                 timeout=120)
            if index == 0:
                # Need to send login string
                self.expectHndl.send("root \r")
                connectionBuffer.append(self.expectHndl.before)
            elif index == 1:
                # Got prompt.  We should be good
                #print "Got prompt, we should be good"
                #print('Got prompt, we should be good')
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
            elif index == 2:
                # Got bash prompt - virtual
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
            elif index == 3:
                # got EOF
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
                common.LogOutput('error', "connection closed to console")
                returnCode = 1
            elif index == 4:
                # got Timeout
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
                common.LogOutput('error', "command timeout")
                returnCode = 1
            else :
                connectionBuffer.append(self.expectHndl.before)
                #time.sleep(3)
                connectionBuffer.append(self.expectHndl.after)
                self.expectHndl.expect(['$'], timeout=1)
                    
        santString = ""
        for curLine in connectionBuffer:#
            santString += str(curLine)

        #Error Check routine identification
        #There are seperate Error check libraries for CLI,OVS and REST commands.
        #The following portion checks for Errors for OVS commands
        if errorCheck is True and returnCode == 0 and ErrorFlag == None :
            #errorCheckRetStruct = switch.ErrorCheck(connection=connection, buffer=santString)
            #returnCode = errorCheckRetStruct['returnCode']
            # Dump the buffer the the debug log
            common.LogOutput('debug', "Sent and received from device: \n" + santString + "\n")

        #The following portion checks for Errors in CLI commands
        if ErrorFlag == 'CLI' :
            #errorCheckRetStruct = switch.CLI.ErrorCheck(connection=connection, buffer=santString)
            #returnCode = errorCheckRetStruct['returnCode']
            common.LogOutput('debug', "NEED TO FIX")
            #The following file checks for errors in Onie prompts after analyzing Onie expect buffer
        if ErrorFlag == 'Onie' :
            #errorCheckRetStruct = switch.ErrorCheckOnie(connection=connection, buffer=santString)
            #returnCode = errorCheckRetStruct['returnCode']
            common.LogOutput('debug', "NEED TO FIX")

        # Return dictionary
        common.LogOutput('debug', "Sent and received from device: \n" + santString + "\n")
        retStruct['returnCode'] = returnCode
        retStruct['buffer'] = santString
        return retStruct
        
    def ErrorCheck(self, **kwargs):
        #connection = kwargs.get('connection')
        buffer = kwargs.get('buffer')
        # Local variables
        returnCode = 0

        retStruct = dict()
        retStruct['returnCode'] = returnCode

        # Set up the command for error check
        command = "echo $?"
        buffer = ""
        self.expectHndl.send(command)
        self.expectHndl.send('\r\n')

        index = self.expectHndl.expect(['root@\S+:.*#\s*$','bash-\d+.\d+#\s*$'], timeout=200)
        if index == 0 or index == 1:
            buffer += self.expectHndl.before
            buffer += self.expectHndl.after
        else:
            common.LogOutput('error', "Received timeout in switch.ErrorCheck")
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
        

