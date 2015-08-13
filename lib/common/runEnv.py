import argparse
import os
import sys
import time
import datetime
#import shutil
import common
import headers
#import lib



class testEnv ():
    def __init__(self, **kwargs):
        self.topoDict = kwargs.get('topoDict')
        
        self.rsvnId = None
        self.topoObj = None
        self.libDirs = ['common', 'console', 'host', 'switch', 'switch/OVS', 'switch/CLI', 'topology']
        self.ResultsDirectory = dict()
        self.envSetup()
        # Here is where we will stub in the provisionng logic.  We should have a topoObj by now 
        self.topoObj.CreateDeviceObjects()
        if self.rsvnId != "virtual":
            common.LogOutput('info', "Enabling all logical links")
            self.topoObj.LinkModifyStatus(enable=1, allLogical=1)
        
        
    def envSetup(self):
        # Command line argument parser
        parser = argparse.ArgumentParser(description='OpenHalon environment test shell')
        #parser.add_argument('--testCase', help="testcase name to run", required=True, dest='testCaseName')
        parser.add_argument('--physicalTopology', help="physical topology filename", required=False, dest='phystopo', default='virtual')
        parser.add_argument('--targetBuild', help="List of logical DUTs and coorsponding builds to provision", required=False, dest='targetBuild', default=None)
        parser.add_argument('--resultDir', help="Result directory for the test case to put results in", required=False, dest='resultDir', default=None)
        args = parser.parse_args()
        self.rsvnId = args.phystopo
        self.targetBuild = args.targetBuild
        self.resultDir = args.resultDir
        #self.image = args.image
        
        
        pythonPathString = ""
        fwbase = os.environ['FT_FRAMEWORK_BASE']
        sys.path.append(fwbase)
        appendDir = fwbase + "/lib"
        sys.path.append(appendDir)
        
        for curDir in self.libDirs:
            appendDir = fwbase + "/lib/" + curDir
            sys.path.append(appendDir)
            if pythonPathString != "":
                pythonPathString += ":" + appendDir
            else:
                pythonPathString += appendDir

        entftbase = os.environ['FT_FRAMEWORK_ENT']
        if entftbase != "":
            appendDir = entftbase
            sys.path.append(appendDir)
            if pythonPathString != "":
                pythonPathString += ":" + appendDir
            else:
                pythonPathString += appendDir
            appendDir = entftbase + "/lib"
            sys.path.append(appendDir)
            if pythonPathString != "":
                pythonPathString += ":" + appendDir
            else:
                pythonPathString += appendDir
                
            appendDir = entftbase + "/lib/RTL"
            sys.path.append(appendDir)
            if pythonPathString != "":
                pythonPathString += ":" + appendDir
            else:
                pythonPathString += appendDir
        
        masterImport = fwbase + "/include/masterImport.py"
        with open(masterImport) as f:
            code = compile(f.read(), masterImport, 'exec')
            exec(code)
        
        if args.resultDir is None:
            # Means we need to create the results structure
            currentDir = common.GetCurrentDirectory()
            ts = time.time()
            timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%b-%d_%H:%M:%S')
            baseResultsDir = os.environ['FT_FRAMEWORK_BASE'] + "/results"
            self.ResultsDirectory['resultsDir'] = baseResultsDir + "/" + timeStamp + "/"
            headers.ResultsDirectory['resultsDir'] = baseResultsDir + "/" + timeStamp + "/"
            self.ResultsDirectory['rtlDir'] = baseResultsDir + "/" + timeStamp + "/RTL/."
            #headers.ResultsDirectory['rtlDir'] = baseResultsDir + "/" + timeStamp + "/RTL/."
        else:
            baseResultsDir = args.resultDir
            self.ResultsDirectory['resultsDir'] = baseResultsDir + "/"
            headers.ResultsDirectory['resultsDir'] = baseResultsDir + "/"
            self.ResultsDirectory['rtlDir'] = baseResultsDir + "/" + "/RTL/"
            #headers.ResultsDirectory['rtlDir'] = baseResultsDir + "/" + "/RTL/"
        
        self.ResultsDirectory['summaryLog'] = self.ResultsDirectory['resultsDir'] + "summary.log"
        #headers.ResultsDirectory['summaryLog'] = self.ResultsDirectory['resultsDir'] + "summary.log"
        self.ResultsDirectory['detailLog'] = self.ResultsDirectory['resultsDir'] + "detail.log"
        #headers.ResultsDirectory['detailLog'] = self.ResultsDirectory['resultsDir'] + "detail.log"
        #self.ResultsDirectory['testcaseName'] = testCaseName
        
        retCode = common.ChangeDirectory(baseResultsDir)
        if retCode['returnCode'] == 0 :
            #if args.resultDir is None:
            #time.sleep(1)
            #retCode = common.CreateDirectory(baseResultsDir + "/" + timeStamp + "/.")
            retCode = common.CreateDirectory(self.ResultsDirectory['resultsDir'])

        if retCode['returnCode'] == 0:
            #common.ChangeDirectory(self.ResultsDirectory['resultsDir'])
            # Create RTL directory
            if args.phystopo != "virtual":
                #if args.resultDir is None:
                    #retCode = common.CreateDirectory(baseResultsDir + "/" + timeStamp + "/RTL/.")
                #print self.ResultsDirectory['rtlDir']
                common.ChangeDirectory(self.ResultsDirectory['resultsDir'])
                #retCode = common.CreateDirectory(self.ResultsDirectory['rtlDir'])
                retCode = common.CreateDirectory("RTL/.")
                #else:
                #    retCode = common.CreateDirectory(baseResultsDir + "/" + "/RTL/.")
            # Create Files under the result directory structure(summary file)
            retCode = common.FileCreate(self.ResultsDirectory['resultsDir'], "summary.log")
            if retCode['returnCode'] <> 0 :
                common.LogOutput('error', "File summary.log not created in the directory structure")
                exit(1)
            # Create Files under the result directory structure(detail.log)
            retCode = common.FileCreate(self.ResultsDirectory['resultsDir'], "detail.log")
            if retCode['returnCode'] <> 0 :
                common.LogOutput('error', "File detail.log not created in the directory structure")
                exit(1)
            # Copy topology.xml and the testcase file to results directory for reference
            #try :
            #    shutil.copy(args.testCaseName, self.ResultsDirectory['resultsDir'])
            #except :
            #    common.LogOutput('error', "Testcase file not copied to destination -> " + self.ResultsDirectory['resultsDir'])
            #    exit(1)
        else :
            common.LogOutput('error', "Result Directory structure not created . Exiting")
            exit(1)
        
        # Header printblock
        common.LogOutput('info', "", datastamp=True)
        #common.LogOutput('info' , "Test Case is: " + args.testCaseName)
        common.LogOutput('info' , "Physical Topology is: " + self.rsvnId)
        
        # Read in the Topology
        if self.rsvnId == "virtual":
            self.topoType = "virtual"
            common.LogOutput('info', "Topology is virtual - creating environment specified in the test case topoDict structure")
            # Create a topology object
            self.topoObj = lib.Topology(topoDict=self.topoDict,runEnv=self)
        elif str.isdigit(args.phystopo) is True:
            self.topoType = "physical"
            # This means we have passed a reservation in
            common.LogOutput('info', "Topology reservation ID was passed in.  ID = " + str(self.rsvnId) + " querying the topology")
            # Create Topology Object
            self.topoObj = RTL.RTL_Topology(topoDict=self.topoDict, topoType="physical", rsvnId=self.rsvnId, runEnv=self)
    
    def topoObjGet(self):
        return(self.topoObj)
