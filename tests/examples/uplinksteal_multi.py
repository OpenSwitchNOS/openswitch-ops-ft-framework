import RTL
# Topology definition
topoDict = {"topoExecution": 1000,
            "topoTarget": "dut01",
            "topoDevices": "dut01 dut02 wrkston01 wrkston02",
            "topoLinks": "lnk01:dut01:wrkston01,lnk02:dut02:wrkston02",
            "topoFilters": "dut01:system-category:switch,dut02:system-category:switch,wrkston01:system-category:workstation,wrkston02:system-category:workstation"}

#Defining the Test Steps
tcInstance.defineStep(stepDesc="Connect to device "+ headers.topo['dut01'])
tcInstance.defineStep(stepDesc="Steal link from the  device "+ headers.topo['dut01'])
tcInstance.defineStep(stepDesc="Restore stolen link to the device "+ headers.topo['dut01'])

switchName = headers.topo['dut01']
tcInstance.startStep()
dut01_conn = opstestfw.switch.Connect(headers.topo['dut01'])
if dut01_conn == None:
   LogOutput('error', "Failed to connect to device " + headers.topo['dut01'])
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
dut02_conn = opstestfw.switch.Connect(headers.topo['dut02'])
if dut02_conn == None:
   LogOutput('error', "Failed to connect to device " + headers.topo['dut02'])
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
tcInstance.endStep()

tcInstance.startStep()
BuildProvisionLinkHandle = RTL.BuildProvisionUplink()
LogOutput('info', "Stealing a link from the switch " + switchName)
retStruct = BuildProvisionLinkHandle.BuildProvisionLinkSteal(device=switchName)
retCode = ReturnJSONGetCode(json=retStruct)
if retCode != 0:
   LogOutput('error', "Failed to steal link from dut01")
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_CONTINUE)
else:
   LogOutput('info', "stole link from dut01:\n" + retStruct)

switchName = headers.topo['dut02']
LogOutput('info', "Stealing a link from the switch " + switchName)
retStruct = BuildProvisionLinkHandle.BuildProvisionLinkSteal(device=switchName)
retCode = ReturnJSONGetCode(json=retStruct)
if retCode != 0:
   LogOutput('error', "Failed to steal link from dut01")
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_CONTINUE)
else:
   LogOutput('info', "stole link from dut01:\n" + retStruct)
tcInstance.endStep()

tcInstance.startStep()
switchName = headers.topo['dut01']
LogOutput('info', "Restoring Stolen link from the switch " + switchName)
retStruct = BuildProvisionLinkHandle.BuildProvisionLinkRestore(device=switchName)
retCode = ReturnJSONGetCode(json=retStruct)
if retCode != 0:
   LogOutput('error', "Failed to restore stole link from dut01")
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_CONTINUE)
else:
   LogOutput('info', "Restored stolen link from dut01:\n" + retStruct)
switchName = headers.topo['dut02']
LogOutput('info', "Restoring Stolen link from the switch " + switchName)
retStruct = BuildProvisionLinkHandle.BuildProvisionLinkRestore(device=switchName)
retCode = ReturnJSONGetCode(json=retStruct)
if retCode != 0:
   LogOutput('error', "Failed to restore stole link from dut01")
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_CONTINUE)
else:
   LogOutput('info', "Restored stolen link from dut01:\n" + retStruct)
tcInstance.endStep()
