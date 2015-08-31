topoDict = {"topoDevices": "dut01 wrkston01 wrkston02",
            "topoLinks": "lnk01:dut01:wrkston01,lnk02:dut01:wrkston02",
            "topoFilters": "dut01:system-category:switch,wrkston01:system-category:workstation,wrkston02:system-category:workstation"}

#
dut01_conn = switch.Connect(headers.topo['dut01'])
if dut01_conn is None:
   LogOutput('error', "Failed to connect to dut01")
   exit(1)

wrkston01_conn = switch.Connect(headers.topo['wrkston01'])
if wrkston01_conn is None:
   LogOutput('error', "Failed to connect to wrkston01")
   exit(1)

wrkston02_conn = switch.Connect(headers.topo['wrkston02'])
if wrkston02_conn is None:
   LogOutput('error', "Failed to connect to wrkston02")
   exit(1)



Sleep(seconds=30, message="Waiting for switch processes to fully come up")

# Grag interfaces
dut01Lnk1PortStruct = topology.InterfaceGetByDeviceLink(device=headers.topo['dut01'], link=headers.topo['lnk01'])

dut01Lnk1Port = ReturnJSONGetData(json=dut01Lnk1PortStruct)

dut01Lnk2PortStruct = topology.InterfaceGetByDeviceLink(device=headers.topo['dut01'], link=headers.topo['lnk02'])
dut01Lnk2Port = ReturnJSONGetData(json=dut01Lnk2PortStruct)

retStruct = switch.OVS.OvsBridgeConfig(connection=dut01_conn, bridge="br0", action='config', ports=[dut01Lnk1Port, dut01Lnk2Port])

retStruct = switch.OVS.OvsVlanConfig(connection=dut01_conn, bridge="br0", vlans="1")

LogOutput('info', "\n\nRunning ovs-vsctl show on dut01")
retStruct = switch.OVS.OvsShow(connection=dut01_conn)
retCode = ReturnJSONGetCode(json=retStruct)
if retCode != 0:
   LogOutput('error', "Failed to retrieve ovs-vsctl show output from dut01")
else:
   #data = ReturnJSONGetData(json=retStruct)
   LogOutput('info', "ovs-vsctl output for dut01:\n" + retStruct)

LogOutput('info', "\n\nRunning ifconfig on wrkston01")
retStruct = switch.DeviceInteract(connection=wrkston01_conn,command="ifconfig")
retCode = retStruct['returnCode']
if retCode != 0:
   LogOutput('error', "Failed to run ifconfig on workston01")
else:
   buffer = retStruct['buffer']
   LogOutput('info', "Rans ifconfig on wrkston01:\n"+ str(buffer))

LogOutput('info', "\n\nRunning ifconfig on wrkston02")
retStruct = switch.DeviceInteract(connection=wrkston02_conn,command="ifconfig")
retCode = retStruct['returnCode']
if retCode != 0:
   LogOutput('error', "Failed to run ifconfig on workston02")
else:
   buffer = retStruct['buffer']
   LogOutput('info', "Rans ifconfig on wrkston01:\n"+ str(buffer))


retStruct = switch.DeviceInteract(connection=wrkston01_conn, command="ping -c 5 10.0.0.2")
print retStruct

LogOutput('info', "Tearing down virtual environment")
mytopo.terminate_nodes()
