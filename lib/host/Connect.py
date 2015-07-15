###PROC+#####################################################################
# Name:        host.Connect
#
# Namespace:   host
#
# Author:      Srinivasa Krishnappa
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
import switch
import host
import console
import xml.etree.ElementTree
import os

def Connect(device):
    # Look up and see if we are physical or virtual
    xpathString = ".//reservation/id"
    rsvnEtreeElement = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
    if rsvnEtreeElement == None:
        # We are not in a good situation, we need to bail
       common.LogOutput('error', "Could not find reservation id tag in topology")
       return None
    
    rsvnType = rsvnEtreeElement.text
    
   
    # Look up the device name in the topology - grab connectivity information
    xpathString = ".//device[name='" + device + "']"
    etreeElement = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
    if etreeElement == None:
       # We are not in a good situation, we need to bail
       common.LogOutput('error', "Could not find device " + device + " in topology")
       return None
    
    
    if rsvnType == 'virtual':
       # Code for virtual
       # Go and grab the connection name
       xpathString = ".//device[name='" + device + "']/connection/name"
       virtualConn = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
       if virtualConn == None:
          common.LogOutput('error', "Failed to virtual connection for " + device )
          return None
       telnetString = "docker exec -ti " + device + " /bin/bash"
       tclient = pexpect.spawn(telnetString,echo=False)
       tclient.delaybeforesend = .5
       expectFileString  = device + ".log"
       
    else:
       # Code for physical
       # Grab IP from etree
       xpathString = ".//device[name='" + device + "']/connection/ipAddr"
       ipNode = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
       if ipNode == None:
          common.LogOutput('error', "Failed to obtain IP address for device " + device )
          return None
    
       ipAddress = ipNode.text
       common.LogOutput ('debug', device + " connection IP address:  " + ipAddress)
    
       # Grab Port from etree
       xpathString = ".//device[name='" + device + "']/connection/port"
       portNode = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
       if portNode == None:
          common.LogOutput('error', "Failed to obtain Port for device " + device)
          return None
    
       port = portNode.text
       common.LogOutput ('debug', device + " connection port:  " + port)
    
       # Grab a connetion element - not testing this since this should exist since we obtained
       # things before us
       xpathString = ".//device[name='" + device + "']/connection"
       connectionElement = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
       
       # Grab a connetion element - not testing this since this should exist since we obtained
       # things before us
       xpathString = ".//device[name='" + device + "']/connection"
       connectionElement = common.XmlGetElementsByTag(headers.TOPOLOGY, xpathString)
       #Create Telnet handle
       #Enable expect device Logging for every connection 
       #Single Log file exists for logging device exchange using pexpect logger .
       #Device logger  name format :: devicename_IP-Port

       telnetString = "telnet " + ipAddress
       expectFileString  = device+"_"+ipAddress+"--"+port + ".log"
    
    
    ExpectInstance = switch.ExpectLog.DeviceLogger(expectFileString)
    expectLogFile = ExpectInstance.OpenExpectLog(expectFileString)
    if expectLogFile == 1 :
     common.LogOutput('error', "Unable to create expect log file")
     exit(1)
    #Opening an expect connection to the device with the specified log file
    common.LogOutput('debug', "Opening an expect connection to the device with the specified log file"+expectFileString)
    if rsvnType == 'virtual':
       tclient = pexpect.spawn(telnetString, echo=False, logfile=switch.ExpectLog.DeviceLogger(expectLogFile))
       tclient.delaybeforesend = 1
    else:
       tclient = pexpect.spawn (telnetString,logfile=switch.ExpectLog.DeviceLogger(expectLogFile))
 
    # Lets go and detect our connection - this will get us to a context we know about
    retVal = host.DetectConnection(tclient)

    if retVal is None:
       return None
    return tclient
    
