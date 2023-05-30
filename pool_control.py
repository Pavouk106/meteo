#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, os.path
import RPi.GPIO as IO

debug = False
log = True

path_to_files = '/tmp/'

remote_state = 0

retry = 0

# Define pins to control outlets
bottom_out = 5
middle_out = 6
top_out = 13

# Initialize RPIO
IO.setwarnings(False)
IO.setmode(IO.BCM)

# Set pins + set to LOW (off)
IO.setup(bottom_out,IO.OUT)
IO.setup(middle_out,IO.OUT)
IO.setup(top_out,IO.OUT)
IO.output(bottom_out,IO.LOW)
IO.output(middle_out,IO.LOW)
IO.output(top_out,IO.LOW)

# Print debug function
def debug_print(text):
	if debug:
		print(text)

def log_action(text):
	if log:
		try:
			log_file=open(path_to_files + 'log', 'a')
			log_file.write(time.strftime("%d-%m-%Y, %H:%M:%S") + " " + text +  "\n")
			log_file.close()
		except:
			pass

def read_data():
	global remote_state, retry
	try:
		with open(path_to_files + 'states', 'r') as states_file:
			states_lines = states_file.read().splitlines()
			remote_state = int(states_lines[2])
			states_file.close()
			retry = 0
			debug_print("DEBUG: " + time.strftime("%H:%M:%S") + " Remote state: " + str(remote_state))
	except:
		retry += 1
		debug_print("DEBUG: " + time.strftime("%H:%M:%S") + " " + path_to_files + "states read failed (retry: " + str(retry) + ")")
		if retry >= 5: # If status wasn't read five times in a row, set it to 0 (off) 
			remote_state = 0
			time.sleep(1) # Add one second to (probably?) offset this script with others, as all have 5 seconds delay and may encounter each other when accessing files
			log_action("[pool_control.py] States file read failed 5 times")
		pass

while 1:
	read_data()

	debug_print("DEBUG: " + time.strftime("%H:%M:%S") + " Remote state: " + str(remote_state))

	# Set output depending on conditions like manual on/off, outside (freezing) temperature, temperature delta of pool, solar power (voltage on cell)
	if remote_state == 1:
		IO.output(top_out,IO.HIGH)
		debug_print("DEBUG: " + time.strftime("%H:%M:%S") + " Top output set to HIGH")
	elif remote_state == 0: # OR tempreture is not below 4 OR temp out and temp in delta is less than 0.5 (not heating) OR solar power is less than XY volts (sunshine is not powerful enough; output of solar cell)
		IO.output(top_out,IO.LOW)
		debug_print("DEBUG: " + time.strftime("%H:%M:%S") + " Top output set to LOW")

	time.sleep(5)
