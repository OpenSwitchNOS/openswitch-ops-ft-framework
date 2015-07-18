# Master library import area
import argparse
import json
import os
import sys
import time
import datetime
import shutil


# Halon Specific Global Variable
import headers

# Command line argument parser
parser = argparse.ArgumentParser(description='OpenHalon environment test shell')
parser.add_argument('--testCase', help="testcase name to run", required=True, dest='testCaseName')
parser.add_argument('--physicalTopology', help="physical topology filename", required=False, dest='phystopo', default='virtual')
parser.add_argument('--image',help="Valid tftp image for physical Halon switch",required=False, dest='image', default=None)
args = parser.parse_args()

# For Python3 since it is vastly different than 2, we need to provision in the PYTHONPATh all of our directory structure for libraries
pythonPathString = ""
fwbase = os.environ['FT_FRAMEWORK_BASE']
appendDir = fwbase + "/lib"
sys.path.append(appendDir)
for curDir in headers.libDirs:
    appendDir = fwbase + "/lib/" + curDir
    sys.path.append(appendDir)
    if pythonPathString != "":
        pythonPathString += ":"+appendDir
    else:
        pythonPathString += appendDir

entftbase = os.environ['FT_FRAMEWORK_ENT']
if entftbase != "":
    appendDir = entftbase + "/lib"
    sys.path.append(appendDir)
    if pythonPathString != "":
        pythonPathString += ":"+appendDir
    else:
        pythonPathString += appendDir

# Local Framework includes
import common
import console
import switch
import switch.OVS
import topology
import switch.CLI
import host
import pdb
try:
    import RTL
except ImportError:
    common.LogOutput('debug', "RTL environment not available")

#Extract the test case name here
testCaseNamePathList = args.testCaseName.split('/')
testCaseName = testCaseNamePathList[len(testCaseNamePathList) - 1]


# Create Result Directory Structure
# Creating the base results directory structure 
# Results directory is created in the local testware/results folder
# Framework provides the dictionary global variable headers.ResultsDirectory which points to 
# the results directory the keys are the files present (Current keys :: summary.log , detail.log
# Dictionary Usage eg :: headers.ResultsDirectory['summaryLog']
# Script exits with error code (1) if the directory structure is not created 

currentDir = common.GetCurrentDirectory()
ts = time.time()
timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%b-%d_%H:%M:%S')
baseResultsDir =  os.environ['FT_FRAMEWORK_BASE']+"/results"

#Setting the global variable headers.ResultsDirectory 
headers.ResultsDirectory['resultsDir'] = baseResultsDir+"/"+timeStamp+"/"
headers.ResultsDirectory['rtlDir'] = baseResultsDir+"/"+timeStamp+"/RTL"
headers.ResultsDirectory['summaryLog'] = headers.ResultsDirectory['resultsDir']+"summary.log"
headers.ResultsDirectory['detailLog'] = headers.ResultsDirectory['resultsDir']+"detail.log"
headers.ResultsDirectory['testcaseName'] = testCaseName
#headers.TftpImage['Image'] = args.image

if args.phystopo != "virtual" :
    TopologyXMLPath = args.phystopo
else :
    TopologyXMLPath = args.phystopo

retCode = common.ChangeDirectory(baseResultsDir)
if retCode['returnCode'] == 0 :
    retCode  = common.CreateDirectory(baseResultsDir+"/"+timeStamp+"/.")
if retCode['returnCode'] == 0:
    common.ChangeDirectory(headers.ResultsDirectory['resultsDir'])
    
    # Create RTL directory
    if args.phystopo != "virtual":
        retCode  = common.CreateDirectory(baseResultsDir+"/"+timeStamp+"/RTL/.")
    #Create Files under the result directory structure(summary file)
    retCode = common.FileCreate(headers.ResultsDirectory['resultsDir'],"summary.log")
    if retCode['returnCode'] <> 0 :
        common.LogOutput('error',"File summary.log not created in the directory structure")
        exit(1)
    #Create Files under the result directory structure(detail.log) 
    retCode = common.FileCreate(headers.ResultsDirectory['resultsDir'],"detail.log")
    if retCode['returnCode'] <> 0 :
        common.LogOutput('error',"File detail.log not created in the directory structure")
        exit(1)
    #Copy topology.xml and the testcase file to results directory for reference 
    try :
        shutil.copy(args.testCaseName,headers.ResultsDirectory['resultsDir'])
    except :
        common.LogOutput('error',"Testcase file not copied to destination -> "+headers.ResultsDirectory['resultsDir'])
        exit(1)
else :
    common.LogOutput('error',"Result Directory structure not created . Exiting")
    exit(1)

# Header printblock
common.LogOutput('info', "", datastamp=True)
common.LogOutput('info' , "Test Case is: " + args.testCaseName)
common.LogOutput('info' , "Physical Topology is: " + args.phystopo)
headers.topoType =""
# Read in the Topology
if args.phystopo == "virtual":
    headers.topoType = "virtual"
    common.LogOutput('info', "Topology is virtual - creating environment specified in the test case topoDict structure")
    rtStruct = topology.TopologyDictGet(testcase=args.testCaseName)
    returnCode = common.ReturnJSONGetCode(json=rtStruct)
    if returnCode != 0:
        # There is an issue, we specifigied topology is virutal and we don't have a definition
        common.LogOutput('error', "Specified topology is virtual, but no topology dictionary specified in test case.")
        exit(1)
    # PUll the dictionary information
    curTopoDict = common.ReturnJSONGetData(json=rtStruct)
    topology.VirtualXMLCreate()
    # Create the virtual topology
    headers.mininetGlobal = topology.VirtualTopo()
    headers.mininetGlobal.setupNet(topoDictionary=curTopoDict)
    topology.TopologyXMLWrite()
    topology.LogicalTopologyCreate(topoDict=curTopoDict)
elif str.isdigit(args.phystopo) is True:
    headers.topoType = "physical"
    # This means we have passed a reservation in
    common.LogOutput('info', "Topology reservation ID was passed in.  ID = " + str(args.phystopo))
    # Create the logical topology from the test case
    rtStruct = topology.TopologyDictGet(testcase=args.testCaseName)
    curTopoDict = common.ReturnJSONGetData(json=rtStruct)
    topology.LogicalTopologyCreate(topoDict=curTopoDict)

    # Start up the back end TCL shell
    RTL.TCLShellCreate()
    RTL.TopologyCreate(rsvnId=args.phystopo)
else:
    rtStruct = topology.TopologyDictGet(testcase=args.testCaseName)
    curTopoDict = common.ReturnJSONGetData(json=rtStruct)
    topology.LogicalTopologyCreate(topoDict=curTopoDict)
    headers.TOPOLOGY = common.XmlFileLoad(args.phystopo)
    if headers.TOPOLOGY == None:
        common.LogOutput('info', "Failed to open topology " + args.phystopo + " file." )

#This is the beginning of execution template
#The base class (tcAction) and the variables in the headers library used by tcAction are procured here :
from headers import *
#Instantiate the base class tcAction here
tcInstance = common.tcAction()

with open(args.testCaseName) as f:
    code = compile(f.read(), args.testCaseName, 'exec')
    exec(code)

# WE can do some closeup code here.
if headers.topoType == "virtual":
    common.LogOutput('info', "Tearing down virtual environment")
    headers.mininetGlobal.terminate_nodes()
