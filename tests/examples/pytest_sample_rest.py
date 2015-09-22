import pytest
from opstestfw.switch.CLI import *
from opstestfw import *

topoDict = {"topoExecution": 3000,
            "topoDevices": "dut01 wrkston01",
            "topoLinks": "lnk01:dut01:wrkston01",
            "topoFilters": "dut01:system-category:switch,\
                            wrkston01:system-category:workstation,\
                            wrkston01:docker-image:halon/halon-host",
            "topoLinkFilter": "lnk01:dut01:interface:eth0"}

switchMgmtAddr = "10.10.10.2"
restClientAddr = "10.10.10.3"

def switch_reboot(dut01):
    # Reboot switch
    LogOutput('info', "Reboot switch")
    dut01.Reboot()
    rebootRetStruct = returnStruct(returnCode=0)
    return rebootRetStruct

def config_rest_environment(dut01, wrkston01):

    global switchMgmtAddr
    global restClientAddr

    retStruct = GetLinuxInterfaceIp(deviceObj=dut01)
    if retStruct.returnCode() != 0:
#        assert("Failed to get linux interface ip on switch")
        pass
    else:
        LogOutput('info', "Successful in getting linux interface ip on the switch")
    switchIpAddr = retStruct.data

    if switchIpAddr == "":
        switchIpAddr = "172.17.0.253"

    if switchIpAddr != None or switchIpAddr != "":
        switchMgmtAddr = switchIpAddr
        #restClientAddr = "172.17.0.253"
    print switchMgmtAddr
    retStruct = InterfaceIpConfig(deviceObj=dut01,
                                  interface="mgmt",
                                  addr=switchMgmtAddr, mask=24, config=True)

    if retStruct.returnCode() != 0:
        assert("Failed to configure IP on switchport")
    else:
        LogOutput('info', "Successfully configured ip on switch port")
    cmdOut = dut01.cmdVtysh(command="show run")
    LogOutput('info', "Running config of the switch:\n" + cmdOut)
    LogOutput('info', "Configuring workstations")
    retStruct = wrkston01.NetworkConfig(ipAddr=restClientAddr, netMask="255.255.255.0",broadcast="140.1.2.255",\
                         interface=wrkston01.linkPortMapping['lnk01'], config=True)
    if retStruct.returnCode() != 0:
        assert("Failed to configure IP on workstation")
    cmdOut = wrkston01.cmd("ifconfig "+ wrkston01.linkPortMapping['lnk01'])
    LogOutput('info', "Ifconfig info for workstation 1:\n" + cmdOut)


    retStruct = GetLinuxInterfaceIp(deviceObj=wrkston01)
    if retStruct.returnCode() != 0:
        assert("Failed to get linux interface ip on switch")
    else:
        LogOutput('info', "Successful in getting linux interface ip on the workstation")
    switchIpAddr = retStruct.data
   retStruct = returnStruct(returnCode=0)
    return retStruct


#
def deviceCleanup(dut01, wrkston01):

    retStruct = wrkston01.NetworkConfig(ipAddr=restClientAddr, netMask="255.255.255.0",broadcast="140.1.2.255",\
                                        interface=wrkston01.linkPortMapping['lnk01'], config=False)
    if retStruct.returnCode() != 0:
        assert("Failed to unconfigure IP address on workstation 1")
    cmdOut = wrkston01.cmd("ifconfig "+ wrkston01.linkPortMapping['lnk01'])
    LogOutput('info', "Ifconfig info for workstation 1:\n" + cmdOut)
#
    retStruct = InterfaceIpConfig(deviceObj=dut01,
                               interface="mgmt",
                               addr=switchMgmtAddr, mask=24, config=False)
    if retStruct.returnCode() != 0:
        assert("Failed to unconfigure IP address on dut01 port " )
    else:
        LogOutput('info', "Unconfigure IP address on dut01 port ")

    cmdOut = dut01.cmdVtysh(command="show run")
    LogOutput('info', "Running config of the switch:\n" + cmdOut)
    retStruct = returnStruct(returnCode=0)
    return retStruct


def restTestPort(wrkston01):


    data = {
    "configuration": {
        "name": "169",
        "interfaces": ["/rest/v1/system/interfaces/1"],
        "trunks": [413],
        "ip4_address_secondary": ["192.168.0.1"],
        "lacp": ["active"],
        "bond_mode": ["l2-src-dst-hash"],
        "tag": [654],
        "vlan_mode": ["trunk"],
        "ip6_address": ["2001:0db8:85a3:0000:0000:8a2e:0370:7334"],
        "external_ids": {"extid1key": "extid1value"},
        "bond_options": {"key1": "value1"},
        "mac": ["01:23:45:67:89:ab"],
        "other_config": {"cfg-1key": "cfg1val"},
        "bond_active_slave": ["string"],
        "ip6_address_secondary": ["01:23:45:67:89:ab"],
        "vlan_options": {"opt1key": "opt2val"},
        "ip4_address": ["192.168.0.1"]
    },
    "referenced_by": [{"uri":"/rest/v1/system/bridges/bridge_normal"}],
    }

    retStruct = wrkston01.RestCmd(switch_ip=switchMgmtAddr, url="/rest/v1/system/ports", method="POST", data=data)
    if retStruct.returnCode() != 0:
        assert("Failed to Execute rest command" + "POST for url=/rest/v1/system/ports")
    else:
        LogOutput('info', "Success in executing the rest command" + "POST for url=/rest/v1/system/ports")

    LogOutput('info', 'http return code' +retStruct.data['http_retcode'])

    if retStruct.data['http_retcode'].find("201") == -1:
        assert("Rest POST port Failed ")
    else:
        LogOutput('info', retStruct.data['response_body'])

    retStruct = wrkston01.RestCmd(switch_ip=switchMgmtAddr, url="/rest/v1/system/ports/169", method="GET")
    if retStruct.returnCode() != 0:
        assert("Failed to Execute rest command" + "GET for url=/rest/v1/system/ports/169")
    else:
        LogOutput('info', "Success in executing the rest command" + "GET for url=/rest/v1/system")

    LogOutput('info', 'http return code' +retStruct.data['http_retcode'])

    if retStruct.data['http_retcode'].find("200") == -1:
        assert("Rest GET port Failed ")
    else:
        LogOutput('info', retStruct.data['response_body'])

    retStruct = wrkston01.RestCmd(switch_ip=switchMgmtAddr, url="/rest/v1/system/ports/169", method="DELETE")
    if retStruct.returnCode() != 0:
        assert("Failed to Execute rest command" + "DELETE for url=/rest/v1/system/ports/169")
    else:
        LogOutput('info', "Success in executing the rest command" + "DELETE for url=/rest/v1/system/ports/169")

    LogOutput('info', 'http return code' +retStruct.data['http_retcode'])

    if retStruct.data['http_retcode'].find("204") == -1:
        assert("Rest DELETE port Failed ")

    retStruct = returnStruct(returnCode=0)
    return retStruct


class Test_ft_framework_rest:
    def setup_class(cls):
        # Create Topology object and connect to devices
        Test_ft_framework_rest.testObj = testEnviron(topoDict=topoDict)
        Test_ft_framework_rest.topoObj = Test_ft_framework_rest.testObj.topoObjGet()
        wrkston01Obj = Test_ft_framework_rest.topoObj.deviceObjGet(device="wrkston01")
        wrkston01Obj.CreateRestEnviron()

    def teardown_class(cls):
        # Terminate all nodes
        Test_ft_framework_rest.topoObj.terminate_nodes()

    def test_reboot_switch(self):
        LogOutput('info', "############################################")
        LogOutput('info', "Reboot the switch")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        devRebootRetStruct = switch_reboot(dut01Obj)
        if devRebootRetStruct.returnCode() != 0:
            assert("Failed to reboot Switch")
        else:
            LogOutput('info', "Passed Switch Reboot piece")

    def test_config_rest_environment(self):
        LogOutput('info', "############################################")
        LogOutput('info', "Configure REST environment")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        wrkston01Obj = self.topoObj.deviceObjGet(device="wrkston01")
        retStruct = config_rest_environment(dut01Obj, wrkston01Obj)
        if retStruct.returnCode() != 0:
            assert("Failed to config REST environ")
        else:
            LogOutput('info', "Passed config REST environ test")

    def test_restTestPort(self):
        LogOutput('info', "############################################")
        LogOutput('info', "Testing REST port basic functionality")
        LogOutput('info', "############################################")
        wrkston01Obj = self.topoObj.deviceObjGet(device="wrkston01")
        retStruct = restTestPort(wrkston01Obj)
        if retStruct.returnCode() != 0:
            assert("Failed to test rest port sample")
        else:
            LogOutput('info', "Passed to test rest port sample")

    def test_clean_up_devices(self):
        LogOutput('info', "############################################")
        LogOutput('info', "Device Cleanup - rolling back config")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        wrkston01Obj = self.topoObj.deviceObjGet(device="wrkston01")
        retStruct = deviceCleanup(dut01Obj, wrkston01Obj)
        if retStruct.returnCode() != 0:
            assert("Failed to cleanup device")
        else:
            LogOutput('info', "Cleaned up devices")

