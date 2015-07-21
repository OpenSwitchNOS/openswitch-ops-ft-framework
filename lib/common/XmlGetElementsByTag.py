###PROC+#####################################################################
# Name:        common.XmlGetElementsByTag
#
# Namespace:   common
#
# Author:      Vince Mendoza
#
# Purpose:     Routine searches elements in the etree by tag
#
# Params:      etree - tree you are searching
#              tag - this can be either a string or a xpath query string
#              allElements = Default = False.  Will look for 1 element
#                            if set to True, will look for multiples
#
# Returns:     elements - element matching.  If there is no element None is
#                        returned
#
##PROC-#####################################################################
import xml.etree.ElementTree

def XmlGetElementsByTag(etree, tag, **kwargs):
    allElements = kwargs.get('allElements', False)
    if allElements is False:
       elements = etree.find(tag)
    else:
       elements = etree.findall(tag)
    #typeTrue = xml.etree.ElementTree.iselement(elements)
    #print elements
    #print typeTrue
    return elements
