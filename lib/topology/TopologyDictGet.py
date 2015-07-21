###PROC+#####################################################################
# Name:        topology.TopologyDictGet
#
# Namespace:   topology
#
# Author:      Vince Mendoza
#
# Purpose:     PUll topology dictionary from the test case & builds out logical topology
#
#
# Params:      testcase
#
# Returns:     json structur
#               returnCode
#               data = topology dictionary
#
##PROC-#####################################################################
import headers
import common
import re
import json

def TopologyDictGet(**kwargs):
    testcase = kwargs.get('testcase', None)
    tcFH = open(testcase, 'r')
    #testCaseData = tcFH.read()
    detectDictStart = 0
    detectDictEnd = 1
    topoDictBuffer = ""
    for curLine in tcFH:
       # Searching for whole dictionary
       wholeDictionary = re.match("^topoDict\s*=\s*({.*})", curLine)
       if wholeDictionary:
          # This means we got it all in 1 shot
          topoDictionary = wholeDictionary.group(1)
          break

       if detectDictStart == 0:
          testForDictStart = re.match("^topoDict\s*=\s*({.*$)", curLine)
          if testForDictStart:
             detectDictStart = 1
             detectDictEnd = 1
             topoDictBuffer = testForDictStart.group(1)
             continue
       else:
          testForDictEnd = re.match("^\s*(.*})", curLine)
          if testForDictEnd:
             detectDictEnd = 1
             topoDictBuffer += testForDictEnd.group(1)
             break;
          else:
             # Weed down the spaces
             dictStringSpan = re.match("^\s*(.*)\s*$", curLine)
             if dictStringSpan:
                topoDictBuffer += dictStringSpan.group(1)
             continue
    # close off file
    tcFH.close()

    if detectDictStart == 1 and detectDictEnd == 1:
       # This means we found dictionary data in the test case
       # Structure a proper dictionary to return back
       topoRetDict = json.loads(topoDictBuffer)
       retString = common.ReturnJSONCreate(returnCode=0, data=topoRetDict)
    else:
       # Means there is no topology dictionary in the test case
       retString = common.ReturnJSONCreate(returnCode=1, data=None)
    return(retString)
    #for lines in str(testcaseData).split('\n'):
    #   print "line: " + lines
