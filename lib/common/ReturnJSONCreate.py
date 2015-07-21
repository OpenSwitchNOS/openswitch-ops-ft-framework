###PROC+#####################################################################
# Name:        common.ReturnJSONCreate
#
# Namespace:   common
#
# Author:      Vince Mendoza
#
# Purpose:     Generates a standard return JSON structure for routines
#
# Params:      returnCode - Return code value
#              data - dictionary data to build out JSON
#
# Returns:     json string
#
##PROC-#####################################################################
import json

def ReturnJSONCreate(**kwargs):
    returnCode = kwargs.get('returnCode')
    data = kwargs.get('data')

    # Create a local dictionary to push into the JSON serialze routine
    localDict = dict()
    localDict['returnCode'] = returnCode
    localDict['data'] = data

    jsonString = json.dumps(localDict,indent=3)
    return jsonString