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
dut01_conn = switch.Connect(headers.topo['dut01'])
if dut01_conn == None:
   # Means we had an issue in the connect logic
   LogOutput('error', "Failed to connect to device " + headers.topo['dut01'])
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)

# Configure bridge on this device
LogOutput('info', "Rebooting device " + headers.topo['dut01'])
dut01_conn = switch.Reboot(connection=dut01_conn)
dut01BridgeRetVal = switch.OVS.OvsBridgeConfig(connection=dut01_conn,ports=dut01Port)
tcInstance.endStep()


# Step 2 - connect to the Second Switch
tcInstance.startStep()
wrkston01_conn = host.Connect(headers.topo['wrkston01'])
host.DeviceInteract(connection=wrkston01_conn,command="ifconfig")
# if wrkston01_conn == None:
#    LogOutput('error', "Failed to connect to device " + headers.topo['dut02'])
#    tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
# dut01BridgeRetVal = switch.OVS.OvsBridgeConfig(connection=dut02_conn,ports=dut02Port)
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
retStruct = switch.OVS.OvsShow(connection=dut01_conn)
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
retStruct = host.DeviceInteract(connection=wrkston01_conn,command="ifconfig")
retCode = retStruct['returnCode']
ifconfigBuffer = retStruct['buffer']
if retCode != 0:
   LogOutput('error', "Failed to run ifconfig on wrkston01")
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_CONTINUE)
else:

   LogOutput('info', "ifconfig data on wrkston01:\n" + ifconfigBuffer)

tcInstance.endStep()

