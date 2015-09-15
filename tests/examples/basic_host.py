# Topology definition

topoDict = {"topoExecution": 1000,
            "topoTarget": "dut01 dut02",
            "topoDevices": "dut01 dut02 workstn01",
            "topoLinks": "lnk01:workstn01:dut01,lnk02:dut01:dut02",
            "topoFilters": "dut01:system-category:switch,dut02:system-category:switch"}

LogOutput('info', 'Sample test case code.')

# Grab the name of the switch from the eTree

hostElement = XmlGetElementsByTag(headers.TOPOLOGY,
        ".//device/system[category='workstation']/name",
        allElements=True)
numHosts = len(hostElement)
for hostE in hostElement:
    hName = hostE.text

   # Connect to the device

    LogOutput('info', '########################################')
    LogOutput('info', 'Connecting to host ' + hName)
    LogOutput('info', '########################################')
    devConn = opstestfw.host.Connect(hName)
    if devConn is None:
        LogOutput('error', 'Failed to connect to host ' + hName)
        continue

    linkList = [headers.topo['lnk01']]
    returnStruct = topology.LinkStatusConfig(links=linkList, enable=1)
    returnCode = ReturnJSONGetCode(json=returnStruct)
    if returnCode != 0:
        LogOutput('error', 'Failed to enable link01')

    linkList = [headers.topo['lnk02']]
    returnStruct = topology.LinkStatusConfig(links=linkList, enable=1)
    returnCode = ReturnJSONGetCode(json=returnStruct)
    if returnCode != 0:
        LogOutput('error', 'Failed to enable link02')

   # Configuring IPv4 on the host ethernet interface

    ipAddr = '20.20.20.2'
    LogOutput('info', 'Configuring host IP' + hName)
    retStruct = opstestfw.host.NetworkConfig(
        connection=devConn,
        eth='eth1',
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

    eth = 'eth1'

#   destNetwork = "30.30.30.0"

    destNetwork = '0.0.0.0'
    netMask = 24
    gateway = '20.20.20.5'

    LogOutput('info', 'Add ipv4 routes to host %s' % hName)
    retStruct = opstestfw.host.IPRoutesConfig(
        connection=devConn,
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

    ipAddr = '30.30.30.5'
    LogOutput('info', 'Pinging %s from host %s' % (ipAddr,
                     hName))
    retStruct = opstestfw.host.DevicePing(connection=devConn, ipAddr=ipAddr)
    retCode = retStruct.get('returnCode')
    retBuff = retStruct.get('buffer')
    if retCode:
        LogOutput('error', 'Failed to ping %s from host %s '
                         % (ipAddr, hName))
    else:
        LogOutput('info', 'Succeeded to ping %s from host %s '
                         % (ipAddr, hName))

    LogOutput('info', 'Delete ipv4 routes to host %s' % hName)
    retStruct = opstestfw.host.IPRoutesConfig(
        connection=devConn,
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
        connection=devConn,
        eth='eth1',
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
    retStruct = opstestfw.host.Network6Config(connection=devConn, eth='eth1',
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

    LogOutput('info', 'Get Local link addresses from host %s'
                     % hName)
    interfaceList = \
        opstestfw.host.GetDirectLocalLinkAddresses(connection=devConn, ipv6Flag=1)
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

#   print retBuff

    ipAddr = '2002::2'
    LogOutput('info', 'Pinging %s from host %s' % (ipAddr,
                     hName))
    retStruct = opstestfw.host.DevicePing(connection=devConn, ipAddr=ipAddr,
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

    ipAddr = '2001::1'

#   ipAddr = "fe80::250:56ff:febd:e5"

    LogOutput('info', 'Configuring host IP' + hName)
    retStruct = opstestfw.host.Network6Config(connection=devConn, eth='eth1',
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

    LogOutput('info', 'Delete ipv6 routes to host %s' % hName)
    retStruct = opstestfw.host.IPRoutesConfig(
        connection=devConn,
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
