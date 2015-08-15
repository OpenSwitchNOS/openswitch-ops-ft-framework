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
#from Console import Console

# This is the base class for any device - This gives the test case developer the ability to connect to the device
# along with interacting with the device
class VSwitch ( Device ):
    def __init__(self, **kwargs):
        self.topology = kwargs.get('topology', None)
        self.device = kwargs.get('device', None)
        # Lets initialize some member variables
        self.memberDefaults()
        self.Connect()
        
    def memberDefaults(self):
        self.expectHndl = None
        self.connectStringBase = "docker exec -ti "
        self.expectList = ['login:\s*$',
                           'root@\S+:.*#\s*$',
                           'bash-[0-9.]+#',
                           '[A-Za-z0-9]+#',
                            '\(config\)#',
                            '\(config-if\)#\s*$',
                            'ONIE:/\s+#\s*$',
                            'telnet: Unable to connect to remote host: Connection refused',
                            pexpect.EOF,
                            pexpect.TIMEOUT]
        
    def cmdVtysh(self, **kwargs):
        # Get into the VTYsh
        cmd = kwargs.get('command', None)
        #config = kwargs.get('config', Fa)
        
        # Get into the VTY Shell
        vtyEnterRet = self.VtyshShell()
        retCode = common.ReturnJSONGetCode(json=vtyEnterRet)
        if retCode != 0:
            common.LogOutput('error', "Unable to enter vtysh")
            return None
        else:
            common.LogOutput('debug', "Entered vtysh")
        
        retStruct = self.DeviceInteract(command=cmd)
        returnCode = retStruct.get('returnCode')
        if returnCode != 0:
            common.LogOutput('error', "Failed to send command " + cmd +" to device " + self.device)
            return None
        returnBuffer = retStruct.get('buffer')
        # Exit vtysh
        vtyExitRet = self.VtyshShell(configOption="exit")
        retCode = common.ReturnJSONGetCode(json=vtyExitRet)
        if retCode != 0:
            common.LogOutput('error', "Unable to exit vtysh")
        else:
            common.LogOutput('debug', "Exited vtysh")
        returnBuffer = retStruct.get('buffer')
        return returnBuffer
    
    # Device Connect Method
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
            common.LogOutput('error', "Failed to virtual connection for " + self.device)
            return None
        telnetString = self.connectStringBase + self.device + " /bin/bash"
        #self.expectHndl = pexpect.spawn(telnetString, echo=False)
        #self.expectHndl.delaybeforesend = .5
        expectFileString = self.device + ".log"
        ExpectInstance = switch.ExpectLog.DeviceLogger(expectFileString)
        expectLogFile = ExpectInstance.OpenExpectLog(expectFileString)
        if expectLogFile == 1 :
            common.LogOutput('error', "Unable to create expect log file")
            exit(1)
        # Opening an expect connection to the device with the specified log file
        common.LogOutput('debug', "Opening an expect connection to the device with the specified log file" + expectFileString)
        self.expectHndl = pexpect.spawn(telnetString, echo=False, logfile=switch.ExpectLog.DeviceLogger(expectLogFile))
        self.expectHndl.delaybeforesend = 1
        
        # Lets go and detect our connection - this will get us to a context we know about
        retVal = self.DetectConnection()
        if retVal is None:
            return None
            
    # DetectConnection - This will get the device in the proper context state
    def DetectConnection(self):
        bailflag = 0
        
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
                # logged-in in prompt
                bailflag = 1
                common.LogOutput("debug", "Root prompt detected:")
                connectionBuffer.append(self.expectHndl.before)
            elif index == 2:
                # Got prompt.  We should be good
                bailflag = 1
                common.LogOutput("debug", "Root prompt detected: Virtual")
                connectionBuffer.append(self.expectHndl.before)
            elif index == 3:
                common.LogOutput("debug", "vtysh prompt detected: Revert to root")
                self.expectHndl.send ('exit\r')
                connectionBuffer.append(self.expectHndl.before)
            elif index == 4:
                common.LogOutput("debug", "vtysh config prompt detected: Revert to root")
                self.expectHndl.send ('exit\r')
                connectionBuffer.append(self.expectHndl.before)
            elif index == 5:
                common.LogOutput("debug", "vtysh config interface prompt detected: Revert to root")
                self.expectHndl.send ('exit \r')
                connectionBuffer.append(self.expectHndl.before)
            elif index == 6:
                # Got ONIE prompt - reboot and get to where we need to be
                self.expectHndl.sendline("reboot")
                connectionBuffer.append(self.expectHndl.before)
            elif index == 7:
                # Got EOF
                common.LogOutput('error', "Telnet to switch failed")
                return None
            elif index == 8:
                # Got EOF
                common.LogOutput('error', "Telnet to switch failed")
                return None
            elif index == 9:
                # Got a Timeout
                common.LogOutput('error', "Connection timed out")
                return None
            else :
                connectionBuffer.append(self.expectHndl.before)
        # Append on buffer after
        connectionBuffer.append(self.expectHndl.after)
        self.expectHndl.expect(['$'], timeout=2)
        # Now lets put in the topology the expect handle
        for curLine in connectionBuffer:
            sanitizedBuffer += str(curLine)
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
                # root prompt
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
            elif index == 2:
                # Got vtysh prompts
                ErrorFlag = "CLI"
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
                #$time.sleep(2)
            elif index == 3:
                # Got bash prompt - virtual
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
            elif index == 4:
                # Got vtysh config prompts
                common.LogOutput('debug', "config prompt")
                ErrorFlag = "CLI"
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
            elif index == 5:
                # Got vtysh config interface prompts
                common.LogOutput('debug', "config interface prompt")
                ErrorFlag = "CLI"
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
            elif index == 6:
                # Got ONIE prompt - reboot and get to where we need to be
                #connection.send("reboot \r")
                ErrorFlag = "Onie"
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
            elif index == 7:
                # got EOF
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
                common.LogOutput('error', "connection closed to console")
                returnCode = 1
            elif index == 8:
                # got EOF
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
                common.LogOutput('error', "connection closed to console")
                returnCode = 1
            elif index == 9:
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
    
    def Reboot(self, **kwargs):
        common.LogOutput('info', "Reboot not supported for Virtual Switch")
        pass
        
    def VtyshShell (self, **kwargs):
        #Parameters
        configOption = kwargs.get('configOption',"config")

        returnDict = dict()
        if configOption == "config":
            #Enter vtysh shell when configOption is config
            command = "vtysh\r"
            common.LogOutput("info","Enter vtysh Shell***")
            #Get the device response buffer as json return structure here
            devIntRetStruct = self.DeviceInteract(command=command,CheckError = 'CLI')
            returnCode = devIntRetStruct.get('returnCode')
            returnDict['vtyshPrompt'] = devIntRetStruct.get('buffer')
            if returnCode != 0:
                common.LogOutput('error', "Failed to get into the vtysh shell")
                returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=returnDict)
                return returnJson

            #Enter paging command for  switch (terminal length)
            command = "terminal length 0\r"
            devIntRetStruct = self.DeviceInteract(command=command)
            returnCode = devIntRetStruct.get('returnCode')
            if returnCode != 0:
                common.LogOutput('error', "Failed to get into the vtysh shell")
                returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=devIntRetStruct)
                return returnJson
            else :
                returnDict['vtyshPrompt'] += devIntRetStruct.get('buffer')

                returnJson = common.ReturnJSONCreate(returnCode=0, data=returnDict)
                return returnJson
        else :
            #Exit vtysh shell
            common.LogOutput("debug","Vtysh shell Exit")
            command = "exit\r"
            #Get the device response buffer as json return structure here
            devIntRetStruct = self.DeviceInteract(command=command,CheckError = 'CLI')
            returnCode = devIntRetStruct.get('returnCode')
            returnDict['vtyshPrompt'] = devIntRetStruct.get('buffer')
            if returnCode != 0:
                common.LogOutput('error', "Failed to exit the vtysh shell")
                returnJson = common.ReturnJSONCreate(returnCode=returnCode, data=returnDict)
                return returnJson
            returnJson = common.ReturnJSONCreate(returnCode=0, data=returnDict)
            return returnJson


