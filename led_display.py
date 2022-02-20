#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time, os.path, itertools
import RPi.GPIO as IO

debug = False

path_to_files = "/tmp/"

# Set output GPIO
data_pin = 17
latch_pin = 27
clock_pin = 22

IO.setwarnings(False)
IO.setmode(IO.BCM)
IO.setup(data_pin,IO.OUT)
IO.setup(latch_pin,IO.OUT)
IO.setup(clock_pin,IO.OUT)

# Function for printing debug output
def debug_print(text):
	if debug:
		print(text)

numbers = [
[1, 1, 0, 0, 0, 0, 0, 0], # 0
[1, 1, 1, 1, 1, 0, 0, 1], # 1
[1, 0, 1, 0, 0, 1, 0, 0], # 2
[1, 0, 1, 1, 0, 0, 0, 0], # 3
[1, 0, 0, 1, 1, 0, 0, 1], # 4
[1, 0, 0, 1, 0, 0, 1, 0], # 5
[1, 0, 0, 0, 0, 0, 1, 0], # 6
[1, 1, 1, 1, 1, 0, 0, 0], # 7
[1, 0, 0, 0, 0, 0, 0, 0], # 8
[1, 0, 0, 1, 0, 0, 0, 0], # 9
[1, 1, 1, 1, 1, 1, 1, 1] # Literally nothing
]

temps = [None] * 3

while 1:
	# Open temperatures file
	try:
		with open(path_to_files + 'meteo', 'r') as temps_file:
			temps_lines = temps_file.read().splitlines()
			for i in range(3):
				temps[i] = temps_lines[i]
			temps_file.close()
			read_fail = 0
			debug_print("DEBUG: Read temps file ok")
	except: # Write --- (error) if file couldn't be opened
		for i in range(3):
			temps[i] = u"---"
		read_fail = 1
		debug_print("DEBUG: Read temps file failed")

	# Do one specific temperature only, can be changed later
	if read_fail:
		for i in range(24):
			debug_print("DEBUG: No values read, printing ---")
			data_out = [1] * 24
			data_out[1] = 0
			data_out[9] = 0
			data_out[16] = 0
			data_out[17] = 0
	else:
		for i in range(3):
			# Clear data_out variable
			data_out = []
			# If temperature reading was ok, prepare 24 bits for shift registers
			if temps[i] != u"---":
				temp = float(temps[i])
				debug_print("DEBUG: Temperature number " + str(i) + " ok, " + str(temp))
				for byte in range(3):
					# Put first number (tens) in data_out
					if byte == 0:
						if abs(temp) < 10:
							data_out.append(numbers[10])
						else:
							data_out.append(numbers[int(abs(temp) / 10)])
						debug_print("DEBUG: Data after first byte " + str(data_out))
					# Put second number (ones) in data_out
					elif byte == 1:
						data_out.append(numbers[int(abs(temp) % 10)])
						debug_print("DEBUG: Data after second byte " + str(data_out))
					# Put third number (tenths) in data_out, add decimal point and figure out negative sign
					elif byte == 2:
						data_out.append(numbers[int(round(abs(temp) % 1, 1) * 10)])
#						debug_print("DEBUG: Temporary, rounding errors? " + str(abs(temp) % 1) + " gets rounded to " + str(int(round(abs(temp) % 1, 1) * 10)))
						debug_print("DEBUG: Data after third byte " + str(data_out))
						data_out = list(itertools.chain(*data_out))
						debug_print("DEBUG: Data before finishing " + str(data_out))
						# Add decimal point
						data_out[8] = 0
						# Figure out poistion of negative sign
						if temp < 0:
							# If temperature is -9.9 to 0, negative sign must be on the second digit (from four total), ie. " -9.9"
							if abs(temp) < 10:
								data_out[1] = 0
							# If temperature is lower than -10, negative sign muse be on the first digit, ie. "-10.0"
							else:
								data_out[16] = 0
			# If there was an error, print out --- on display
			else:
				debug_print("DEBUG: Bad reading, printing ---")
				data_out = [1] * 24
				data_out[1] = 0
				data_out[9] = 0
				data_out[17] = 0
			debug_print("DEBUG: Data before shifting out " + str(data_out))

			# Shift out to LED display
			IO.output(data_pin,IO.LOW)
			IO.output(clock_pin,IO.LOW)
			IO.output(latch_pin,IO.LOW)
			IO.output(clock_pin,IO.HIGH)
			for bit in range(24):
				IO.output(clock_pin,IO.LOW)
				IO.output(data_pin,data_out[bit])
				IO.output(clock_pin,IO.HIGH)
			IO.output(clock_pin,IO.LOW)
			IO.output(latch_pin,IO.HIGH)
			IO.output(clock_pin,IO.HIGH)

			time.sleep(2)

#	for n in range(10):
#		for i in range(16):
#			IO.output(clock_pin,IO.LOW)
#			IO.output(data_pin,1)
#			IO.output(clock_pin,IO.HIGH)
#		debug_print("DEBUG: Number " + str(n))
#		if debug:
#			time.sleep(1)
#		else:
#			time.sleep(5)
