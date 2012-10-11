#!/usr/bin/python

import os
import commands
import sys
from time import strftime

# Prepare the log file
global logfile
logfile = open("/var/log/netrunner-system.log", "w")

def log (string):
	logfile.writelines("%s - %s\n" % (strftime("%Y-%m-%d %H:%M:%S"), string))
	logfile.flush()

log("netrunner-system started")

try:
	# Read configuration	
	from configobj import ConfigObj
	config = ConfigObj("/etc/netrunner/netrunner-system.conf")
	
	# Default values
	if ('global' not in config):
		config['global'] = {}
	if ('enabled' not in config['global']):
		config['global']['enabled'] = "True"
	if ('restore' not in config):
		config['restore'] = {}
	if ('lsb-release' not in config['restore']):
		config['restore']['lsb-release'] = "True"
	if ('etc-issue' not in config['restore']):
		config['restore']['etc-issue'] = "True"	
	config.write()


	# Exit if disabled
	if (config['global']['enabled'] == "False"):
		log("Disabled - Exited")
		sys.exit(0)

	adjustment_directory = "/etc/netrunner/adjustments/"

	# Perform file execution adjustments
	for filename in os.listdir(adjustment_directory):
		basename, extension = os.path.splitext(filename)
        	if extension == ".execute":
	            full_path = adjustment_directory + "/" + filename
        	    os.system("chmod a+rx %s" % full_path)
	            os.system(full_path)
        	    log("%s executed" % full_path)

	# Perform file overwriting adjustments

	array_preserves = []
	if os.path.exists(adjustment_directory):
		for filename in os.listdir(adjustment_directory):
    			basename, extension = os.path.splitext(filename)
			if extension == ".preserve":
				filehandle = open(adjustment_directory + "/" + filename)
				for line in filehandle:
					line = line.strip()
					array_preserves.append(line)
				filehandle.close()
	overwrites = {}
	if os.path.exists(adjustment_directory):
		for filename in sorted(os.listdir(adjustment_directory)):
    			basename, extension = os.path.splitext(filename)
			if extension == ".overwrite":
				filehandle = open(adjustment_directory + "/" + filename)
				for line in filehandle:
					line = line.strip()					
					line_items = line.split()
					if len(line_items) == 2:
						source, destination = line.split()
						if destination not in array_preserves:							
							overwrites[destination] = source
				filehandle.close()

	for key in overwrites.keys():
		source = overwrites[key]
		destination = key
		if os.path.exists(source):
			if not "*" in destination:
				# Simple destination, do a cp
				if os.path.exists(destination):
					os.system("cp " + source + " " + destination)
					log(destination + " overwritten with " + source)
			else:
				# Wildcard destination, find all possible matching destinations
				matching_destinations = commands.getoutput("find " + destination)
				matching_destinations = matching_destinations.split("\n")
				for matching_destination in matching_destinations:					
					matching_destination = matching_destination.strip()
					if os.path.exists(matching_destination):
						os.system("cp " + source + " " + matching_destination)
						log(matching_destination + " overwritten with " + source)		
				

except Exception, detail:
	print detail
	log(detail)

log("netrunner-system stopped")
logfile.close()

