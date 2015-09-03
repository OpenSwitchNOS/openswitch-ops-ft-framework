import pytest
from switch.CLI import *
from switch.CLI.LAG import *
from lib import *

topoDict = {"topoExecution": 3000,
            "topoDevices": "dut01",
            "topoFilters": "dut01:system-category:switch"
            }

class Test_ft_framework_basics:
    def setup_class(cls):
        # Create Topology object and connect to devices
        Test_ft_framework_basics.testObj = testEnviron(topoDict=topoDict)
        Test_ft_framework_basics.topoObj = Test_ft_framework_basics.testObj.topoObjGet()
      
    def test_reboot_switch(self):
        LogOutput('info', "############################################")
        LogOutput('info', "Testing libraries")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        exampleRetStruc = InterfaceLagIdConfig(deviceObj=dut01Obj, interface=1, lagId=1, enable=False)
        if exampleRetStruc.returnCode() != 0:
            LogOutput('info', "No paso")
            assert(False)
        else:
            LogOutput('info', "Paso todo bien")
  
