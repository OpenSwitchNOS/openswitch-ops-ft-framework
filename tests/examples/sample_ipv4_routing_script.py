import common
import switch
#import switch.CLI.lldp
from switch.CLI import *
from switch.CLI.lldp import *
from switch.CLI.interface import *

#from switch.CLI.lldp import *
from lib import testEnviron
#import switch
topoDict = {"topoExecution": 3000,
            "topoDevices": "dut01 wrkston01 wrkston02",
            "topoLinks": "lnk01:dut01:wrkston01,lnk02:dut01:wrkston02",
            "topoFilters": "dut01:system-category:switch,\
                            wrkston01:system-category:workstation,\
                            wrkston02:system-category:workstation"}

#
# Test object will parse command line and formulate the env
testObj = testEnviron(topoDict=topoDict)
common.LogOutput('info', "##########################################################")
common.LogOutput('info', "")
common.LogOutput('info', "Sample IPv4 Routing Code - not an official test case")
common.LogOutput('info', "Demonstrates how to use library functionality to set up")
common.LogOutput('info', "a simple routing situation")
common.LogOutput('info', "")
common.LogOutput('info', "##########################################################")
# Get topology object
topoObj = testObj.topoObjGet()

# GEt Device objects
dut01Obj = topoObj.deviceObjGet(device="dut01")
wrkston01Obj = topoObj.deviceObjGet(device="wrkston01")
wrkston02Obj = topoObj.deviceObjGet(device="wrkston02")

# Reboot switch
common.LogOutput('info', "Reboot switch") 
retStruct = dut01Obj.Reboot()

# Switch config
common.LogOutput('info', "Configuring Switch to be an IPv4 router")
retStruct = InterfaceEnable(deviceObj=dut01Obj, enable=True,
                            interface=dut01Obj.linkPortMapping['lnk01'])
retStruct = InterfaceEnable(deviceObj=dut01Obj, enable=True,
                            interface=dut01Obj.linkPortMapping['lnk02'])
# #print retStruct
retStruct = InterfaceIpConfig(deviceObj=dut01Obj,
                              interface=dut01Obj.linkPortMapping['lnk01'],
                              addr="140.1.1.1", mask=24, config=True)
retStruct = InterfaceIpConfig(deviceObj=dut01Obj,
                              interface=dut01Obj.linkPortMapping['lnk02'],
                              addr="140.1.2.1", mask=24, config=True)

cmdOut = dut01Obj.cmdVtysh(command="show run")
common.LogOutput('info', "Running config of the switch:\n" + cmdOut)

# Workstation config
common.LogOutput('info', "Configuring workstations")
retStruct = wrkston01Obj.NetworkConfig(ipAddr="140.1.1.10", netMask="255.255.255.0", broadcast="140.1.1.255", 
                                       interface=wrkston01Obj.linkPortMapping['lnk01'], config=True)
cmdOut = wrkston01Obj.cmd("ifconfig "+ wrkston01Obj.linkPortMapping['lnk01'])
common.LogOutput('info', "Ifconfig info for workstation 1:\n" + cmdOut)

retStruct = wrkston02Obj.NetworkConfig(ipAddr="140.1.2.10", netMask="255.255.255.0", broadcast="140.1.2.255", 
                                       interface=wrkston02Obj.linkPortMapping['lnk02'], config=True)
cmdOut = wrkston02Obj.cmd("ifconfig "+ wrkston02Obj.linkPortMapping['lnk02'])
common.LogOutput('info', "Ifconfig info for workstation 2:\n" + cmdOut)

retStruct = wrkston01Obj.IPRoutesConfig(config=True, destNetwork="140.1.2.0", netMask=24, gateway="140.1.1.1")
cmdOut = wrkston01Obj.cmd("netstat -rn")
common.LogOutput('info', "IPv4 Route table for workstation 1:\n" + cmdOut)

retStruct = wrkston02Obj.IPRoutesConfig(config=True, destNetwork="140.1.1.0", netMask=24, gateway="140.1.2.1")
cmdOut = wrkston02Obj.cmd("netstat -rn")
common.LogOutput('info', "IPv4 Route table for workstation 2:\n" + cmdOut)

common.LogOutput('info', "Pinging between workstation1 and workstation2")
retStruct = wrkston01Obj.Ping(ipAddr="140.1.2.10")
common.LogOutput('info', "IPv4 Ping from workstation 1 to workstation 2 return JSON:\n" + retStruct)

common.LogOutput('info', "Unonfiguring workstations")
retStruct = wrkston01Obj.IPRoutesConfig(config=False, destNetwork="140.1.2.0", netMask=24, gateway="140.1.1.1")
cmdOut = wrkston02Obj.cmd("netstat -rn")
common.LogOutput('info', "IPv4 Route table for workstation 2:\n" + cmdOut)

retStruct = wrkston02Obj.IPRoutesConfig(config=False, destNetwork="140.1.1.0", netMask=24, gateway="140.1.2.1")
cmdOut = wrkston01Obj.cmd("netstat -rn")
common.LogOutput('info', "IPv4 Route table for workstation 1:\n" + cmdOut)

retStruct = wrkston01Obj.NetworkConfig(ipAddr="140.1.1.10", netMask="255.255.255.0", broadcast="140.1.1.255", 
                                      interface=wrkston01Obj.linkPortMapping['lnk01'], config=False)
cmdOut = wrkston01Obj.cmd("ifconfig "+ wrkston01Obj.linkPortMapping['lnk01'])
common.LogOutput('info', "Ifconfig info for workstation 1:\n" + cmdOut)

retStruct = wrkston02Obj.NetworkConfig(ipAddr="140.1.2.10", netMask="255.255.255.0", broadcast="140.1.2.255", 
                                       interface=wrkston02Obj.linkPortMapping['lnk02'], config=False)
cmdOut = wrkston02Obj.cmd("ifconfig "+ wrkston02Obj.linkPortMapping['lnk02'])
common.LogOutput('info', "Ifconfig info for workstation 2:\n" + cmdOut)

common.LogOutput('info', "Unconfigure switch")
retStruct = InterfaceIpConfig(deviceObj=dut01Obj,
                              interface=dut01Obj.linkPortMapping['lnk01'],
                              addr="140.1.1.1", mask=24, config=False)
retStruct = InterfaceIpConfig(deviceObj=dut01Obj,
                              interface=dut01Obj.linkPortMapping['lnk02'],
                              addr="140.1.2.1", mask=24, config=False)

retStruct = InterfaceEnable(deviceObj=dut01Obj, enable=False,
                            interface=dut01Obj.linkPortMapping['lnk01'])
retStruct = InterfaceEnable(deviceObj=dut01Obj, enable=False,
                            interface=dut01Obj.linkPortMapping['lnk02'])
cmdOut = dut01Obj.cmdVtysh(command="show run")
common.LogOutput('info', "Running config of the switch:\n" + cmdOut)


topoObj.terminate_nodes()

