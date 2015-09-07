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
from lib import *
#from Console import Console

# This is the base class for any device - This gives the test case developer the ability to connect to the device
# along with interacting with the device
class VSwitch ( Device ):
    def __init__(self, **kwargs):
        self.topology = kwargs.get('topology', None)
        self.device = kwargs.get('device', None)
        self.noConnect = kwargs.get('noConnect', False)
        # Lets initialize some member variables
        self.memberDefaults()
        if self.noConnect is False:
            self.Connect()

    def memberDefaults(self):
        self.expectHndl = None
        self.connectStringBase = "docker exec -ti "
        self.expectList = ['login:\s*$',
                           'root@\S+:.*#\s*$',
                           'bash-[0-9.]+#',
                           '[A-Za-z0-9]+#',
                            '\(config\)#',
                            '\(config-\S+\)#\s*$',
                            'ONIE:/\s+#\s*$',
                            'telnet: Unable to connect to remote host: Connection refused',
                            pexpect.EOF,
                            pexpect.TIMEOUT]
        # Device Contexts
        # linux - assumed root
        # vtyShell
        # vtyShellConfig
        self.deviceContext = ""

    def cmdVtysh(self, **kwargs):
        # Get into the VTYsh
        cmd = kwargs.get('command', None)
        #config = kwargs.get('config', Fa)

        # Get into the VTY Shell
        vtyEnterRet = self.VtyshShell(enter=True)
        retCode = vtyEnterRet.returnCode()
        if retCode != 0:
            LogOutput('error', "Unable to enter vtysh")
            return None
        else:
            LogOutput('debug', "Entered vtysh")
        
        retStruct = self.DeviceInteract(command=cmd)
        returnCode = retStruct.get('returnCode')
        if returnCode != 0:
            LogOutput('error', "Failed to send command " + cmd +" to device " + self.device)
            return None
        returnBuffer = retStruct.get('buffer')
        # Exit vtysh
        vtyExitRet = self.VtyshShell(enter=False)
        retCode = vtyExitRet.returnCode()
        if retCode != 0:
            LogOutput('error', "Unable to exit vtysh")
        else:
            LogOutput('debug', "Exited vtysh")
        returnBuffer = retStruct.get('buffer')
        return returnBuffer

    # Device Connect Method
    def Connect(self):
        # Look up the device name in the topology - grab connectivity information
        xpathString = ".//device[name='" + self.device + "']"
        etreeElement = XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
        if etreeElement == None:
            # We are not in a good situation, we need to bail
            LogOutput('error', "Could not find device " + self.device + " in topology")
            return None
        # Code for virtual
        # Go and grab the connection name
        xpathString = ".//device[name='" + self.device + "']/connection/name"
        virtualConn = XmlGetElementsByTag(self.topology.TOPOLOGY, xpathString)
        if virtualConn == None:
            LogOutput('error', "Failed to virtual connection for " + self.device)
            return None
        telnetString = self.connectStringBase + self.device + " /bin/bash"
        #self.expectHndl = pexpect.spawn(telnetString, echo=False)
        #self.expectHndl.delaybeforesend = .5
        expectFileString = self.device + ".log"
        #ExpectInstance = switch.ExpectLog.DeviceLogger(expectFileString)
        ExpectInstance = DeviceLogger(expectFileString)
        expectLogFile = ExpectInstance.OpenExpectLog(expectFileString)
        if expectLogFile == 1 :
            LogOutput('error', "Unable to create expect log file")
            exit(1)
        # Opening an expect connection to the device with the specified log file
        LogOutput('debug', "Opening an expect connection to the device with the specified log file" + expectFileString)
        self.expectHndl = pexpect.spawn(telnetString, echo=False, logfile=DeviceLogger(expectLogFile))
        self.expectHndl.delaybeforesend = .05
        
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
                LogOutput("debug", "Login required::")
                self.expectHndl.sendline("root")
                connectionBuffer.append(self.expectHndl.before)
            elif index == 1:
                # logged-in in prompt
                bailflag = 1
                LogOutput("debug", "Root prompt detected:")
                connectionBuffer.append(self.expectHndl.before)
            elif index == 2:
                # Got prompt.  We should be good
                bailflag = 1
                LogOutput("debug", "Root prompt detected: Virtual")
                connectionBuffer.append(self.expectHndl.before)
            elif index == 3:
                LogOutput("debug", "vtysh prompt detected: Revert to root")
                self.expectHndl.send ('exit\r')
                connectionBuffer.append(self.expectHndl.before)
            elif index == 4:
                LogOutput("debug", "vtysh config prompt detected: Revert to root")
                self.expectHndl.send ('exit\r')
                connectionBuffer.append(self.expectHndl.before)
            elif index == 5:
                LogOutput("debug", "vtysh config interface prompt detected: Revert to root")
                self.expectHndl.send ('exit \r')
                connectionBuffer.append(self.expectHndl.before)
            elif index == 6:
                # Got ONIE prompt - reboot and get to where we need to be
                self.expectHndl.sendline("reboot")
                connectionBuffer.append(self.expectHndl.before)
            elif index == 7:
                # Got EOF
                LogOutput('error', "Telnet to switch failed")
                return None
            elif index == 8:
                # Got EOF
                LogOutput('error', "Telnet to switch failed")
                return None
            elif index == 9:
                # Got a Timeout
                LogOutput('error', "Connection timed out")
                return None
            else :
                connectionBuffer.append(self.expectHndl.before)
        # Append on buffer after
        connectionBuffer.append(self.expectHndl.after)
        self.expectHndl.expect(['$'], timeout=2)
        # Now lets put in the topology the expect handle
        for curLine in connectionBuffer:
            sanitizedBuffer += str(curLine)
        LogOutput('debug', sanitizedBuffer)
        self.deviceContext = "linux"
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
        #time.sleep(1)
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
                LogOutput('debug', "config prompt")
                ErrorFlag = "CLI"
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
            elif index == 5:
                # Got vtysh config interface prompts
                LogOutput('debug', "config interface prompt")
                ErrorFlag = "CLI"
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
            elif index == 6:
                # Got ONIE prompt - reboot and get to where we need to be
                #connection.send("reboot \r")
                LogOutput('debug', "Got Onie prompt")
                ErrorFlag = "Onie"
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
            elif index == 7:
                # got EOF
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
                LogOutput('error', "connection closed to console")
                returnCode = 1
            elif index == 8:
                # got EOF
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
                LogOutput('error', "connection closed to console")
                returnCode = 1
            elif index == 9:
                # got Timeout
                bailflag = 1
                connectionBuffer.append(self.expectHndl.before)
                LogOutput('error', "command timeout")
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
            LogOutput('debug', "Sent and received from device: \n" + santString + "\n")

        #The following portion checks for Errors in CLI commands
        if ErrorFlag == 'CLI' :
            #errorCheckRetStruct = switch.CLI.ErrorCheck(connection=connection, buffer=santString)
            #returnCode = errorCheckRetStruct['returnCode']
            LogOutput('debug', "NEED TO FIX")
            #The following file checks for errors in Onie prompts after analyzing Onie expect buffer
        if ErrorFlag == 'Onie' :
            #errorCheckRetStruct = switch.ErrorCheckOnie(connection=connection, buffer=santString)
            errorCheckRetStruct = self.ErrorCheckOnie(connection=self.expectHndl, buffer=santString)
            returnCode = errorCheckRetStruct['returnCode']
            LogOutput('debug', "Doing error check for Onie prompt")

        # Return dictionary
        LogOutput('debug', "Sent and received from device: \n" + santString + "\n")
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
            LogOutput('error', "Received timeout in switch.ErrorCheck")
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
        LogOutput('info', "Reboot not supported for Virtual Switch")
        pass
        
    def VtyshShell (self, **kwargs):
        #Parameters
        configOption = kwargs.get('configOption',"config")
        option = kwargs.get('enter', True)
        # Transitioning away from configOption, so option will always override
        if option is True:
            configOption = "config"
        else:
            configOption = "unconfig"
        returnDict = dict()
        overallBuffer = []
        if configOption == "config" or option is True:
            if self.deviceContext == "vtyShell":
                LogOutput('debug', "Already in vtysh context")
                returnCls = returnStruct(returnCode=0)
                return returnCls

            if self.deviceContext == "linux":
                #Enter vtysh shell when configOption is config
                command = "vtysh\r"
                LogOutput("debug","Enter vtysh Shell***")
                #Get the device response buffer as json return structure here
                devIntRetStruct = self.DeviceInteract(command=command,CheckError = 'CLI')
                returnCode = devIntRetStruct.get('returnCode')
                overallBuffer.append(devIntRetStruct.get('buffer'))
                if returnCode != 0:
                    LogOutput('error', "Failed to get into the vtysh shell")
                    bufferString = ""
                    for curLine in overallBuffer:
                        bufferString += str(curLine)
                    returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
                    return returnCls

                #Enter paging command for  switch (terminal length)
                command = "terminal length 0\r"
                devIntRetStruct = self.DeviceInteract(command=command)
                returnCode = devIntRetStruct.get('returnCode')
                overallBuffer.append(devIntRetStruct.get('buffer'))
                if returnCode != 0:
                    LogOutput('error', "Failed to get into the vtysh shell")
                    bufferString = ""
                    for curLine in overallBuffer:
                        bufferString += str(curLine)
                    returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
                    return returnCls
                else :
                    buffer = devIntRetStruct.get('buffer')
                    self.deviceContext = "vtyShell"
                    returnCls = returnStruct(returnCode=0, buffer=buffer)
                    return returnCls
            bufferString = ""
            for curLine in overallBuffer:
                bufferString += str(curLine)
            returnCls = returnStruct(returnCode=0, buffer=bufferString)
            return returnCls
        else :
            #Exit vtysh shell
            LogOutput("debug","Vtysh shell Exit")
            command = "exit\r"
            #Get the device response buffer as json return structure here
            devIntRetStruct = self.DeviceInteract(command=command,CheckError = 'CLI')
            returnCode = devIntRetStruct.get('returnCode')
            overallBuffer.append(devIntRetStruct.get('buffer'))
            #returnDict['vtyshPrompt'] = devIntRetStruct.get('buffer')
            if returnCode != 0:
                LogOutput('error', "Failed to exit the vtysh shell")
                bufferString = ""
                for curLine in overallBuffer:
                    bufferString += str(curLine)
                returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
                return returnCls
            self.deviceContext = "linux"
            bufferString = ""
            for curLine in overallBuffer:
                bufferString += str(curLine)
            returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
            return returnCls

    def ConfigVtyShell(self, **kwargs):
            #Parameters
            option = kwargs.get('enter', True)

            returnDict = dict()
            overallBuffer = []
            if option is True:
                if self.deviceContext == "vtyShellConfig":
                    LogOutput('debug', "Already in vtysh config context")
                    returnCls = returnStruct(returnCode=0)
                    return returnCls

                if self.deviceContext == "linux":
                    # Get into vtyshell
                    vtyRetStruct = self.VtyshShell(enter=True)
                    retCode = vtyRetStruct.returnCode()
                    if retCode != 0:
                        LogOutput('error', "Failed to get into the vtyshell context")
                        returnCls = returnStruct(returnCode=1)
                        return returnCls

                # Validate we are in the vtyShell context
                if self.deviceContext == "vtyShell":

                    #Enter vtysh shell when configOption is config
                    command = "config terminal\r"
                    LogOutput("debug","Enter vtysh shell config context***")
                    #Get the device response buffer as json return structure here
                    devIntRetStruct = self.DeviceInteract(command=command,CheckError = 'CLI')
                    returnCode = devIntRetStruct.get('returnCode')
                    #returnDict['vtyshPrompt'] = devIntRetStruct.get('buffer')
                    overallBuffer.append(devIntRetStruct.get('buffer'))
                    if returnCode != 0:
                        LogOutput('error', "Failed to get into the vtysh shell")
                        bufferString = ""
                        for curLine in overallBuffer:
                            bufferString += str(curLine)
                        returnCls = returnStruct(returnCode=1, buffer=bufferString)
                        return returnCls
                    else:
                        self.deviceContext = "vtyShellConfig"
                        bufferString = ""
                        for curLine in overallBuffer:
                            bufferString += str(curLine)
                        returnCls = returnStruct(returnCode=0, buffer=bufferString)
                        return returnCls
            else :
                if self.deviceContext == "vtyShellConfig":
                    #Exit vtysh shell
                    LogOutput("debug","vtysh config context exit")
                    command = "exit\r"
                    #Get the device response buffer as json return structure here
                    devIntRetStruct = self.DeviceInteract(command=command,CheckError = 'CLI')
                    returnCode = devIntRetStruct.get('returnCode')
                    #returnDict['vtyshPrompt'] = devIntRetStruct.get('buffer')
                    overallBuffer.append(devIntRetStruct.get('buffer'))
                    if returnCode != 0:
                        LogOutput('error', "Failed to exit the vtysh shell")
                        bufferString = ""
                        for curLine in overallBuffer:
                            bufferString += str(curLine)
                        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
                        return returnCls
                    self.deviceContext = "vtyShell"
                    bufferString = ""
                    for curLine in overallBuffer:
                        bufferString += str(curLine)
                    returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
                    return returnCls
                else:
                    if self.deviceContext == "vtyShell":
                        bufferString = ""
                        for curLine in overallBuffer:
                            bufferString += str(curLine)
                        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
                        return returnCls
