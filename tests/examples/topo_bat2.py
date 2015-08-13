import common
# Topology definition
topoDict = {"topoType" : "all",
            "topoExecution": 1000,
            "topoTarget": "dut01",
            "topoDevices": "dut01 wrkston01 wrkston02",
            "topoLinks": "lnk01:dut01:wrkston01,\
                          lnk02:dut01:wrkston02",
            "topoFilters": "dut01:system-category:switch,\
                            wrkston01:system-category:workstation,\
                            wrkston02:system-category:workstation",
            "topoLinkFilter": "lnk01:dut01:interface:eth0"}

# Test object will parse command line and formulate the env
testObj = common.testEnv(topoDict=topoDict)

# Get topology object
topoObj = testObj.topoObjGet()

# GEt Device objects
dut01Obj = topoObj.deviceObjGet(device="dut01")
#cmdOut = dut01Obj.cmd("ovs-vsctl show")
#common.LogOutput('info', "output from dut01\n" + cmdOut)

cmdOut = dut01Obj.cmdVtysh(command="show system")
common.LogOutput('info', "output from dut01\n" + cmdOut)

wrkston01Obj = topoObj.deviceObjGet(device="wrkston01")
cmdOut = wrkston01Obj.cmd("uname -a")
common.LogOutput('info', "output from wrkston01\n" + cmdOut)


wrkston02Obj = topoObj.deviceObjGet(device="wrkston02")
cmdOut = wrkston02Obj.cmd("ifconfig -a")
common.LogOutput('info', "output from wrkston02\n" + cmdOut)


common.LogOutput('info', "Link info " + str(dut01Obj.linkPortMapping))
topoObj.terminate_nodes()