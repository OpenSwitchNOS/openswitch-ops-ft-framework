

# Topology definition
topoDict = {"topoExecution": 1000,
            "topoTarget": "dut01",
            "topoDevices": "dut01 wrkston01",
            "topoLinks": "lnk01:dut01:wrkston01",
            "topoFilters": "dut01:system-category:switch,wrkston01:system-category:workstation"}

# Test object will parse command line and formulate the env
testObj = testEnv(topoDict=topoDict)
# Temporary - this needs to be moved into the testEnv code
testObj.ResultsDirectory['testcaseName'] = "virutaltopo_bat2_new.py"
tcInstance = tcAction()

# Get topology object
topoObj = testObj.topoObjGet()
dut01Obj = topoObj.deviceObjGet(device="dut01")
wrkston01Obj = topoObj.deviceObjGet(device="wrkston01")

# Test case definition
TEST_DESCRIPTION = "Virtual Topology / Physical Topology Sample Test"
tcInstance.tcInfo(tcName = testObj.ResultsDirectory['testcaseName'], tcDesc = TEST_DESCRIPTION)
#Defining the Test Steps
tcInstance.defineStep(stepDesc="Reboot Switch "+ dut01Obj.device)
tcInstance.defineStep(stepDesc="Fan and show ovs information using OVS commands on "+ dut01Obj.device)
tcInstance.defineStep(stepDesc="Running ifconfig on  "+ wrkston01Obj.device)

tcInstance.startStep()
dut01Obj.Reboot()
tcInstance.endStep()

tcInstance.startStep()
# Run a command
LogOutput('info', "Running an ovs-vsctl show on dut01")
retStruct = dut01Obj.DeviceInteract(command="ovs-vsctl show")
retCode = retStruct.get('returnCode')
if retCode != 0:
    LogOutput('error', "Failed to retrieve ovs-vsctl show output from dut01")
    tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_CONTINUE)
else:
    mybuffer = retStruct.get('buffer')
    LogOutput('info', "ovs-vsctl output for dut01:\n" + mybuffer)
tcInstance.endStep()


# Step 4 - ovs-vsctl show on the second switch
tcInstance.startStep()
LogOutput('info', "Running ifconfig on wrkston01")
retStruct = wrkston01Obj.DeviceInteract(command="ifconfig")
retCode = retStruct['returnCode']
ifconfigBuffer = retStruct['buffer']
if retCode != 0:
    LogOutput('error', "Failed to run ifconfig on wrkston01")
    tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_CONTINUE)
else:
    LogOutput('info', "ifconfig data on wrkston01:\n" + ifconfigBuffer)

tcInstance.endStep()

topoObj.terminate_nodes()
