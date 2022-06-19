#!/bin/python3
# -*- coding: utf-8 -*-

import time, os.path
import RPi_I2C_driver

debug = False

path_to_files = "/tmp/"


mylcd = RPi_I2C_driver.lcd()
mylcd.lcd_clear()

temps = [None] * 3

# Function for printing debug output
def debug_print(text):
	if debug:
		print(text)

while 1:
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
	if read_fail:
		mylcd.lcd_clear()
		mylcd.lcd_display_string("Chyba cteni", 1)
	else:
		if temps[0] != None:
			if temps[0] != u"---" and temps[1]!= u"---":
				if float(temps[1]) - float(temps[0]) >= 0:
					mylcd.lcd_display_string("Voda: " + str(round(float(temps[0]), 1)) + "+" + str(round(float(temps[1]) - float(temps[0]), 1)) + u"\337" + "C", 1)
				else:
					mylcd.lcd_display_string("Voda: " + str(round(float(temps[0]), 1)) + "-" + str(abs(round(float(temps[1]) - float(temps[0]), 1))) + u"\337" + "C", 1)
			else:
				mylcd.lcd_display_string_pos("       ", 1, 9)
				mylcd.lcd_display_string("Voda: ---", 1)
			if temps[2] != u"---":
				mylcd.lcd_display_string("Vzduch: " + str(round(float(temps[2]), 1)) + u"\337" + "C ", 2)
			else:
				mylcd.lcd_display_string_pos("     ", 2, 11)
				mylcd.lcd_display_string("Vzduch: ---", 2)

	time.sleep(5)
