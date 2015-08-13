import common
#import switch
topoDict = {"topoExecution": 3000,
            "topoDevices": "dut01 dut02",
            "topoLinks": "lnk01:dut01:dut02",
            "topoFilters": "dut01:system-category:switch,dut02:system-category:switch"}

#
# Test object will parse command line and formulate the env
testObj = common.testEnv(topoDict=topoDict)

# Get topology object
topoObj = testObj.topoObjGet()
# TMP HACK
import switch
# GEt Device objects
dut01Obj = topoObj.deviceObjGet(device="dut01")
dut02Obj = topoObj.deviceObjGet(device="dut02")


retStruct = switch.CLI.ShowLldpNeighborInfo(deviceObj=dut01Obj)
retCode = common.ReturnJSONGetCode(json=retStruct)
#print retStruct
common.LogOutput('info', "The struct \n" + str(retStruct))
if retCode != 0:
    common.LogOutput('error', "Unable get get LLDP information from switch")
# This will get you the dictionary back from portstats.  This is indexed by port number
retStruct = switch.CLI.ShowLldpNeighborInfo(deviceObj=dut01Obj, port=dut01Obj.linkPortMapping['lnk01'])
retCode = common.ReturnJSONGetCode(json=retStruct)
if retCode != 0:
    common.LogOutput('error', "Unable get get LLDP information from switch")
    
lnk01PrtStats = common.ReturnJSONGetData(json=retStruct, dataElement='portStats')
print lnk01PrtStats[dut01Obj.linkPortMapping['lnk01']]


topoObj.terminate_nodes()

