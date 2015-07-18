###PROC+#####################################################################
# Name:        switch.Reboot
#
# Namespace:   switch
#
# Author:      Vince Mendoza
#
# Purpose:     Logic Reboot a switch
#
# Params:      connection - expect connection handle
#              onie    - flag to boot to onie (physical only)
#
# Returns:     Dictionary with the following
#              returnCode = 0 for pass, 1 for fail
#              buffer - buffer of command
#
##PROC-#####################################################################

import pexpect
import headers
import common
import time
import switch
import xml.etree.ElementTree
import pdb 

def Reboot(**kwargs):
    connection = kwargs.get('connection')
    onie = kwargs.get('onie', False)
    device = kwargs.get('device', None)
    onieMode = kwargs.get('onieMode', "")

    # Local variables
    bailflag = 0
    retStruct = dict()
    retStruct['returnCode'] = 1
    retStruct['buffer'] = []

    if headers.topoType == "physical":
        # Send the command
        connection.send('reboot\n')
        connectionBuffer = []
        while bailflag == 0:
            # '\S+@\S+:.*#',
            index = connection.expect(['login:\s*$',
                                    'root@\S+:.*#\s*$',
                                    'GNU GRUB',
                                    'ONIE:/\s+#',
                                    pexpect.EOF,
                                    pexpect.TIMEOUT],
                                    timeout=300)
            if index == 0:
                # Need to send login string
                common.LogOutput('debug', "Saw login - logging in")
                connection.sendline("root")
                connectionBuffer.append(connection.before)
            elif index == 1:
                # Got prompt.  We should be good
                common.LogOutput('debug', "Saw prompt")
                connectionBuffer.append(connection.before)
                bailflag = 1
            elif index == 2:
                # See Grub
                common.LogOutput('debug', "Saw GRUB")
                connectionBuffer.append(connection.before)
                if onie is True:
                    common.LogOutput('debug', "Sent ONIE arrow navigation")
                    connection.send("\033[B")
                    connection.send("\033[B")
                    connection.send("\033[B")
                    connection.send("\n")
                    bailflag = 1
            elif index == 3:
                # Got ONIE prompt - reboot and get to where we need to be
                # print "Got ONIE prompt.  Rebooting device"
                # print('Got ONIE prompt, Rebooting device')
                connection.sendline("reboot")
                connectionBuffer.append(connection.before)
            elif index == 4:
                # got EOF
                bailflag = 1
                connectionBuffer.append(connection.before)
                common.LogOutput('error', "connection closed to console")
                returnCode = 1
            elif index == 5:
                # got Timeout
                bailflag = 1
                connectionBuffer.append(connection.before)
                common.LogOutput('error', "command timeout")
                returnCode = 1
            else :
                # print "Got index ", index, " wainting again"
                # print('Got index %d wainting again'.format(index))
                connectionBuffer.append(connection.before)
                connectionBuffer.append(connection.after)
        time.sleep(2)
        # Onie rescue mode for provisioning DUT via TFTP(physical)
        if onieMode == "rescue" :
            bailflag = 0
            connection.send("\033[B")
            connection.send("\n")
            expectStringList = ['Rescue mode detected.*',
                               'ONIE: Using DHCPv4 addr: eth0.*',
                               'ONIE:/ #']
            # connection.expect('Rescue mode detected.*')
            while bailflag == 0:
                index = connection.expect(expectStringList, timeout=200)
                if index == 0:
                    # Matching ONIE rescue mode command
                    common.LogOutput('debug', "Booting ONIE to Rescue Mode ***")
                    connection.send("\n")
                    connectionBuffer.append(connection.before)
                elif index == 1:
                    common.LogOutput('debug', "ONIE : DHCP address obtained to get to TFTP***")
                    connectionBuffer.append(connection.before)
                elif index == 2:
                    bailflag = 1
                    common.LogOutput('debug', "Saw ONIE Starting ONIE Service")
                    common.LogOutput("info", "===ONIE rescue prompt===")
                    connectionBuffer.append(connection.before)               

            # Takes the switch to Install OS mode in Onie 
            if onie is True and onieMode != "rescue":
                common.LogOutput('debug', "going into ONIE loop")
                bailflag = 0
                expectStringList = ['Booting `ONIE:\s+Install OS`',
                                    'ONIE:\s+Starting\s+ONIE\s+Service\s+Discovery',
                                    'ONIE:\s+Using DHCPv4 addr:',
                                    'Stopping:\s+discovery...\s+done',
                                    'ONIE:/ #']
                while bailflag == 0:
                    index = connection.expect(expectStringList, timeout=200)
                    if index == 0:
                        # Matching Booting banner
                        common.LogOutput('debug', "Saw Booting ONIE")
                        connectionBuffer.append(connection.before)
                    elif index == 1:
                        common.LogOutput('debug', "Saw ONIE Starting ONIE Service")
                        connectionBuffer.append(connection.before)
                    elif index == 2:
                        common.LogOutput('debug', "Saw ONIE DHCP Addr")
                        connectionBuffer.append(connection.before)
                        connection.send("\n")
                        connection.send("/etc/init.d/discover.sh stop\n")
                    elif index == 3:
                        common.LogOutput('debug', "Saw Discovery Stopped")
                        connectionBuffer.append(connection.before)
                        connection.send("\n")
                        connection.send("\n")
                    elif index == 4:
                        common.LogOutput('debug', "Saw prompt")
                        connectionBuffer.append(connection.before)
                        bailflag = 1

                connectionBuffer.append(connection.after)

                # Now lets put in the topology the expect handle
                santString = ""
                for curLine in connectionBuffer:  #
                    santString += curLine
                    
        return connection
    else:
        # This is for if we are a virtual setup
        # Find out what switch I am before I reboot it.
        myswitch = connection.args[3]
        switches = headers.mininetGlobal.net.switches

        for curSwitch in switches:
            if myswitch == curSwitch.container_name:
                switchObj = curSwitch
                # print switchObj
                break

        connection.send('reboot\n')
        connectionBuffer = []
        while bailflag == 0:
            # '\S+@\S+:.*#', 
            index = connection.expect([pexpect.EOF,
                                       pexpect.TIMEOUT],
                                      timeout=300)
            # index = 0
            if index == 0:
                # This means that process has died
                # Lets try to fake things out
                common.LogOutput('info', "detected virtual switch has died to to reboot - expected")
                # common.LogOutput('info', "Wainting 10 seconds")
                # time.sleep(10)
                headers.mininetGlobal.RestartSwitch(switch=myswitch)
                # Reconnect to the switch
                common.LogOutput('info', "Reconnecting to switch " + myswitch)
                dutHdl = switch.Connect(myswitch)
                bailflag = 1

        if dutHdl is None:
            return None
        return dutHdl
