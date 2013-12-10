#!/usr/bin/python

"""
Inciga and/or Nagios script for monitoring Ethernet OAM LBM status 
"""

import sys
import subprocess
from optparse import OptionParser
from collections import defaultdict

ErrorStateString = { 0: "OK", 1: "WARNING", 2: "CRITICAL"}

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# Parse and check arguments

def buildParser():
	"""
	Prepare parsing of command line options
	"""

	parser = OptionParser("usage: %prog [options] destination_MAC")

	parser.add_option("-i", "--interface", 
		      	  dest="interface",
                  	  help="interface to use",
		  	  default="",
			  metavar="INTERFACE")
	parser.add_option("-v", "--vlan", 
		    	  dest="vlan", 
			  default="",
                  	  help="vlan to query", 
		  	  metavar="VLAN")
	parser.add_option("-l", "--mdlevel", 
		  	  dest="mdlevel",
			  default="",
                  	  help="OAM Maintentance Level", 
		  	  metavar="MDLEVEL")
	parser.add_option("-c", "--count", 
		  	  dest="count", 
			  default='5',
                  	  help="number of ethpings to send", 
		 	  metavar="COUNT")
        parser.add_option("-w", "--warn_on_packetloss",
                          dest="warn_on_packetloss",
                          default='1',
			  help="Return warning on packetloss 1=yes 0=no (default=1)",
                          metavar="WARN_ON_PACKETLOSS")
	return parser



def main():
	"""
	Main function for check_ethping.py 
	"""
	
	ErrorState=0

	# Parse options and arguments

	parser = buildParser()
	(options, args) = parser.parse_args()
	if len(args) == 0:
        	print "No destination_MAC specified --exiting"
        	quit()
	if len(options.interface) == 0:
		print "No interface specified --exiting"		
		quit()
 	

	# prepare and generate system call for executing ethping

	call = ["/usr/local/bin/ethping","-i",options.interface,"-c",options.count]
	if len(options.vlan) > 0:
		call.append("-v")
		call.append(options.vlan)
        if len(options.mdlevel) > 0:
		call.append("-l")
		call.append(options.mdlevel)
	call.append(args[0])
	
	ret = subprocess.check_output(call)
	result = ret.split("ms")
	
	RTTlist= []
	for i in result:
		value = i[i.rfind(', ')+1:].strip(' ')
		if is_number(value) :
			RTTlist.append(float(value))
	
	if len(RTTlist) == 0:
		packetloss = 100
		RTA = 0
	else:
		packetloss = 100.0 - (len(RTTlist) / int(options.count)) * 100
		RTA = sum(RTTlist)/len(RTTlist)
	
	if (packetloss > 0) & (options.warn_on_packetloss == '1'): ErrorState = 1
        if packetloss == 100: ErrorState = 2	
	
	print "PING {0} {1} - Packet loss = {2}%, RTA = {3:.4f} ms".format(args[0],ErrorStateString[ErrorState], int(packetloss), RTA)
 
	# Exit with value to inform Nagios / Icinga
	sys.exit(ErrorState)

if __name__ == "__main__":
    main()
