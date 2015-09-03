##########################################################################################
# Name:        switch.CLI.LAG.InterfaceShow
#
# Namespace:   switch.CLI.LAG
#
# Author:      Randall Loaiza
#
# Purpose:     Library function to configure LAG parameters on an interface
#
# Params:      deviceObj - device object.
#              interface - interface to config   
#              lagId - Name to identify the LAG which the interface belongs
#              lacpPortId - Range between 1 and 65535 to identify port in LACP
#              lacpPortPriority - Range between 1 and 65535 to assign priority of interface between members of same dynamic LAG (LACP)
#              lacpAggKey - Range betwen 1 and 65535. Key used to identify all members of LAG to be of the same 2 switches. Will probably not be added in Basil
#              enable - True for configuration/false for removing LAG  
#
# Returns:     JSON structure
#              returnCode - status of command(0 for pass , gets errorcodes for failure)
#              data: 
#
##PROC-###################################################################################

from lib import *
import re
import time

def LagInterfaceConfig(**kwargs):