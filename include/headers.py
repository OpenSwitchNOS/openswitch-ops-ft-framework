# # All import code should be brought in here
# Global Variables
global TOPOLOGY # Physical Topology ETREE
global LOGICAL_TOPOLOGY # Logical Topology ETREE
global topo # Topology dictionary for logical to physical mapping
global libDirs
global topoType # Topology type - virtual / physical
global mininetGlobal # global mininet instance
global ResultsDirectory
global TftpImage
global TC_STEPSTATUS_INCOMPLETE
global TC_STEPSTATUS_FAILED
global TC_STEPSTATUS_PASSED
global TC_STEPVERDICT_FAIL
global TC_STEPVERDICT_PASS
global TC_STEPFAILACTION_CONTINUE
global TC_STEPFAILACTION_EXIT
global TC_EXECSTATUS_PASSED
global TC_EXECSTATUS_FAILED

# TCL SH backend
global tclsh_handle
ResultsDirectory = dict()
TftpImage = dict()


# Logical Topo Dictionary
topo = dict()

# Need to add to this list everytime we create a new directory
libDirs = ['common', 'console', 'host', 'switch', 'switch/OVS', 'switch/CLI', 'topology']

TC_STEPSTATUS_INCOMPLETE = "incomplete"
TC_STEPSTATUS_FAILED = "failed"
TC_STEPSTATUS_PASSED = "passed"
TC_STEPVERDICT_FAIL = 1
TC_STEPVERDICT_PASS = 0
TC_STEPFAILACTION_CONTINUE = "continue"
TC_STEPFAILACTION_EXIT = "exit"
TC_EXECSTATUS_PASSED = 0
TC_EXECSTATUS_FAILED = 1
