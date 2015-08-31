# Topology definition
topoDict = {"topoExecution": 1000,
            "topoTarget": "dut01",
            "topoDevices": "dut01",
            "topoFilters": "dut01:system-category:switch"}

#The base class for test case flow control is -> tcAction
#Modify the test case description below :
TEST_DESCRIPTION = "Connecting to the Halon Switch and use OVS commands to display output"
tcInstance.tcInfo(tcName = ResultsDirectory['testcaseName'], tcDesc = TEST_DESCRIPTION)

#Defining the Test Steps
tcInstance.defineStep(stepDesc="Parse Topology XML to extract Edge core switch devices")
tcInstance.defineStep(stepDesc="Connect to the device in the topology")
tcInstance.defineStep(stepDesc="Issue Reboot command to the switch in topology")
tcInstance.defineStep(stepDesc="Configure VLAN on the switch")
tcInstance.defineStep(stepDesc="Fan and show ovs information using OVS commands")
tcInstance.defineStep(stepDesc="Testcase Cleanup")

#Step 1: Parse Topology XML to extract Edge core switch devices
tcInstance.startStep()

# Grab the name of the switch from the eTree
switchElement = XmlGetElementsByTag(headers.TOPOLOGY, ".//device/system[vendor='Edgecore']/name", allElements=True)
if switchElement is None :
        LogOutput('error', "Failed to Parse Topology XML to extract Edge core switch devices ")
        tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)

tcInstance.endStep()

#Step 2: Connect to Halon Device
tcInstance.startStep()
numSwitches = len(switchElement)
for switchE in switchElement:
   switchName = switchE.text

devConn = switch.Connect(switchName)
if devConn is None:
        LogOutput('error', "Failed to connect to switch " + switchName)
        tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)

tcInstance.tcDevConn = devConn

tcInstance.endStep()

#Step 3: Issue Reboot command to the switch in topology
tcInstance.startStep()
retStruct = switch.Reboot(connection=devConn)
returnCode = retStruct.get('returnCode')
if returnCode != 0:
   LogOutput('error', "Failed to reboot switch " + switchName)
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
else:
   LogOutput('info', "Successfully rebooted switch " + switchName)

tcInstance.endStep()

#Step 4: Configure VLAN on the switch
tcInstance.startStep()
# Creating OVS Bridge
retStruct = switch.OVS.OvsBridgeConfig(connection=devConn, bridge="br0", action='config', ports=[1, 2, 3])
returnCode = ReturnJSONGetCode(json=retStruct)
if returnCode != 0:
   LogOutput('error', "Failed to configure OVS bridge " + bridge)
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
else:
   LogOutput('info', "Successfully configured OVS bridge on the switch " + switchName)

#Configuring a VLAN
vlanList = [7]
retStruct = switch.OVS.OvsVlanConfig(connection=devConn, bridge="br0", vlans=vlanList)
returnCode = ReturnJSONGetCode(json=retStruct)
if returnCode != 0:
   LogOutput('error', "Failed to configure VLAN on" + bridge)
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
else:
   LogOutput('info', "Successfully VLAN configured on the switch " + switchName)

tcInstance.endStep()

#Step 5 : OVS Show commands
tcInstance.startStep()
mystruct = switch.OVS.OvsShow(connection=devConn)
retCode = ReturnJSONGetCode(json=mystruct)
uuid = ReturnJSONGetData(json=mystruct, dataElement="Open_vSwitch_UUID")
LogOutput('info', "Open VSwitch UUID:" + str(uuid))
fanInfo = ReturnJSONGetData(json=mystruct, dataElement='Fans')
LogOutput('info', "Fan Information")
fans = fanInfo.keys()
for curFan in fans:
   curDict = fanInfo[curFan]
   status = curDict['status']
   rpm = curDict['rpm']
   speed = curDict['speed']
   LogOutput('info', "\tCurrent Fan " + curFan + " status:" + str(status) + " speed:" + str(speed) + " rpm:" + str(rpm))
tcInstance.endStep()


#Step 6: Testcase Cleanup
tcInstance.startStep()

retStruct = switch.Reboot(connection=devConn)
returnCode = retStruct.get('returnCode')
if returnCode != 0:
   LogOutput('error', "Failed to reboot switch " + switchName)
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
else:
   LogOutput('info', "Successfully rebooted switch " + switchName)
tcInstance.endStep()

