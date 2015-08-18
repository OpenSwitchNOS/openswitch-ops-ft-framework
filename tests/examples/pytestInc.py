import pytest
import common
from lib import testEnviron
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


class Test_template:

    def setup_class(cls):
        # Create Topology object and connect to devices
        Test_template.testObj = testEnviron(topoDict=topoDict)
        Test_template.topoObj =Test_template.testObj.topoObjGet()
        
    def teardown_class(cls):
        # Terminate all nodes
        Test_template.topoObj.terminate_nodes()
        common.LogOutput('info', "Tearing Down Topology")
        
    def test_showSystem(self):
        # show system test
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        cmdOut = dut01Obj.cmdVtysh(command="show system")
        common.LogOutput('info', "output from dut01\n" + cmdOut)
    
    def test_wrkston01Uname(self):
        wrkston01Obj = Test_template.topoObj.deviceObjGet(device="wrkston01")
        cmdOut = wrkston01Obj.cmd("uname -a")
        common.LogOutput('info', "output from wrkston01\n" + cmdOut)
    
    def test_wrkston02IfCOnfig(self):
        wrkston02Obj = Test_template.topoObj.deviceObjGet(device="wrkston02")
        cmdOut = wrkston02Obj.cmd("ifconfig -a")
        common.LogOutput('info', "output from wrkston02\n" + cmdOut)

