import pytest

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
        Test_template.tcInstance = tcAction()
        TEST_DESCRIPTION = "Virtual Topology / Physical Topology Sample Test"
        Test_template.testObj.ResultsDirectory['testcaseName'] = "pytestInc.py"
        Test_template.tcInstance.tcInfo(tcName = Test_template.testObj.ResultsDirectory['testcaseName'], tcDesc = TEST_DESCRIPTION)
        
        Test_template.tcInstance.defineStep(stepDesc="Show System on dut01")
        Test_template.tcInstance.defineStep(stepDesc="Uname on wrkston01")
        Test_template.tcInstance.defineStep(stepDesc="Ifconfig on wrkston02")
        
    def teardown_class(cls):
        # Terminate all nodes
        Test_template.topoObj.terminate_nodes()
        #LogOutput('info', "Tearing Down Topology")
        
    def test_showSystem(self):
        # show system test
        self.tcInstance.startStep()
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        cmdOut = dut01Obj.cmdVtysh(command="show system")
        LogOutput('info', "output from dut01\n" + cmdOut)
        self.tcInstance.endStep()
    
    def test_wrkston01Uname(self):
        self.tcInstance.startStep()
        wrkston01Obj = Test_template.topoObj.deviceObjGet(device="wrkston01")
        cmdOut = wrkston01Obj.cmd("uname -a")
        LogOutput('info', "output from wrkston01\n" + cmdOut)
        self.tcInstance.endStep()
        
    def test_wrkston02IfCOnfig(self):
        self.tcInstance.startStep()
        wrkston02Obj = Test_template.topoObj.deviceObjGet(device="wrkston02")
        cmdOut = wrkston02Obj.cmd("ifconfig -a")
        LogOutput('info', "output from wrkston02\n" + cmdOut)
        self.tcInstance.endStep()

