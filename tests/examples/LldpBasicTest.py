import pdb
topoDict = {"topoExecution": 1000,
            "topoTarget": "dut01 dut02",
            "topoDevices": "dut01 dut02",
            "topoLinks": "lnk01:dut01:dut02",
            "topoFilters": "dut01:system-category:switch,dut02:system-category:switch"}

TEST_DESCRIPTION = "Virtual Topology / Physical Topology Sample Test"
tcInstance.tcInfo(tcName = ResultsDirectory['testcaseName'], tcDesc = TEST_DESCRIPTION)

#Defining the Test Steps
tcInstance.defineStep(stepDesc="Connect to device "+ headers.topo['dut01'])
tcInstance.defineStep(stepDesc="Show LLDP neighbor detail")

# Step 1 - connect to the first Switch
tcInstance.startStep()
dut01_conn = switch.Connect(headers.topo['dut01'])
if dut01_conn == None:
   # Means we had an issue in the connect logic
   common.LogOutput('error', "Failed to connect to device " + headers.topo['dut01'])
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
tcInstance.endStep()

#Step 2 - Show LLDP neighbor
tcInstance.startStep()
returnJsonStruct = switch.CLI.ShowLldpNeighborInfo(connection = dut01_conn,port=2)
Neighbor_Ch = common.ReturnJSONGetData(json=returnJsonStruct,dataElement="Neighbor_Info")
returnCode = common.ReturnJSONGetCode(json=returnJsonStruct)
#Insert the logical steps to evaluate the keys obtained from libraries
#No regular expression parsing should be done in the main testcase .
if returnCode != 0:
   common.LogOutput('error', "Failed to how lldp commands on "+ headers.topo['dut01'])
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
else:
   common.LogOutput('info', "Successfully showing lldp commands" + headers.topo['dut01'])
tcInstance.endStep()

