###PROC+#####################################################################
# Name:        topology.VirtualTopology
#
# Namespace:   topology
#
# Author:      Vince Mendoza
#
# Purpose:     Creates a Virtual Topology 
#              
#
# Params:      device - device name
#
# Returns:     
#
##PROC-#####################################################################

from mininet.net import *
from mininet.topo import *
from mininet.node import *
from mininet.link import *
from mininet.cli import *
from mininet.log import *
from mininet.util import *
from subprocess import *
from subprocess import *
from halonvsi.docker import *
from halonvsi.halon import *
import re
import select
import headers
import common
import topology
import shutil

class VirtualTopo( HalonTest ):
    def __init__(self):
       self.id = str(os.getpid())
       self.testdir = "/tmp/halonnet/" + str(self.id)
        
       os.makedirs(self.testdir)
       self.hostmounts = []
       self.switchmounts = []
       
    def setupNet(self, **kwargs):
        topoDictionary = kwargs.get('topoDictionary')
        
        # Print out topology aspects 
        self.topoDevices = str(topoDictionary['topoDevices'])
        self.topoLinks = str(topoDictionary['topoLinks'])
        self.topoFilters = str(topoDictionary['topoFilters'])
        
        # Define Mininet object so we can populate it.
        self.topo = mininet.topo.Topo(hopts=self.getHostOpts(), sopts=self.getSwitchOpts())
        
        logicalTopo = dict()
        for curDev in str.split(self.topoDevices):
           logicalTopo[curDev] = dict()
           logicalTopo[curDev]['attributes'] = dict()
           logicalTopo[curDev]['links'] = dict()
                       
                       
        # Create a local dictionary around the devices in topoFilters
        for curFilter in str.split(self.topoFilters, ','):
           (cDev, cAttr, cVal) = str.split(curFilter, ':')
           logicalTopo[cDev]['attributes'][cAttr] = cVal
        
        
        for curDev in logicalTopo.keys():
           # Grag attributes for each device
           devAttrs = logicalTopo[curDev]['attributes']
           devCategory = devAttrs['system-category']
           if devCategory == "switch":
              common.LogOutput('debug', "Added Switch Device: "+ curDev)
              self.topo.addSwitch(curDev)
           elif devCategory == "workstation":
              common.LogOutput('debug', "Added Workstation Device: "+ curDev)
              self.topo.addHost(curDev)
           
        for curLink in str.split(self.topoLinks,','):
           (link, dev1, dev2) = str.split(curLink, ':')
           common.LogOutput('debug', "Creating Link "+ link +" between "+ dev1 + " & "+ dev2)
           linkKey = self.topo.addLink(dev1, dev2,key=link)
           
           # Add to Link Logical Topology
           logicalTopo[dev1]['links'][link] = dev2
           logicalTopo[dev2]['links'][link] = dev1
           
        #print logicalTopo
        # Configure MiniNet
        self.net = mininet.net.Mininet(topo=self.topo,
                           switch=HalonSwitch,
                           host=HalonHost,
                           link=HalonLink,
                           controller=None,
                           build=True)
        print ""
        
        
        
        # Now we need to query what we have.... to put in the topology
        # We will not formally have mapping, so we will create the mapping array here.
        switches = self.net.switches
        for curSwitch in switches:
           xmlAddRet = topology.VirtualXMLDeviceAdd(name=str(curSwitch.container_name))
           logDevRe = re.match("^\d+_(\S+)", curSwitch.container_name)
           if logDevRe:
              logicalDevice = logDevRe.group(1)
              headers.topo[logicalDevice] = curSwitch.container_name
              headers.topo[curSwitch.container_name] = logicalDevice
        
        hosts = self.net.hosts
        #print hosts
        for curHost in hosts:
           xmlAddRet = topology.VirtualXMLDeviceAdd(name=str(curHost.container_name))
           logDevRe = re.match("^\d+_(\S+)", curHost.container_name)
           if logDevRe:
              logicalDevice = logDevRe.group(1)
              headers.topo[logicalDevice] = curHost.container_name
              headers.topo[curHost.container_name] = logicalDevice
        
        # Query Links and update the XML
        
        topoLinkMininet  = self.topo.iterLinks(withKeys=True, withInfo=True)
        for curLink in topoLinkMininet:
           linkName = curLink[2]
           print curLink
           #linkstatus = curLink.status
           #print "Current Line: " + str(linkName) +"status = "+ str(linkstatus)
           #print linkName
           linkInfo = curLink[3]
           #print linkInfo
           node1 = linkInfo['node1']
           node1Obj = self.searchNetNodes(headers.topo[node1])
           node1port = linkInfo['port1']
           node1IntStruct = node1Obj.intfList()
           #print node1IntStruct
           
           node2 = linkInfo['node2']
           node2Obj = self.searchNetNodes(headers.topo[node2])
           node2port = linkInfo['port2']
           node2IntStruct = node2Obj.intfList()
           #print node2IntStruct
           
           
           # Add link to Topology XML
           retStruct = topology.VirtualXMLLinkAdd(link=linkName, 
                                                  device1=headers.topo[node1], 
                                                  device1Port=node1IntStruct[node1port], 
                                                  device2=headers.topo[node2], 
                                                  device2Port=node2IntStruct[node2port])
           headers.topo[linkName] = linkName
           
           
        # print out topology mapping
        common.LogOutput('info', "=====================================================================")
        common.LogOutput('info', "Topology Mapping")
        for curDev in str.split(self.topoDevices):
           outstring = curDev + "  =  " + headers.topo[curDev]
           common.LogOutput('info', outstring)
           
        # LEts go and resolve the links
        for curLink in str.split(self.topoLinks, ','):
           (link, dev1, dev2) = str.split(curLink, ':')
           dev1LportStruct = topology.InterfaceGetByDeviceLink(device=headers.topo[dev1], link=link)
           if common.ReturnJSONGetCode(json=dev1LportStruct) != 0:
              # didn't get link info
              common.LogOutput('error', "Unable to obtain link information for "+ link + " for " + dev1)
              continue
           dev1Lport = common.ReturnJSONGetData(json=dev1LportStruct)
           
           dev2LportStruct = topology.InterfaceGetByDeviceLink(device=headers.topo[dev2], link=link)
           if common.ReturnJSONGetCode(json=dev2LportStruct) != 0:
              # didn't get link info
              common.LogOutput('error', "Unable to obtain link information for "+ link + " for " + dev2)
              continue
           dev2Lport = common.ReturnJSONGetData(json=dev2LportStruct)
           
           outstring = link + "  =  " + headers.topo[dev1] + ":" + str(dev1Lport) + " <==> " + headers.topo[dev2] + ":" + str(dev2Lport)
           common.LogOutput('info', outstring)
        common.LogOutput('info', "=====================================================================")

    # Routine to alter link state
    def VirtualLinkModifyStatus(self, **kwargs):
       link = kwargs.get('link', None)
       status = kwargs.get('status', 'down')
       # Find out who the link belongs to - can do this with the logical topology
       xpath = "./link[@name='"+ str(link) + "']" 
       linkNameElement = common.XmlGetElementsByTag(headers.LOGICAL_TOPOLOGY, xpath)

       linkAttrs = linkNameElement.attrib
       device1 = linkAttrs['device1']
       device2 = linkAttrs['device2']
       
       self.net.configLinkStatus(device1, device2, status)
       retString = common.ReturnJSONCreate(returnCode=0)
       return(retString)
    
    # Restart Switch
    def RestartSwitch(self, **kwargs):
       switch = kwargs.get('switch', None)
       common.LogOutput('info', "Restarting Virtual Switch: "+ switch)
       switches = headers.mininetGlobal.net.switches
      
       for curSwitch in switches:
          if switch == curSwitch.container_name:
             switchObj = curSwitch
             #print switchObj
             break
       
       mylogicalDev = headers.topo[switch]
       
       # Lets cleanup the old container
       switchObj.terminate()
       
       # Clean up old directory so we do not run into issues outside of our control
       mydir = switchObj.testdir + "/" + mylogicalDev
       shutil.rmtree(mydir)
       
       # We actually really need to add the switch again in order to get everything
       # properly setup to as it was before.
       self.net.addSwitch(mylogicalDev, testid=str(self.id),testdir=str(self.testdir))
       
       # Now search for links in the logical topology that are in respect to this dev and add them.
       for curLink in str.split(self.topoLinks,','):
           (link, dev1, dev2) = str.split(curLink, ':')
           if dev1 == mylogicalDev or dev2 == mylogicalDev:
              # we need to add the link
              common.LogOutput('debug', "Creating Link "+ link +" between "+ dev1 + " & "+ dev2)
              self.net.addLink(dev1, dev2)
       
       return None
       
    # Routine to search for Net Node
    def searchNetNodes(self, name):
        switches = self.net.switches
        hosts = self.net.hosts
        
        for curSwitch in switches:
           if curSwitch.container_name == name:
              return(curSwitch)
         
        for curHost in hosts:
            if curHost.container_name == name:
               return(curHost)
        
        return(None)
        
    def terminate_nodes(self):
        # gather up all nudes
        switch_list = self.net.switches
        host_list = self.net.hosts
        
        for curSwitch in switch_list:
           common.LogOutput('debug', "terminating "+ str(curSwitch))
           curSwitch.terminate()
      
        for curHost in host_list:
           common.LogOutput('debug', "terminating "+ str(curHost))
           curHost.stop()
           curHost.terminate()
