#########################################################################################################
# Name:        lagDynamicSupportedAndUnsupportedNames
#
# Objective:   To verify a dynamic LAG can be created using permitted names 
#              and cannot be created if the name is too long or has unsupported characters
#
# Author:      Pablo Araya M.
#
# Topology:    1 swtich (DUT running Halon)
#  
########################################################################################################## 

from lib import *
import switch
import pytest
from switch.CLI import *
from switch.CLI.lldp import *
from switch.CLI.interface import *
from switch.CLI.lag import *


topoDict = {"topoExecution": 120,
            "topoDevices": "dut01",
            "topoFilters": "dut01:system-category:switch"}
 

def deviceCleanup(dut01Obj):
    returnCode = 0;
    
    LogOutput('info', "############################################")
    LogOutput('info', "CLEANUP: Reboot the switch")
    LogOutput('info', "############################################")
    rebootRetStruct = dut01Obj.Reboot()
    rebootRetStruct = returnStruct(returnCode=0)
        
    if rebootRetStruct.returnCode() != 0:
        LogOutput('error', "Switch Reboot failed")
        returnCode = 1;
    else:
        LogOutput('info', "Passed Switch Reboot piece")
            
    # Global cleanup return structure
    cleanupRetStruct = returnStruct(returnCode=returnCode)
    return cleanupRetStruct


def configureLag(dut01Obj, lagName, negative):
    LogOutput('info', "############################################")
    LogOutput('info', "Configure LAG using name: "+str(lagName))
    LogOutput('info', "############################################")
        
    retStruct = lagMode(deviceObj=dut01Obj, lagId=lagName, lagMode="active")
    
    if negative:
        if retStruct.returnCode() == 0:
            LogOutput('error', "LAG with invalid name "+str(lagName)+" successfully configured")
            return False
        else:
            LogOutput('info', "LAG with invalid name "+str(lagName)+" was not configure, as expected")
            return True
    else:
        if retStruct.returnCode() != 0:
            LogOutput('error', "Failed to configure LAG with name "+str(lagName))
            return False
        else:
            LogOutput('info', "Successfully configured LAG with name "+str(lagName))
            return True


class Test_lagDynamicSupportedAndUnsupportedNames:
    
    # Global variables
    dut01Obj = None
    
    
    def setup_class(cls):
        # Create Topology object and connect to devices
        Test_lagDynamicSupportedAndUnsupportedNames.testObj = testEnviron(topoDict=topoDict)
        Test_lagDynamicSupportedAndUnsupportedNames.topoObj = Test_lagDynamicSupportedAndUnsupportedNames.testObj.topoObjGet()
        # Global variables
        global dut01Obj 
        dut01Obj = cls.topoObj.deviceObjGet(device="dut01")
        
    
    def teardown_class(cls):
        # Terminate all nodes
        deviceCleanup(dut01Obj)
        Test_lagDynamicSupportedAndUnsupportedNames.topoObj.terminate_nodes()

    def test_configure_LAG_ValidName_1(self):
        lagName = 1;
        assert(configureLag(dut01Obj, lagName, False))
                       
    def test_configure_LAG_ValidName_2(self):
        lagName = 2000;
        assert(configureLag(dut01Obj, lagName, False))
                         
    def test_configure_LAG_InvalidName_1(self):
        lagName = "theLag01";
        assert(configureLag(dut01Obj, lagName, True))
        
    def test_configure_LAG_InvalidName_2(self):
        lagName = 0;
        assert(configureLag(dut01Obj, lagName, True))
        
    def test_configure_LAG_InvalidName_3(self):
        lagName = -1;
        assert(configureLag(dut01Obj, lagName, True))
        
    def test_configure_LAG_InvalidName_4(self):
        lagName = 2001;
        assert(configureLag(dut01Obj, lagName, True))