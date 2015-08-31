LogOutput("info", "Sample test case code.")
# This is not using the template - don't use as example test case
# Grab the name of the switch from the eTree
switchElement = XmlGetElementsByTag(headers.TOPOLOGY, ".//device/system[vendor='Edgecore']/name", allElements=True)
numSwitches = len(switchElement)
for switchE in switchElement:
    switchName = switchE.text
    # Connect to the device
    LogOutput('info', "########################################")
    LogOutput('info', "Connecting to switch " + switchName)
    LogOutput('info', "########################################")
    devConn = switch.Connect(switchName)
    if devConn is None:
        LogOutput('error', "Failed to connect to switch " + switchName)
        continue

    # Rebooting switch
    LogOutput('info', "Rebooting switch " + switchName)
    retStruct = switch.Reboot(connection=devConn)
    retCode = retStruct.get('returnCode')
    if retCode != 0:
        LogOutput('error', "Failed to reboot switch " + switchName)
    else:
        LogOutput('info', "Successfully rebooted switch " + switchName)
    # Do vlan create
    retStruct = switch.OVS.OvsBridgeConfig(connection=devConn, bridge="br0", action='config', ports=[1, 2, 3])

    vlanList = [1]
    retStruct = switch.OVS.OvsVlanConfig(connection=devConn, bridge="br0", vlans=vlanList)


    # OvsShow
    mystruct = switch.OVS.OvsShow(connection=devConn)
    retCode = ReturnJSONGetCode(json=mystruct)
    print mystruct
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

    # Temp sensor INformation
    tempInfo = ReturnJSONGetData(json=mystruct, dataElement='Temp_Sensors')
    tempKeys = tempInfo.keys()
    LogOutput('info', "Temperature Info")
    for curTemp in tempKeys:
        curDict = tempInfo[curTemp]
        temperature = curDict['temperature']
        max = curDict['max']
        min = curDict['min']
        LogOutput('info', "\tCurrent Temp Sensor " + curTemp + " temperature:" + str(temperature) + " max:" + str(max) + " min:" + str(min))

    otherConfig = ReturnJSONGetData(json=mystruct, dataElement='other_config')
    LogOutput('info', "Other Configuration")
    keys_List = otherConfig.keys()
    for curKey in keys_List:
        LogOutput('info', "\t" + str(curKey) + ": " + otherConfig[curKey])
