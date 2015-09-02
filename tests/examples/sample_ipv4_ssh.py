
import switch
#import switch.CLI.lldp
from switch.CLI import *
from switch.CLI.lldp import *
from switch.CLI.interface import *

#from switch.CLI.lldp import *
from lib import testEnviron
#import switch
topoDict = {"topoExecution": 3000,
            "topoDevices": "dut01 wrkston01",
            "topoLinks": "lnk01:dut01:wrkston01",
            "topoFilters": "dut01:system-category:switch,\
                            wrkston01:system-category:workstation",
            "topoLinkFilters": "lnk01:dut01:interface:eth0" }

#
# Test object will parse command line and formulate the env
testObj = testEnviron(topoDict=topoDict)
LogOutput('info', "##########################################################")
LogOutput('info', "")
LogOutput('info', "Sample IPv4 SSH Code - not an official test case")
LogOutput('info', "Demonstrates how to use library functionality to set up")
LogOutput('info', "a simple routing situation")
LogOutput('info', "")
LogOutput('info', "##########################################################")
# Get topology object
topoObj = testObj.topoObjGet()

# GEt Device objects
dut01Obj = topoObj.deviceObjGet(device="dut01")
wrkston01Obj = topoObj.deviceObjGet(device="wrkston01")

# Reboot device
retStrReboot = dut01Obj.Reboot()
# Configure Ip on switch
cmdOut = dut01Obj.cmd("ip address add 10.10.1.1/24 dev eth0")
cmdOut = dut01Obj.cmd("ifconfig eth0 inet broadcast 10.10.1.255")

# Configure IP on wrkston01

retStructNetConfig = wrkston01Obj.NetworkConfig(interface=wrkston01Obj.linkPortMapping['lnk01'],
                                                ipAddr="10.10.1.10", netMask="255.255.255.0", 
                                                broadcast="10.10.1.255", config=True)
if retStructNetConfig.returnCode() != 0:
    LogOutput('error', "Failed to configure IP address on the workstation")
    
# Get an inband connection with the switch
switchConnObj1 = topoObj.inbandSwitchConnectGet(srcObj=wrkston01Obj, targetObj=dut01Obj, address="10.10.1.1")
cmdOut = switchConnObj1.cmdVtysh(command="show version")
print cmdOut

myretStruct = ShowLldpNeighborInfo(deviceObj=switchConnObj1)
if myretStruct.returnCode() != 0:
    LogOutput('error', "Failed to do lldp neighbor command")
else:
    LogOutput('info', "LLDP output\n" + myretStruct.buffer())
    LogOutput('info', "LLDP ret data\n" + myretStruct.retValueString())

vtyShRetStruct = switchConnObj1.VtyshShell(enter=True)
if vtyShRetStruct.returnCode() != 0:
    LogOutput('error', "Failed to get into vtyshell")
else:
    LogOutput('info', "Succeeded to get into vtyshell")

cmdOut = switchConnObj1.cmd("show version")
LogOutput('info', "Show version from vtysh\n:" + cmdOut)

switchConnObj2 = topoObj.inbandSwitchConnectGet(srcObj=wrkston01Obj, targetObj=dut01Obj, address="10.10.1.1")
cmdOut = switchConnObj2.cmd("ps -ef")
LogOutput('info', "Connection 2 command from linux\n:" + cmdOut)

retStructNetConfig = wrkston01Obj.NetworkConfig(interface=wrkston01Obj.linkPortMapping['lnk01'],
                                                ipAddr="10.10.1.10", netMask="255.255.255.0",
                                                broadcast="10.10.1.255", config=False)

print topoObj.deviceObjList()

topoObj.terminate_nodes()

