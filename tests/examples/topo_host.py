import common
from lib import testEnviron
#
# Topology definition
topoDict = {"topoType" : "all",
            "topoExecution": 1000,
            "topoTarget": "dut01",
            "topoDevices": "dut01 dut02 wrkston01",
            "topoLinks": "lnk01:dut01:wrkston01,\
                          lnk02:dut01:dut02",
            "topoFilters": "dut01:system-category:switch,\
                            dut02:system-category:switch,\
                            wrkston01:system-category:workstation",
            "topoLinkFilter": "lnk01:dut01:interface:eth0"}

# Test object will parse command line and formulate the env
testObj = testEnviron(topoDict=topoDict)
# Get topology object
topoObj = testObj.topoObjGet()

# GEt Device objects
wrkston01Obj = topoObj.deviceObjGet(device="wrkston01")

cmdOut = wrkston01Obj.NetworkConfig(eth='eth0',
        ipAddr='20.20.20.2',
        netMask='255.255.255.0',
        broadcast='20.20.20.1',
        clear=0)

retCode = cmdOut.get('returnCode')
retBuff = cmdOut.get('buffer')
if retCode:
    common.LogOutput('error', 'Failed to config ipv4 address on host')
else:
    common.LogOutput('info', 'Succeed to config ipv4 address on host')

cmdOut = wrkston01Obj.Network6Config(eth='eth0',
        ipAddr='2001::1',
        netMask=64,
        clear=0)

retCode = cmdOut.get('returnCode')
retBuff = cmdOut.get('buffer')
if retCode:
    common.LogOutput('error', 'Failed to config ipv6 address on host')
else:
    common.LogOutput('info', 'Succeed to config ipv6 address on host')


cmdOut = wrkston01Obj.IPRoutesConfig(
        routeOperation='add',
        destNetwork='30.30.30.0',
        netMask=24,
        via='20.20.20.5',
        eth='eth0',
        metric=1,
        ipv6Flag=0,
        )

retCode = cmdOut.get('returnCode')
retBuff = cmdOut.get('buffer')
if retCode:
    common.LogOutput('error', 'Failed to config ipv4 routes on host')
else:
    common.LogOutput('info', 'Succeed to config ipv4 routes on host')

#this works only if neigbour is connected
cmdOut = wrkston01Obj.GetDirectLocalLinkAddresses()
#localLinkAddress = interfaceList[0]['address']
#eth = interfaceList[0]['eth']

cmdOut = wrkston01Obj.IPRoutesConfig(
        routeOperation='add',
        destNetwork='2002::',
        netMask=64,
        via='fe80::1',
        eth='eth0',
        metric=1,
        ipv6Flag=1,
        )

retCode = cmdOut.get('returnCode')
retBuff = cmdOut.get('buffer')
if retCode:
    common.LogOutput('error', 'Failed to config ipv6 routes on host')
else:
    common.LogOutput('info', 'Succeed to config ipv6 routes on host')


cmdOut = wrkston01Obj.DevicePing(ipAddr="20.20.20.2")
retCode = cmdOut.get('returnCode')
retBuff = cmdOut.get('buffer')
if retCode:
    common.LogOutput('error', 'Failed to ping ipv4 dest ip on host')
else:
    common.LogOutput('info', 'Succeed to config ipv4 dest ip on host')
topoObj.terminate_nodes()
