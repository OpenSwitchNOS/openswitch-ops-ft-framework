# Topology definition
topoDict = {"topoExecution": 1000,
            "topoTarget": "dut01",
            "topoDevices": "dut01",
            "topoFilters": "dut01:system-category:switch"}

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

   # Configuring IP on the host ethernet interface
   ipAddr = "10.10.10.10"
   common.LogOutput('info', "Configuring host IP" + hName)
   retStruct = host.ConfigNetwork(connection=devConn, eth="eth1",ipAddr=ipAddr, netMask="255.255.255.0", gateway="10.10.10.1",clear=1)
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
