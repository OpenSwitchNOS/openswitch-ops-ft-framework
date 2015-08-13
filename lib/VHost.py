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

# This is the base class for any device - This gives the test case developer the ability to connect to the device
# along with interacting with the device
class VHost ( Device ):
    def __init__(self, **kwargs):
        self.topology = kwargs.get('topology', None)
        self.device = kwargs.get('device', None)
        # Bring in Default member values
        self.defaultMembers()
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

