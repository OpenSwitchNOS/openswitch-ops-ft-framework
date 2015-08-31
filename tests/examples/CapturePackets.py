#Sample test case to demonstrate packet capture
#Topology definition
#Topology : TwoDUT's , One workstation
topoDict = {"topoExecution": 1000,
            "topoTarget": "dut01",
            "topoDevices": "dut01 dut02 wrkston01",
            "topoLinks": "lnk01:dut01:dut02,lnk02:dut01:wrkston01",
            "topoFilters": "dut01:system-category:switch,dut02:system-category:switch,wrkston01:system-category:workstation"}

TEST_DESCRIPTION = "LLDP packet capture"
tcInstance.tcInfo(tcName = ResultsDirectory['testcaseName'], tcDesc = TEST_DESCRIPTION)

#Defining the Test Steps
tcInstance.defineStep(stepDesc="Port discovery") 
tcInstance.defineStep(stepDesc="Connect to device "+ headers.topo['dut01'])
tcInstance.defineStep(stepDesc="Enable Links")
tcInstance.defineStep(stepDesc="Capture and parse LLDP packets on the workstation")

# Step 1 - Port Discovery (Physical)
tcInstance.startStep()
dut01LinkStruct = topology.InterfaceGetByDeviceLink(device=headers.topo['dut01'], link=headers.topo['lnk01'])
dut01Port = ReturnJSONGetData(json=dut01LinkStruct)
dut02LinkStruct = topology.InterfaceGetByDeviceLink(device=headers.topo['dut01'], link=headers.topo['lnk02'])
dut02Port = ReturnJSONGetData(json=dut02LinkStruct)
tcInstance.endStep()

# Step 2 - Connect to the workstation
tcInstance.startStep()
LogOutput('info', "##Connecting to host "+ headers.topo['wrkston01'])
wrkston01Conn = host.Connect(headers.topo['wrkston01'])
if wrkston01Conn is None :
   LogOutput('error', "Failed to connect to host " + headers.topo['wrkston01'])
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
tcInstance.endStep()
 
#Step 3 : Enable all the links
tcInstance.startStep()
linkList = [headers.topo['lnk01'],headers.topo['lnk02']]
returnStruct = topology.LinkStatusConfig(links=linkList, enable=1)
returnCode = ReturnJSONGetCode(json=returnStruct)
if returnCode != 0:
   LogOutput('error', "Failed to enable links")
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
tcInstance.endStep()

#Step 4 Capture LLDP packets
#Packet Capture
tcInstance.startStep()
pktInstance = host.PacketCapture(headers.topo['wrkston01'],"capture.pcap")
#Filter can be passed as an optional argument
#pktInstance.StartCapture(connection=wrkston01Conn,filter="lldp")
pktInstance.StartCapture(connection=wrkston01Conn)
Sleep(seconds=40, message="Waiting for LLDP packets to be captured")
returnStruct = pktInstance.ParseCapture(wrkston01Conn)
LogOutput("info", "Return Json structure for LLDP packets captures")
LogOutput("info",returnStruct)
returnCode = ReturnJSONGetCode(json=returnStruct)
if returnCode != 0 :
   LogOutput('error', "Failed to parse packets on the host " + headers.topo['wrkston01'])
   tcInstance.setVerdictAction (TC_STEPVERDICT_FAIL, TC_STEPFAILACTION_EXIT)
tcInstance.endStep()
 
