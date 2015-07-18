###PROC+#####################################################################
# Name:        common.ReturnJSONGetData
#
# Namespace:   common
#
# Author:      Vince Mendoza
#
# Purpose:     Retrieves data from a returnStruct
#
# Params:      json - Return code value
#              dataElement - (optional)
#
# Returns:     0 or 1
#
##PROC-#####################################################################
import json

def ReturnJSONGetData(**kwargs):
    returnStruct = kwargs.get('json')
    dataElement = kwargs.get('dataElement', None)

    localDict = json.loads(returnStruct)
    returnData = localDict['data']

    if dataElement == None:
        # We want to return the whole data dictionary
        dataToReturn = returnData
    else:
        # We return individual item
        if type(returnData) == dict:
            if dataElement in returnData.keys():
                dataToReturn = returnData[dataElement]
                dataToReturn = dataToReturn.encode('utf-8')
            else :
                dataToReturn = None
        else :
            dataToReturn = None
    return dataToReturn
