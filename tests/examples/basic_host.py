# Topology definition
topoDict = {"topoExecution": 1000,
            "topoTarget": "dut01 dut02",
            "topoDevices": "dut01 dut02 workstn01",
            "topoLinks": "lnk01:workstn01:dut01,lnk02:dut01:dut02",
            "topoFilters": "dut01:system-category:switch,dut02:system-category:switch"}

common.LogOutput("info", "Sample test case code.")

# Grab the name of the switch from the eTree
hostElement = common.XmlGetElementsByTag(headers.TOPOLOGY, ".//device/system[category='workstation']/name", allElements=True)
numHosts = len(hostElement)
for hostE in hostElement:
   hName = hostE.text
   # Connect to the device
   common.LogOutput('info', "########################################")
   common.LogOutput('info', "Connecting to host " + hName)
   common.LogOutput('info', "########################################")
   devConn = host.Connect(hName)
   if devConn is None:
      common.LogOutput('error', "Failed to connect to host " + hName)
      continue


   linkList = [headers.topo['lnk01']]
   returnStruct = topology.LinkStatusConfig(links=linkList, enable=1)
   returnCode = common.ReturnJSONGetCode(json=returnStruct)
   if returnCode != 0:
      common.LogOutput('error', "Failed to enable link01")

   linkList = [headers.topo['lnk02']]
   returnStruct = topology.LinkStatusConfig(links=linkList, enable=1)
   returnCode = common.ReturnJSONGetCode(json=returnStruct)
   if returnCode != 0:
      common.LogOutput('error', "Failed to enable link02")

   # Configuring IPv4 on the host ethernet interface
   '''
   ipAddr = "10.10.10.10"
   common.LogOutput('info', "Configuring host IP" + hName)
   retStruct = host.ConfigNetwork(connection=devConn, eth="eth1",ipAddr=ipAddr, netMask="255.255.255.0", gateway="10.10.10.1",clear=0)
   retCode = retStruct.get('returnCode')
   retBuff = retStruct.get('buffer')
   if retCode:
      common.LogOutput('error', "Failed to configure IP %s on  host %s " %(ipAddr, hName))
   else:
      common.LogOutput('info', "Succeeded in configuring IP  %s on host %s " %(ipAddr, hName))
   common.LogOutput('info', "Pinging %s from host %s"%(ipAddr, hName))
   retStruct = host.PingDevice(connection=devConn, ipAddr=ipAddr)
   retCode = retStruct.get('returnCode')
   retBuff = retStruct.get('buffer')
   if retCode:
      common.LogOutput('error', "Failed to ping %s from host %s " %(ipAddr, hName))
   else:
      common.LogOutput('info', "Succeeded to ping %s from host %s " %(ipAddr, hName))
   '''
   # Configuring IPv6 on the host ethernet interface
   ipAddr = "2001::1"
#   ipAddr = "fe80::250:56ff:febd:e5"
   common.LogOutput('info', "Configuring host IP" + hName)
   retStruct = host.Config6Network(connection=devConn, eth="eth1",ipAddr=ipAddr, netMask=64, clear=0)
   retCode = retStruct.get('returnCode')
   retBuff = retStruct.get('buffer')
   if retCode:
      common.LogOutput('error', "Failed to configure IPv6 %s on  host %s " %(ipAddr, hName))
   else:
      common.LogOutput('info', "Succeeded in configuring IPv6  %s on host %s " %(ipAddr, hName))
#   print retBuff
   ipAddr = "2002::1"
   common.LogOutput('info', "Pinging %s from host %s"%(ipAddr, hName))
   retStruct = host.PingDevice(connection=devConn, ipAddr=ipAddr, ipv6Flag=1)
   retCode = retStruct.get('returnCode')
   retBuff = retStruct.get('buffer')
   if retCode:
      common.LogOutput('error', "Failed to ping %s from host %s " %(ipAddr, hName))
   else:
      common.LogOutput('info', "Succeeded to ping %s from host %s " %(ipAddr, hName))
   print retBuff
   ipAddr = "2001::1"
#   ipAddr = "fe80::250:56ff:febd:e5"
   common.LogOutput('info', "Configuring host IP" + hName)
   retStruct = host.Config6Network(connection=devConn, eth="eth1",ipAddr=ipAddr, netMask=64, clear=1)
   retCode = retStruct.get('returnCode')
   retBuff = retStruct.get('buffer')
   if retCode:
      common.LogOutput('error', "Failed to clear IPv6 %s on  host %s " %(ipAddr, hName))
   else:
      common.LogOutput('info', "Succeeded in clearing IPv6  %s on host %s " %(ipAddr, hName))

