# Topology definition
topoDict = {"topoExecution": 1000,
            "topoTarget": "dut01",
            "topoDevices": "dut01 wrkston01",
            "topoLinks": "lnk01:dut01:wrkston01",
            "topoFilters": "dut01:system-category:switch,wrkston01:system-category:workstation"}

TEST_DESCRIPTION = "Virtual Topology / Physical Topology Sample Test"
tcInstance.tcInfo(tcName = ResultsDirectory['testcaseName'], tcDesc = TEST_DESCRIPTION)

#Defining the Test Steps
tcInstance.defineStep(stepDesc="Port discovery")
tcInstance.defineStep(stepDesc="Connect to device "+ headers.topo['dut01'])
tcInstance.defineStep(stepDesc="Connect to device "+ headers.topo['wrkston01'])
tcInstance.defineStep(stepDesc="Enable Links ")
tcInstance.defineStep(stepDesc="Fan and show ovs information using OVS commands on "+ headers.topo['dut01'])
tcInstance.defineStep(stepDesc="Fan and show ovs information using OVS commands on "+ headers.topo['wrkston01'])

# Step 1 - physical port discovery
tcInstance.startStep()
dut01LinkStruct = topology.InterfaceGetByDeviceLink(device=headers.topo['dut01'], link=headers.topo['lnk01'])
dut01Port = ReturnJSONGetData(json=dut01LinkStruct)
dut02LinkStruct = topology.InterfaceGetByDeviceLink(device=headers.topo['wrkston01'], link=headers.topo['lnk01'])
dut02Port = ReturnJSONGetData(json=dut02LinkStruct)
tcInstance.endStep()

tcInstance.startStep()
dut01_conn = opstestfw.switch.Connect(headers.topo['dut01'])
if dut01_conn == None:
   # Means we had an issue in the connect logic
   LogOutput('error', "Failed to connect to device " + headers.topo['dut01'])
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)

# Configure bridge on this device
LogOutput('info', "Rebooting device " + headers.topo['dut01'])
dut01_conn = opstestfw.switch.Reboot(connection=dut01_conn)
dut01BridgeRetVal = opstestfw.switch.OVS.OvsBridgeConfig(connection=dut01_conn,ports=dut01Port)
tcInstance.endStep()


# Step 2 - connect to the Second Switch
tcInstance.startStep()
wrkston01_conn = opstestfw.host.Connect(headers.topo['wrkston01'])
# Grab the name of the switch from the eTree

hostElement = XmlGetElementsByTag(headers.TOPOLOGY,
        ".//device/system[category='workstation']/name",
        allElements=True)
numHosts = len(hostElement)
hName = "TestHost"

for hostE in hostElement:
    hName = hostE.text

# Configuring IPv4 on the host ethernet interface

ipAddr = '20.20.20.2'
LogOutput('info', 'Configuring host IP' + hName)
retStruct = opstestfw.host.NetworkConfig(
        connection=wrkston01_conn,
        eth='eth0',
        ipAddr=ipAddr,
        netMask='255.255.255.0',
        broadcast='20.20.20.1',
        clear=0,
        )
retCode = retStruct.get('returnCode')
retBuff = retStruct.get('buffer')
if retCode:
    LogOutput('error',
                         'Failed to configure IP %s on  host %s '
                         % (ipAddr, hName))
else:
    LogOutput('info',
                         'Succeeded in configuring IP  %s on host %s '
                         % (ipAddr, hName))

eth = 'eth0'

#   destNetwork = "30.30.30.0"

destNetwork = '0.0.0.0'
netMask = 24
gateway = '20.20.20.5'

LogOutput('info', 'Add ipv4 routes to host %s' % hName)
retStruct = opstestfw.host.IPRoutesConfig(
        connection=wrkston01_conn,
        routeOperation='add',
        destNetwork=destNetwork,
        netMask=netMask,
        via=gateway,
        eth=eth,
        metric=1,
        ipv6Flag=0,
        )
retCode = retStruct.get('returnCode')
retBuff = retStruct.get('buffer')
if retCode:
    LogOutput('error', 'Failed to add ipv4 route to host %s '
                          % hName)
else:
    LogOutput('info',
                         'Succeeded in adding ipv4 route to host %s '
                         % hName)

ipAddr = '20.20.20.2'
LogOutput('info', 'Pinging %s from host %s' % (ipAddr,
                     hName))
retStruct = opstestfw.host.DevicePing(connection=wrkston01_conn, ipAddr=ipAddr)
retCode = retStruct.get('returnCode')
retBuff = retStruct.get('buffer')
if retCode:
    LogOutput('error', 'Failed to ping %s from host %s '
                         % (ipAddr, hName))
else:
    LogOutput('info', 'Succeeded to ping %s from host %s '
                         % (ipAddr, hName))

opstestfw.host.DeviceInteract(connection=wrkston01_conn,command="ifconfig")
LogOutput('info', 'Delete ipv4 routes to host %s' % hName)
retStruct = opstestfw.host.IPRoutesConfig(
        connection=wrkston01_conn,
        routeOperation='delete',
        destNetwork=destNetwork,
        netMask=netMask,
        via=gateway,
        eth=eth,
        metric=1,
        ipv6Flag=0,
        )
retCode = retStruct.get('returnCode')
retBuff = retStruct.get('buffer')
if retCode:
    LogOutput('error',
                         'Failed to delete ipv4 route to host %s '
                         % hName)
else:
    LogOutput('info',
                         'Succeeded in deleting ipv4 route to host %s '
                         % hName)

# Clearing IPv4 on the host ethernet interface

ipAddr = '20.20.20.2'
LogOutput('info', 'Clearing host IP' + hName)
retStruct = opstestfw.host.NetworkConfig(
        connection=wrkston01_conn,
        eth='eth0',
        ipAddr=ipAddr,
        netMask='255.255.255.0',
        broadcast='20.20.20.5',
        clear=1,
        )
retCode = retStruct.get('returnCode')
retBuff = retStruct.get('buffer')
if retCode:
    LogOutput('error',
                         'Failed to configure IP %s on  host %s '
                         % (ipAddr, hName))
else:
    LogOutput('info',
                         'Succeeded in configuring IP  %s on host %s '
                         % (ipAddr, hName))

# Configuring IPv6 on the host ethernet interface

ipAddr = '2001::1'
LogOutput('info', 'Configuring host IP' + hName)
retStruct = opstestfw.host.Network6Config(connection=wrkston01_conn, eth='eth0',
                                    ipAddr=ipAddr, netMask=64, clear=0)
retCode = retStruct.get('returnCode')
retBuff = retStruct.get('buffer')
if retCode:
    LogOutput('error',
                         'Failed to configure IPv6 %s on  host %s '
                         % (ipAddr, hName))
else:
    LogOutput('info',
                         'Succeeded in configuring IPv6  %s on host %s '
                          % (ipAddr, hName))
'''
LogOutput('info', 'Get Local link addresses from host %s'
                     % hName)
interfaceList = \
        opstestfw.host.GetDirectLocalLinkAddresses(connection=wrkston01_conn, ipv6Flag=1)
localLinkAddress = interfaceList[0]['address']
eth = interfaceList[0]['eth']
LogOutput('info', 'Add routes to host %s' % hName)
retStruct = opstestfw.host.IPRoutesConfig(
        connection=devConn,
        routeOperation='add',
        destNetwork='2002::',
        netMask=64,
        via=localLinkAddress,
        eth=eth,
        metric=1,
        ipv6Flag=1,
        )
retCode = retStruct.get('returnCode')
retBuff = retStruct.get('buffer')
if retCode:
    LogOutput('error', 'Failed to add ipv6 route to host %s '
                          % hName)
else:
    LogOutput('info',
                         'Succeeded in adding ipv6 route to host %s '
                         % hName)

print retBuff
'''
#   print retBuff

ipAddr = '2001::1'
LogOutput('info', 'Pinging %s from host %s' % (ipAddr,
                     hName))
retStruct = opstestfw.host.DevicePing(connection=wrkston01_conn, ipAddr=ipAddr,
                                ipv6Flag=1)
retCode = retStruct.get('returnCode')
retBuff = retStruct.get('buffer')
if retCode:
    LogOutput('error', 'Failed to ping %s from host %s '
                         % (ipAddr, hName))
else:
    LogOutput('info', 'Succeeded to ping %s from host %s '
                         % (ipAddr, hName))
print retBuff

opstestfw.host.DeviceInteract(connection=wrkston01_conn,command="ifconfig")
ipAddr = '2001::1'

#   ipAddr = "fe80::250:56ff:febd:e5"

LogOutput('info', 'Configuring host IP' + hName)
retStruct = opstestfw.host.Network6Config(connection=wrkston01_conn, eth='eth0',
                                    ipAddr=ipAddr, netMask=64, clear=1)
retCode = retStruct.get('returnCode')
retBuff = retStruct.get('buffer')
if retCode:
    LogOutput('error', 'Failed to clear IPv6 %s on  host %s '
                          % (ipAddr, hName))
else:
    LogOutput('info',
                         'Succeeded in clearing IPv6  %s on host %s '
                         % (ipAddr, hName))
'''
LogOutput('info', 'Delete ipv6 routes to host %s' % hName)
retStruct = opstestfw.host.IPRoutesConfig(
        connection=wrkston01_conn,
        routeOperation='delete',
        destNetwork='2002::',
        netMask=64,
        via=localLinkAddress,
        eth=eth,
        metric=1,
        ipv6Flag=1,
        )
retCode = retStruct.get('returnCode')
retBuff = retStruct.get('buffer')
if retCode:
    LogOutput('error',
                         'Failed to delete ipv6 route to host %s '
                         % hName)
else:
    LogOutput('info',
                         'Succeeded in deleting ipv6 route to host %s '
                         % hName)
print retBuff
'''
opstestfw.host.DeviceInteract(connection=wrkston01_conn,command="ifconfig")
# if wrkston01_conn == None:
#    LogOutput('error', "Failed to connect to device " + headers.topo['dut02'])
#    tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
# dut01BridgeRetVal = opstestfw.switch.OVS.OvsBridgeConfig(connection=dut02_conn,ports=dut02Port)
tcInstance.endStep()

tcInstance.startStep()
linkList = [headers.topo['lnk01']]
returnStruct = topology.LinkStatusConfig(links=linkList, enable=1)
returnCode = ReturnJSONGetCode(json=returnStruct)
if returnCode != 0:
   LogOutput('error', "Failed to enable links")
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
tcInstance.endStep()
# Waiting some time for the switch to come up
Sleep(seconds=25, message="Waiting for switch processes to fully come up")

# Step 3 - ovs-vsctl show on the first switch
tcInstance.startStep()
# Run a command
LogOutput('info', "Running an ovs-vsctl show on dut01")
retStruct = opstestfw.switch.OVS.OvsShow(connection=dut01_conn)
retCode = ReturnJSONGetCode(json=retStruct)
if retCode != 0:
   LogOutput('error', "Failed to retrieve ovs-vsctl show output from dut01")
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_CONTINUE)
else:
   #data = ReturnJSONGetData(json=retStruct)
   LogOutput('info', "ovs-vsctl output for dut01:\n" + retStruct)
tcInstance.endStep()


# Step 4 - ovs-vsctl show on the second switch
tcInstance.startStep()
LogOutput('info', "Running ifconfig on wrkston01")
retStruct = opstestfw.host.DeviceInteract(connection=wrkston01_conn,command="ifconfig")
retCode = retStruct['returnCode']
ifconfigBuffer = retStruct['buffer']
if retCode != 0:
   LogOutput('error', "Failed to run ifconfig on wrkston01")
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_CONTINUE)
else:

   LogOutput('info', "ifconfig data on wrkston01:\n" + ifconfigBuffer)

tcInstance.endStep()

