import pytest
from switch.CLI import *
from switch.CLI.LAG import *
from switch.CLI.interface import *
from lib import *

topoDict = {"topoExecution": 3000,
            "topoDevices": "dut01 wrkston01 wrkston02",
            "topoLinks": "lnk01:dut01:wrkston01,\
                          lnk02:dut01:wrkston02",
            "topoFilters": "dut01:system-category:switch,\
                            wrkston01:system-category:workstation,\
                            wrkston02:system-category:workstation"}

class Test_ft_LAG_Static_L2_hashing_flow_distribution:
    def setup_class(cls):
        # Create Topology object and connect to devices
        Test_ft_framework_basics.testObj = testEnviron(topoDict=topoDict)
        Test_ft_framework_basics.topoObj = Test_ft_framework_basics.testObj.topoObjGet()
        
    def teardown_class(cls):
        # Terminate all nodes
        Test_ft_framework_basics.topoObj.terminate_nodes()
        
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
    
    def test_ping_to_switch(self):
        LogOutput('info', "############################################")
        LogOutput('info', "Configure and ping to switch")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        wrkston01Obj = self.topoObj.deviceObjGet(device="wrkston01")
        pingSwitchRetStruct = ping_to_switch(dut01Obj, wrkston01Obj)
        if pingSwitchRetStruct.returnCode() != 0:
            assert("Failed to ping to the switch")
        else:
            LogOutput('info', "Passed ping to switch test")
    
    def test_ping_through_switch(self):
        LogOutput('info', "############################################")
        LogOutput('info', "Additional configuration and ping through switch")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        wrkston01Obj = self.topoObj.deviceObjGet(device="wrkston01")
        wrkston02Obj = self.topoObj.deviceObjGet(device="wrkston02")
        pingSwitchRetStruct = ping_through_switch(dut01Obj, wrkston01Obj, wrkston02Obj)
        if pingSwitchRetStruct.returnCode() != 0:
            assert("Failed to ping through the switch")
        else:
            LogOutput('info', "Passed ping to switch test")
    
    def test_clean_up_devices(self):
        LogOutput('info', "############################################")
        LogOutput('info', "Device Cleanup - rolling back config")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        wrkston01Obj = self.topoObj.deviceObjGet(device="wrkston01")
        wrkston02Obj = self.topoObj.deviceObjGet(device="wrkston02")
        cleanupRetStruct = deviceCleanup(dut01Obj, wrkston01Obj, wrkston02Obj)
        if cleanupRetStruct.returnCode() != 0:
            assert("Failed to cleanup device")
        else:
            LogOutput('info', "Cleaned up devices")

