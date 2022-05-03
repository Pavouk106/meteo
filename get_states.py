#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, os.path, urllib, re

debug = False

path_to_files = '/tmp/'

states_values = [0] * 4

retry = 0

# Print debug function
def debug_print(text):
	if debug:
		print(text)

while 1:
	# Teploty z kotelny
	states_file = open(path_to_files + 'states', 'w')
	try:
		data = urllib.urlopen("http://thermostat.pavoukovo.cz/states").read().decode() # Otevrit soubor
		if data.find("html") == -1:
			states_file.write(data)
			retry = 0
			debug_print("DEBUG: HTTP states read ok")
		else:
			retry += 1
			debug_print("DEBUG: " + time.strftime("%H:%M:%S") + " HTTP states read failed, remote file not found (retry: " + str(retry) + ")")
			if retry >= 5:
				for i in range(0, 4):
					states_file.write("%s\n" % "0") # Kdyz se nepodari otevrit soubor, zapsat 0
	except:
		retry += 1
		debug_print("DEBUG: " + time.strftime("%H:%M:%S") + " HTTP states read failed (retry: " + str(retry) + ")")
		if retry >= 5:
			for i in range(0, 4):
				states_file.write("%s\n" % "0") # Kdyz se nepodari otevrit soubor, zapsat 0
	states_file.close()
	time.sleep(5)