topoDict = {"topoExecution": 1000,
            "topoTarget": "dut01 dut02",
            "topoDevices": "dut01 dut02", 
            "topoLinks": "lnk01:dut01:dut01", 
            "topoFilters": "dut01:system-category:switch,dut02:system-category:switch"}

common.LogOutput("info", "Sample test case code.")

# Grab the name of the switch from the eTree
switchElement = common.XmlGetElementsByTag(headers.TOPOLOGY, ".//device/system[vendor='Edgecore']/name", allElements=True)
numSwitches = len(switchElement)
for switchE in switchElement:
   switchName = switchE.text
   # Connect to the device
   common.LogOutput('info', "########################################")
   common.LogOutput('info', "Connecting to switch " + switchName)
   common.LogOutput('info', "########################################")
   devConn = switch.Connect(switchName)
   if devConn is None:
      common.LogOutput('error', "Failed to connect to switch " + switchName)
      continue
   
   # Rebooting switch
   common.LogOutput('info', "Rebooting switch " + switchName)
   retStruct = switch.Reboot(connection=devConn)
   retCode = retStruct.get('returnCode')
   if retCode != 0:
      common.LogOutput('error', "Failed to reboot switch " + switchName)
   else:
      common.LogOutput('info', "Successfully rebooted switch " + switchName)
   # Do vlan create
   retStruct = switch.OVS.OvsBridgeConfig(connection=devConn, bridge="br0", action='config', ports=[1, 2, 3])
   
   vlanList = [1]
   retStruct = switch.OVS.OvsVlanConfig(connection=devConn, bridge="br0", vlans=vlanList)
   

   # OvsShow
   mystruct = switch.OVS.OvsShow(connection=devConn)
   retCode = common.ReturnJSONGetCode(json=mystruct)
   print mystruct
   uuid = common.ReturnJSONGetData(json=mystruct, dataElement="Open_vSwitch_UUID")
   common.LogOutput('info', "Open VSwitch UUID:" + str(uuid))
   fanInfo = common.ReturnJSONGetData(json=mystruct, dataElement='Fans')
   common.LogOutput('info', "Fan Information")
   fans = fanInfo.keys()
   for curFan in fans:
      curDict = fanInfo[curFan]
      status = curDict['status']
      rpm = curDict['rpm']
      speed = curDict['speed']
      common.LogOutput('info', "\tCurrent Fan " + curFan + " status:" + str(status) + " speed:" + str(speed) + " rpm:" + str(rpm))
    
   # Temp sensor INformation
   tempInfo = common.ReturnJSONGetData(json=mystruct, dataElement='Temp_Sensors')
   tempKeys = tempInfo.keys()
   common.LogOutput('info', "Temperature Info")
   for curTemp in tempKeys:
      curDict = tempInfo[curTemp]
      temperature = curDict['temperature']
      max = curDict['max']
      min= curDict['min']
      common.LogOutput('info', "\tCurrent Temp Sensor " + curTemp + " temperature:" + str(temperature) + " max:" + str(max) + " min:" + str(min))
    
   otherConfig = common.ReturnJSONGetData(json=mystruct, dataElement='other_config')
   common.LogOutput('info', "Other Configuration")
   keys_List = otherConfig.keys()
   for curKey in keys_List:
      common.LogOutput('info', "\t" + str(curKey) + ": " +  otherConfig[curKey])
