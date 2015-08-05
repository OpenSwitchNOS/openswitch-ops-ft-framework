# Topology definition
topoDict = {"topoExecution": 1000,
            "topoTarget": "dut01",
            "topoDevices": "dut01",
            "topoFilters": "dut01:system-category:switch"}

TEST_DESCRIPTION = "Virtual Topology / Physical Topology Sample Test"
tcInstance.tcInfo(tcName = ResultsDirectory['testcaseName'], tcDesc = TEST_DESCRIPTION)

#Defining the Test Steps
tcInstance.defineStep(stepDesc="Connect to device "+ headers.topo['dut01'])
tcInstance.defineStep(stepDesc="Onie Rescue,Provision Switch *******")

# Step 1 - connect to the first Switch
tcInstance.startStep()
dut01_conn = switch.Connect(headers.topo['dut01'])
if dut01_conn == None:
   # Means we had an issue in the connect logic
   common.LogOutput('error', "Failed to connect to device " + headers.topo['dut01'])
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
tcInstance.endStep()

#Step 2 - Provision switch
tcInstance.startStep()
returnJsonStruct = switch.SwitchProvisioning(connection=dut01_conn)
returnCode = common.ReturnJSONGetCode(json=returnJsonStruct)
if returnCode != 0:
   common.LogOutput('error', "failed to provision switch "+ headers.topo['dut01'])
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
else:
   common.LogOutput('info', "Successfully showing lldp commands" + headers.topo['dut01'])
tcInstance.endStep()

