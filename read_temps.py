#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os.path, re, time
import RPi.GPIO as IO
IO.setwarnings(False)
IO.setmode(IO.BCM)

debug = False
log = True

path_to_files = '/tmp/'

dallas_address = [
"28-3c01a816c6cd", # bazen sani
"28-3c01a816e735", # bazen solar
"28-3c01a816b7d5" # 5cm
]

temps_values = [None] * len(dallas_address)

# Counter for hard fails - that is when sensors haven't produced a temperature for extended period of time and many attempts; this will trigger power cycle of sensors
hard_fails = 0

# Setup sensor power output
sensor_pwr_pin = 21
IO.setup(sensor_pwr_pin,IO.OUT)
IO.output(sensor_pwr_pin,IO.LOW)

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

while 1:
	# Read dallas temperature sensors
	for i in range(0, len(dallas_address)):
		fails = 0
		debug_print("Dallas: " + dallas_address[i]);
		# Check if we didn't have too many failed attempts to read temperature
		while fails < 5:
			try:
				temp_file = open('/sys/bus/w1/devices/' + dallas_address[i] + '/w1_slave', 'r')
				file_lines = temp_file.read().splitlines()
				crc = re.compile('crc=.. (.*)')
				crc_value = crc.search(file_lines[0])
				debug_print(crc_value.group(1))
				# Check if CRC is ok
				if crc_value.group(1) == "YES":
					temp = re.compile('t=(.*)')
					temp_value = temp.search(file_lines[1])
					debug_print(temp_value.group(1))
					# Check if we got right temperature; Dallas sometimes outputs 85000 or -127000, which are failed values
					if abs(int(temp_value.group(1))) < 85000:
						temps_values[i] = round(float(temp_value.group(1)) / 1000, 2)
						if i == 1:
							debug_print("Offsetting temperature from " + str(temps_values[i]) + " to " + str(temps_values[i] - 0.5))
							temps_values[i] = temps_values[i] - 0.5
						break
					# Temperature fail, wait and repeat
					else:
						debug_print("85 or -127 degrees registered")
						fails += 1
						time.sleep(0.5)
				# CRC fail, wait and repeat
				else:
					debug_print("CRC failed")
					fails += 1
					time.sleep(0.5)
				temp_file.close()
			# Can't open file, wait and repeat
			except:
					fails += 1
					time.sleep(0.5)
					debug_print('/sys/bus/w1/devices/' + dallas_address[i] + '/w1_slave Temp read failed')
					pass

		# If reading file failed or other error happened 5 times
		if fails >= 5:
			# Increment hard fail
			hard_fails += 1
			# 5 hard fails = 25 normal fails, something is worng -> we try power cycling
			if hard_fails >= 5:
				# Write "---" for temperature values
				temps_velues = [0] * len(dallas_address)
				temps_values = [u"---"] * len(dallas_address)
				debug_print("!!! Power cycled !!!")
				log_action("[read_temps.py] Power cycled")
				hard_fails = 0
				# Turn off power for sensors
				IO.output(sensor_pwr_pin,IO.HIGH)
				# Wait
				time.sleep(5)
				# Turn power back on
				IO.output(sensor_pwr_pin,IO.LOW)
				# Wait
				time.sleep(5)
		# Just for cleaner debug
		elif fails != 0 or hard_fails != 0:
			debug_print("Fails: " + str(fails))
			debug_print("Hard fails: " + str(hard_fails))
		debug_print("-----------------------")

	# Write dallas temperature sensors readings to file
	try:
		temps_file_json = open(path_to_files + 'meteo.json', 'w')
		temps_file_json.write('{ "Teplota bazénu": {"teplota": "%s"}, "Rozdíl teploty bazénu": {"teplota": "%s"}, "Vnější teplota (5cm)": {"teplota": "%s"} }' % (temps_values[0], round(temps_values[0]-temps_values[1], 3), temps_values[2]))
		temps_file_json.close()
		temps_file = open(path_to_files + 'meteo', 'w') # Predelat na rw kvuli timestamp
		for i in range(0, len(temps_values) + 1):
			# Predelat na timestamp (kdyz starsi nez pet minut, zapsat vadu) - nutno precist ze souboru
			if u"---" in temps_values:
				temps_values[i] = u"---"
			temps_file.write("%s\n" % temps_values[i])
		temps_file.close()
	except:
		pass
	time.sleep(5)
