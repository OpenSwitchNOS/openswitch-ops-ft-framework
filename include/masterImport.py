import argparse
import json
import os
import sys
import time
import datetime
import shutil


import lib
import common
#import console
import switch
import switch.OVS
#import topology
import switch.CLI
import host
import pdb

try:
    import RTL
except ImportError:
    common.LogOutput('debug', "RTL environment not available")
    #t "no rtl"