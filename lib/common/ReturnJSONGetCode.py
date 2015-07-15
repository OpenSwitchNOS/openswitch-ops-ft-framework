###PROC+#####################################################################
# Name:        common.ReturnJSONGetCode
#
# Namespace:   common
#
# Author:      Vince Mendoza
#
# Purpose:     Retrieves returnCode from a returnStruct
#
# Params:      json - Return code value
#
# Returns:     0 or 1
#
##PROC-#####################################################################
import json

def ReturnJSONGetCode(**kwargs):
    returnStruct = kwargs.get('json')
    
    localDict = json.loads(returnStruct)
    returnCode = localDict['returnCode']
    return returnCode