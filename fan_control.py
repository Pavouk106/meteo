#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess, time, os.path
import RPi.GPIO as IO

debug = False

path_to_files = "/tmp/"

# Set output GPIO
fan_pin = 19

IO.setwarnings(False)
IO.setmode(IO.BCM)
IO.setup(fan_pin,IO.OUT)
fan_pwm = IO.PWM(fan_pin, 50)
fan_pwm.start(0)

#lo_out = 5
#mid_out = 6
#hi_out = 13
#IO.setup(lo_out,IO.OUT)
#IO.setup(mid_out,IO.OUT)
#IO.setup(hi_out,IO.OUT)
#IO.output(lo_out,IO.LOW)
#IO.output(mid_out,IO.LOW)
#IO.output(hi_out,IO.LOW)

fan_values = [None] * 2
speed = 0

# Function for printing debug output
def debug_print(text):
	if debug:
		print(text)

while 1:
	# Read SoC temp from external scipt, set fan PWM based on temp
	try:
		# for Python 3.6
		#temp = float(subprocess.run(["/home/pi/software/pool/rpi_temp"], stdout=subprocess.PIPE).stdout.decode("utf-8").strip("\n"))
		# for Python 3.7+
		temp = float(subprocess.run(["/home/pi/software/meteo/rpi_temp"], capture_output=True).stdout.decode("utf-8").strip("\n"))
		if temp < 35 and temp > 33 and speed > 0:
			speed = int(20*(temp - 30)/5)
		else:
			# Set PWM to 0% for temperature <35C, 20% for temperature 35C ... 100% for temperature 55C
			speed = int(20*(temp - 30)/5)
			if speed < 20:
				speed = 0
			elif speed > 100:
				speed = 100
		# Set PWM output
		fan_pwm.ChangeDutyCycle(speed)
		# Write values to list (to write to file)
		fan_values[0] = temp
		fan_values[1] = speed
		# Debug
		debug_print("Temp: " + str(temp))
		debug_print("Speed: " + str(speed))
	except:
		debug_print("Read temp failed")
		pass

	# Write temp and PWM speed to file
	try:
		fan_file = open(path_to_files + 'fan', 'w')
		for i in range(0, 2):
			fan_file.write("%s\n" % fan_values[i])
		fan_file.close()
	except:
		pass

	# Sleep before repeating
	if debug:
		time.sleep(1)
	else:
		time.sleep(10)
