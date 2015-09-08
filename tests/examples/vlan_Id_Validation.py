# Description: Verify that a VID out of the 802.1Q range or reserved VID cannot be set and 
#              also verifies that a VID which already exists cannot not be set again.  
#
# Author:      Jose Pablo Araya
#
# Topology:       |Switch| 
#
# Success Criteria:  PASS -> Vlan out of range and repeated not configured
#
#                             FAILED -> Bad vlans were configured 
#
##########################################################################################################

import pytest
import common
import switch
from switch.CLI.vlan import * 
from lib import testEnviron
from lib import *
# Topology definition
topoDict = {"topoExecution": 1000,
            "topoTarget": "dut01",
            "topoDevices": "dut01",
            "topoFilters": "dut01:system-category:switch"}

def verifyInvalidVlan(dut):
	LogOutput('info', "Validating invalid vlan")
	devRetStruct = ShowVlan(deviceObj=dut)
	returnData = devRetStruct.valueGet(key=None)
	for dictionary in returnData:
		assert dictionary['VLAN'] != str(4095)

def verifyRepeatedVlan(dut):
	LogOutput('info', "Validating invalid vlan")
	cont = 0
	devRetStruct = ShowVlan(deviceObj=dut)
	returnData = devRetStruct.valueGet(key=None)
	for dictionary in returnData:
		if dictionary['VLAN'] == str(2):
			cont = cont + 1  
	assert cont < 2


class Test_vlan_Id_Validation:
	

    def setup_class(cls):
        # Create Topology object and connect to devices
        Test_vlan_Id_Validation.testObj = testEnviron(topoDict=topoDict)
        Test_vlan_Id_Validation.topoObj = Test_vlan_Id_Validation.testObj.topoObjGet()
        Test_vlan_Id_Validation.dut01Obj = Test_vlan_Id_Validation.topoObj.deviceObjGet(device="dut01")
        
    def teardown_class(cls):
        # Terminate all nodes
        Test_vlan_Id_Validation.topoObj.terminate_nodes()
        
    def test_invalid_vlan_add(self):
        LogOutput('info', "############################################")
        LogOutput('info', "Step 1- Try to add invalid vlan out of range")
        LogOutput('info', "############################################")
        devRetStruct = AddVlan(deviceObj=self.dut01Obj, vlanId=4095)

    def test_validate_invalid_vlan(self):
        LogOutput('info', "############################################")
        LogOutput('info', "Step 2- Validate invalid vlan not configured") 
        LogOutput('info', "############################################")
        devRetStruct = verifyInvalidVlan(self.dut01Obj)

    def test_vlan_add(self):
        LogOutput('info', "############################################")
        LogOutput('info', "Step 3- Add vlan")
        LogOutput('info', "############################################")
        devRetStruct = AddVlan(deviceObj=self.dut01Obj, vlanId=2)


    def test_repeated_vlan_add(self):
        LogOutput('info', "############################################")
        LogOutput('info', "Step 4- Try to add repeated vlan")
        LogOutput('info', "############################################")
        devRetStruct = AddVlan(deviceObj=self.dut01Obj, vlanId=2)


    def test_verifyRepeatedVlan(self):
        LogOutput('info', "############################################")
        LogOutput('info', "Step 5- Validate vlan repeated not configured ") 
        LogOutput('info', "############################################")
        devRetStruct = verifyRepeatedVlan(self.dut01Obj)
