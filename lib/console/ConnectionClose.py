###PROC+#####################################################################
# Name:        console.ConnectionClose
#
# Namespace:   console
#
# Author:      Vince Mendoza
#
# Purpose:     Close connection with console server
#
#
# Params:      connection
#
# Returns:     returnCode
#
##PROC-#####################################################################
import pexpect
import headers
import common
import console
import xml.etree.ElementTree

def ConnectionClose(**kwargs):
    # Look up the device name in the topology - grab connectivity information
    connection = kwargs.get('connection')
    connection.close()

    return 0


