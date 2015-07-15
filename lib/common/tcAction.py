#####################################################################
# Name:        tcAction
#
# Namespace:   common
#
# Author:      Srinivasa Krishnappa
#
# Purpose:     Standard class definition to control test case flow and log test
#               step and summary verdict.
#
# Params:
#
#
# Returns:     None
#
##PROC-#####################################################################

import os
import sys
import time
import pprint
import datetime
import common
from headers import *

class tcAction(object):
    '''
    This is the main class for tcAction mini framework test case action library.
    Usage:
    '''

    def __init__(self):
        self.tcDescription = ""
        self.tcStepDescription = ""
        self.tcName = ""
        self.tcStepReturnCode = TC_STEPVERDICT_PASS
        self.tcRunFlag = 1
        self.tcStepStartTime = 0
        self.tcStepEndTime = 0
        self.tcStepMessage = ""
        self.tcFailAction = "exit"
        self.tcStepStatus = ""
        self.tcReturnCode = TC_EXECSTATUS_PASSED
        self.tcCurrentStep = 0
        self.tcTotalSteps = 0
        self.tcStepDetail = {"tcName":"", "tcDescription":"", "tcRunFlag":0, "tcFailAction":"exit", "tcReturnCode":0, "tcStepDescription":"",
                         "tcStepExecTime":0.0, "tcStepMessage":"", "tcStepStatus":"", "tcStepReturnCode":0}
        self.tcExecutedSteps = []
        self.tcCleanupFn = "cleanup"
        self.tcVerdict = 1
        self.tcStepFailAction = TC_STEPFAILACTION_CONTINUE
        common.LogOutput("info", "#"*120)
        common.LogOutput("info", "     Starting Test Case Execution     ".center(120, "*" ))
        common.LogOutput("info", "#"*120)

    def defineStep(self, **kwargs):
        '''
        defineStep:
        API to define the step with the passed step description.
        '''
        stepDesc = kwargs.get('stepDesc')
        if (stepDesc == ""):
                common.LogOutput("error", self.tcName +":  Please add step Description   ")
                return 1
        self.tcStepDetail["tcStepDescription"] = stepDesc
        self.tcStepDetail["tcStepReturnCode"] = TC_STEPVERDICT_FAIL
        self.tcStepDetail["tcStepStatus"] = "Incomplete"
        #total steps we can get it from the array tcExecutedSteps elements count as well.
        self.tcTotalSteps += 1
        self.tcExecutedSteps.append(self.tcStepDetail.copy())
        common.LogOutput("info", self.tcName +"  Step Definition   "+ stepDesc)

    def tcInfo(self, **kwargs):
        '''
        tcInfo:
        API to set the test case common.LogOutput("info", (name, description and cleanupfunction) with the passed test case description.
        '''
        tcName= kwargs.get("tcName")
        tcDesc= kwargs.get("tcDesc")
        tcCleanupFn= kwargs.get("tcCleanupFn")
        self.tcStepDetail["tcName"] = tcName
        self.tcStepDetail["tcDescription"] = tcDesc
        self.tcName = tcName
        self.tcDescription = tcDesc
        common.LogOutput("info", "###TCINFO+"+"#"*110)
        common.LogOutput("info", "Test Case name and Description :: " + self.tcName + "  ::" +self.tcDescription)
        common.LogOutput("info", "\n")

    def startStep(self):
        if (self.tcCurrentStep == 0):
		common.LogOutput("info", "###TCINFO-"+"#"*110)
        common.LogOutput("info", "###STEP+"+"#"*112)
        common.LogOutput("info", "Starting Test Step - %s"%self.tcExecutedSteps[self.tcCurrentStep]["tcStepDescription"])

        if (self.tcCurrentStep > self.tcTotalSteps):
                common.LogOutput("error", "Insufficient test case steps are defined")
                return 1
        self.tcExecutedSteps[self.tcCurrentStep]["tcStepStartTime"] = time.time()
        self.tcStepStatus = TC_STEPSTATUS_INCOMPLETE
        self.tcStepReturnCode = TC_STEPVERDICT_PASS
        #check whether is the first step of test case and take action
        if (self.tcCurrentStep == 0):
                self.tcStartTime = time.time()

    def setVerdictAction(self, stepVerdict = 0, stepFailAction = "EXIT"):
        self.tcStepStatus = stepVerdict
        self.tcStepFailAction = stepFailAction


    def endStep(self, **kwargs):

        stepVerdict = kwargs.get("stepVerdict")
        failAction = kwargs.get("failAction")
        self.tcExecutedSteps[self.tcCurrentStep]["tcStepEndTime"] = time.time()
        self.tcStepReturnCode = stepVerdict


        self.tcExecutedSteps[self.tcCurrentStep]["tcStepExecTime"] =  self.tcExecutedSteps[self.tcCurrentStep]["tcStepEndTime"] -  self.tcExecutedSteps[self.tcCurrentStep]["tcStepStartTime"]
        self.tcExecutedSteps[self.tcCurrentStep]["tcStepReturnCode"] = stepVerdict
        self.tcExecutedSteps[self.tcCurrentStep]["tcFailAction"] = failAction

        #process stepVerdict parameter 1- failed, 0 - passed
        if (self.tcStepReturnCode == TC_STEPSTATUS_FAILED):
                self.tcStepStatus = TC_STEPSTATUS_FAILED
                self.tcReturnCode = TC_EXECSTATUS_FAILED 
                self.tcExecutedSteps[self.tcCurrentStep]["tcStepStatus"] = TC_STEPSTATUS_FAILED
                self.tcVerdict = TC_STEPVERDICT_FAIL
                self.tcStepFailAction = failAction
        else:
                self.tcStepStatus = TC_STEPSTATUS_PASSED
                self.tcExecutedSteps[self.tcCurrentStep]["tcStepStatus"] = TC_STEPSTATUS_PASSED

        self.logTcStepResult()
        #increment the current step
        self.tcCurrentStep += 1
        #check this as a final step
        if ((self.tcCurrentStep == self.tcTotalSteps) or (self.tcStepFailAction == "exit")):
                self.tcEndTime = time.clock()
                self.logTcSummaryResult()
                self.tcFinal()
        if (self.tcStepFailAction == TC_STEPFAILACTION_EXIT):
                print "calling cleanup before exit"
                self.cleanup()
                sys.exit()




    def tcFinal(self):
        totalSteps = 0
	talliedSteps = 0
        stepsPassed = 0
        stepsFailed = 0
        stepsIncomplete = 0
        stepsSkipped = 0
        tcExecutionTime = 0
        tcTestVerdict = "PASSED"
        for tcStep in self.tcExecutedSteps:
		totalSteps += 1
                if(tcStep["tcStepStatus"] == TC_STEPSTATUS_FAILED):
                        stepsFailed += 1
                elif (tcStep["tcStepStatus"] == TC_STEPSTATUS_PASSED):
                        stepsPassed += 1
                else:
                        stepsIncomplete += 1
			stepsSkipped += 1
                tcExecutionTime = tcExecutionTime + tcStep["tcStepExecTime"]
        if (stepsFailed > 0 or stepsIncomplete > 0):
                tcTestVerdict = "FAILED"
        talliedSteps = stepsPassed + stepsFailed +stepsIncomplete
        common.LogOutput("info",      "#")
        common.LogOutput("info",      "#            Test Case Totals")
        common.LogOutput("info",      "#")
        common.LogOutput("info",      "# %-20s: %s"%("Test Case", self.tcName))
        common.LogOutput("info",      "#")
        common.LogOutput("info",      "#"+"-"*119)
        common.LogOutput("info",      "# %-20s: %-10d"%("Steps Passed", stepsPassed))
        common.LogOutput("info",      "# %-20s: %-10d"%("Steps Failed", stepsFailed))
        common.LogOutput("info",      "# %-20s: %-10d"%("Steps Not Executed", stepsIncomplete))
        common.LogOutput("info",      "# %-20s: %-10d"%("Steps Skipped", stepsSkipped))
        common.LogOutput("info",      "#"+"-"*119)
        common.LogOutput("info",      "# %-20s: %d/%d"%("Steps defined/tallied", totalSteps, talliedSteps))
        common.LogOutput("info",      "#")
        common.LogOutput("info",      "#")
        common.LogOutput("info",      "# %-20s: %-10s"%("Final Verdict", tcTestVerdict))
        common.LogOutput("info",      "# %-20s: %-10d"%("Return Code", self.tcReturnCode))
        common.LogOutput("info",      "# %-20s: %-10.3f"%("Execution Time", tcExecutionTime))
        common.LogOutput("info",      "#")
        common.LogOutput("info",      "\n###RESULT-"+"#"*110)

    def logTcStepResult(self):

        logBuffer = "Testcase= %s Step= %s Status= %s ExecTime_in_seconds= %d"%(self.tcName, self.tcExecutedSteps[self.tcCurrentStep]["tcStepDescription"],
                        self.tcExecutedSteps[self.tcCurrentStep]["tcStepStatus"], self.tcExecutedSteps[self.tcCurrentStep]["tcStepExecTime"])
        common.LogOutput("info", "\n")
        common.LogOutput("info", "Status - %-10s\t Execution Time - %-10.3f " % (self.tcExecutedSteps[self.tcCurrentStep]["tcStepStatus"],self.tcExecutedSteps[self.tcCurrentStep]["tcStepExecTime"]))
        common.LogOutput("info", "###STEP-"+"#"*112)


    #logging results/errors test case wise to summary file for all of the steps
    def logTcSummaryResult(self):
        common.LogOutput("info",      "\n###RESULT+"+"#"*110)
        common.LogOutput("info",      "#")
        common.LogOutput("info",      "#            Test Case Status")
        common.LogOutput("info",      "#")
        common.LogOutput("info",      "# %-20s: %s"%("Test Case", self.tcName))
        common.LogOutput("info",      "#")
        common.LogOutput("info",      "# %-15s %-10s %-9s\t%s"%("Steps", "Result", "Second(S)", "Description"))
        common.LogOutput("info",      "#"+"-"*119)

        stepCtr = 0
        for tcStep in self.tcExecutedSteps:
                stepCtr += 1
                common.LogOutput("info",      "# Steps %-10d %-10s %-10.3f\t%s"%(stepCtr, tcStep["tcStepStatus"], tcStep["tcStepExecTime"], tcStep["tcStepDescription"]))
        

    def cleanup(self):
        print "Baseclass tcAction cleanup"


