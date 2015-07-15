###PROC+#####################################################################
# Name:        console.Connect
#
# Namespace:   console
#
# Author:      Vince Mendoza
#
# Purpose:     Connect to device under test
#              
#
# Params:      device - device name
#
# Returns:     connectHandle - Connection handle or None if no connection is made
#
##PROC-#####################################################################
import pexpect
import headers
import common
import console
import switch
import xml.etree.ElementTree

def Connect(device):
    # Look up the device name in the topology - grab connectivity information
    xpathString = ".//device[name='" + device + "']"
    etreeElement = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
    if etreeElement == None:
       # We are not in a good situation, we need to bail
       common.LogOutput('error', "Could not find device " + device + " in topology")
       return None
    
    # Grab IP from etree
    xpathString = ".//device[name='" + device + "']/connection/ipAddr"
    ipNode = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
    if ipNode == None:
       common.LogOutput('error', "Failed to obtain IP address for device " + device )
       return None
    
    ipAddress = ipNode.text
    common.LogOutput ('debug', device + " connection IP address:  " + ipAddress)
    
    # Grab a connetion element - not testing this since this should exist since we obtained
    # things before us
    xpathString = ".//device[name='" + device + "']/connection"
    connectionElement = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
    
    # Grab authentication pieces out of the XML 
    # username
    xpathString = ".//device[name='" + device + "']/login/user"
    userElement = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
    userName = userElement.text
    
    # password
    xpathString = ".//device[name='" + device + "']/login/password"
    passwordElement = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
    password = passwordElement.text
    
    # admin password
    xpathString = ".//device[name='" + device + "']/login/adminPassword"
    adminPasswordElement = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
    adminPassword = adminPasswordElement.text
    
    # Create Telnet handle and open Console expect logging 

    common.LogOutput("debug","Clearing Console and opening Console expect logging")
    telnetString = "telnet " + ipAddress
    ConsoleFileString  = "Console_"+ipAddress+".log"    
    ExpectIns = switch.ExpectLog.DeviceLogger(ConsoleFileString)
    ConsoleLogFile = ExpectIns.OpenExpectLog(ConsoleFileString)
    if ConsoleLogFile == 1 :
     common.LogOutput('error', "Unable to create Console expect log file")
     exit(1)
    #Opening an expect connection to the device with the specified log file
    common.LogOutput('debug', "Opening an expect connection to the device with the specified log file"+ConsoleFileString)
    tclient = pexpect.spawn (telnetString,logfile=switch.ExpectLog.DeviceLogger(ConsoleLogFile))

    
    # Not doing logging until we have the logs ironed out.
    #tclient.logfile = file('/tmp/vinceTest.log', 'w')
    #tclient.logfile = open('/tmp/vinceTest.log', 'w')
    
    # Lets go and detect our connection - this will get us to a context we know about
    retVal = console.DetectConnection(connection=tclient, username=userName, password=password, adminPassword=adminPassword)
    if retVal is None:
       common.LogOutput('error', "Failed to detect connection for device")
       return None
    
    # Now lets put in the topology the expect handle
    #spawnIdElement = xml.etree.ElementTree.SubElement(connectionElement, 'spawnId')
    #print spawnIdElement
    #myfd = tclient.fileno()
    #idElement = xml.etree.ElementTree.SubElement(spawnIdElement, "id")
    #idElement.text = str(myfd)
    #print tclient
    return tclient
    
    
