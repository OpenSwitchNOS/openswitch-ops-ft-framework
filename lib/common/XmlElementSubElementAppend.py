###PROC+#####################################################################
# Name:        common.XmlElementSubElementAppend
#
# Namespace:   common
#
# Author:      Vince Mendoza
#
# Purpose:     Routine adds a subelement to an parent element in the etree
#
# Params:      parentElement - Etree element
#              childElement  - Etree element
#
# Returns:     etree - child element
#
##PROC-#####################################################################
import xml.etree.ElementTree


def XmlElementSubElementAppend(parentElement, childElement):
    mychild = parentElement.append(childElement)
    return mychild
    