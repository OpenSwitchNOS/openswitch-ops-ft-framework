#########################################################################################################
# Name:        lagDynamicInterfacesOnOtherLag
#
# Objective:   To verify the interface is moved when it is part of a dynamic LAG and is 
#                added to another LAG
#
# Author:      Pablo Araya M.
#
# Topology:    1 switch (DUT running Halon)
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

def verifyInterfaceLag(dut01Obj, interface, lagId):
    LogOutput('info', "############################################")
    LogOutput('info', "Verify that interface "+str(interface)+" belongs to LAG "+str(lagId))
    LogOutput('info', "############################################")
            
    retStruct = InterfaceLagShow(deviceObj=dut01Obj, interface=interface)
    if retStruct.returnCode() != 0:
        LogOutput('error', "Failed to get interface "+str(interface)+" configuration")
        return False
    
    aggregateName = retStruct.valueGet(key="remotePort")["lagId"]
    if int(lagId)==int(aggregateName):
        LogOutput('info', "Interface "+str(interface)+" correctly belongs to LAG "+str(aggregateName))
        return True
    else:
        LogOutput('info', "Interface "+str(interface)+" incorrectly belongs to LAG "+str(aggregateName))
        return False
    
        
class Test_lagStaticInterfacesOnOtherLag:
    
    # Global variables
    dut01Obj = None
    
    
    def setup_class(cls):
        # Create Topology object and connect to devices
        Test_lagStaticInterfacesOnOtherLag.testObj = testEnviron(topoDict=topoDict)
        Test_lagStaticInterfacesOnOtherLag.topoObj = Test_lagStaticInterfacesOnOtherLag.testObj.topoObjGet()
        # Global variables
        global dut01Obj 
        dut01Obj = cls.topoObj.deviceObjGet(device="dut01")
            
    def teardown_class(cls):
        # Terminate all nodes
        deviceCleanup(dut01Obj)
        Test_lagStaticInterfacesOnOtherLag.topoObj.terminate_nodes()

    def test_configure_LAG_1(self):
        lagName = 1;
        LogOutput('info', "############################################")
        LogOutput('info', "Configure LAG using name: "+str(lagName))
        LogOutput('info', "############################################")
            
        retStruct = lagMode(deviceObj=dut01Obj, lagId=lagName, lagMode="active")
        if retStruct.returnCode() != 0:
            LogOutput('error', "Failed to configure LAG "+str(lagName))
        else:
            LogOutput('info', "LAG  "+str(lagName)+" successfully configured")
        
        assert(retStruct.returnCode() == 0)
    
    def test_add_ports_to_LAG_1(self):
        lagName = 1;
        portId = 10;
        LogOutput('info', "############################################")
        LogOutput('info', "Add interface "+str(portId)+" to LAG "+str(lagName))
        LogOutput('info', "############################################")
            
        retStruct = InterfaceLagIdConfig(deviceObj=dut01Obj, interface=portId, lagId=lagName)
        if retStruct.returnCode() != 0:
            LogOutput('error', "Failed to add interface "+str(portId)+" to LAG "+str(lagName))
        else:
            LogOutput('info', "Successfully added interface "+str(portId)+" to LAG "+str(lagName))
        
        assert(retStruct.returnCode() == 0)
                           
    def test_verify_Interface_Lag1(self):
        lagName = 1;
        portId = 10;
        assert(verifyInterfaceLag(dut01Obj=dut01Obj, interface=portId, lagId=lagName))
                           
    def test_configure_LAG_2(self):
        lagName = 2;
        LogOutput('info', "############################################")
        LogOutput('info', "Configure LAG using name: "+str(lagName))
        LogOutput('info', "############################################")
            
        retStruct = lagMode(deviceObj=dut01Obj, lagId=lagName, lagMode="active")
        if retStruct.returnCode() != 0:
            LogOutput('error', "Failed to configure LAG "+str(lagName))
        else:
            LogOutput('info', "LAG  "+str(lagName)+" successfully configured")
        
        assert(retStruct.returnCode() == 0)
                         
    def test_add_ports_to_LAG_2(self):
        lagName = 2;
        portId = 10;
        LogOutput('info', "############################################")
        LogOutput('info', "Add interface "+str(portId)+" to LAG "+str(lagName))
        LogOutput('info', "############################################")
            
        retStruct = InterfaceLagIdConfig(deviceObj=dut01Obj, interface=portId, lagId=lagName)
        if retStruct.returnCode() != 0:
            LogOutput('info', "Failed to add interface "+str(portId)+" to LAG "+str(lagName))
        else:
            LogOutput('error', "Successfully added interface "+str(portId)+" to LAG "+str(lagName))
        
        assert(retStruct.returnCode() == 0)
        
    def test_verify_Interface_Lag2(self):
        lagName = 2;
        portId = 10;
        assert(verifyInterfaceLag(dut01Obj=dut01Obj, interface=portId, lagId=lagName))
        