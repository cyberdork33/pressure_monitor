# Script to constantly monitor the pressure
# cyberdork33 <cyberdork33@gmail.com>

import time, datetime
import board, busio
import csv
from collections import namedtuple
from os import path

# Modules to interface with the ADC
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

##------------------------------------------------------------------------------
## Global Vars
DEBUG = True
SUPPLY_VOLTAGE = 3.3# Volts. This is the supply voltage to the Pressure Sensor.
DEFAULT_FILENAME = 'monitor.csv'
DEFAULT_DELTAT = 60*15# Seconds
I2C_ADDRESS = 0x48 # 0x48 is the default

##------------------------------------------------------------------------------
## Setup interface with ADC
	# Create the I2C bus object
i2c = busio.I2C(board.SCL, board.SDA)
# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c, address=I2C_ADDRESS)
# Create single-ended input on channel 0
channel0 = AnalogIn(ads, ADS.P0)

##------------------------------------------------------------------------------
## Define a named tuple to hold data for a particular reading
Reading = namedtuple("Reading", "timestamp raw voltage pressure")

##------------------------------------------------------------------------------
## This function will create an output csv file
# It purposely does not check for prior existance,
# and as such, will overwrite an existing file with a new one.
def initialize_file(filename) -> bool:
	try:
		with open(filename, mode='w', newline='', encoding='utf-8') as file:
			writer = csv.writer(file)
			writer.writerow(["Timestamp", "Raw Value", "Voltage [V]", "Pressure [psi]"])
		return True
	except:
		print("Error creating file.")
		return False

##------------------------------------------------------------------------------
## Every reading taken should report
##		1. When it was taken
##		2. Raw ADC value
##		2. The voltage read
##		3. The calculated Pressure
def take_reading() -> Reading:
	try:
		# take actual reading from ADC
		raw_value = channel0.value
		voltage = channel0.voltage

		# Get Timestamp
		ct = datetime.datetime.now()

		# Convert the read voltage to pressure
		# This would be the equation to change due to any calibration
		# P = ((V_read / Vcc) - 0.1) * 125
		pressure = ((voltage / SUPPLY_VOLTAGE) - 0.1) * 125

		# Do not report negative pressure values
		if pressure < 0: pressure = 0

		this_reading = Reading(timestamp=ct,
													raw=raw_value,
													voltage=voltage,
													pressure=pressure)

		return this_reading
	except:
		print("There was an error while taking the reading.")
		return False

##------------------------------------------------------------------------------
## Writes a line to a csv file named filename
# We implement this here explicitly rather than just piping stdout
# so that we can append to the file over long periods of time and current
# output can be viewed simply by opening the file.
def write_reading(filename: str, reading: Reading) -> bool:
	try:
		# Check that file exists, if not, create it
		if path.exists(filename) == False:
			initialize_file(filename)

		# Write the passed reading data
		with open(filename, mode='a', newline='', encoding='utf-8') as file:
			writer = csv.writer(file)
			# Write this reading to the file
			writer.writerow([reading.timestamp,
											 reading.raw,
											 reading.voltage,
											 reading.pressure])
		return True
	except:
		print("Error writing file.")
		return False

def monitor(output_filename:str, time_delta:int):
	while True: # Loop forever

		# Take Reading
		r = take_reading()

		# Write Reading
		if r != False:
			write_reading(output_filename,r)
		if DEBUG:
			# If we choose, print values to stdout
			print("Timestamp, Raw Value, Voltage [V], Pressure [psi]")
			format_string = "{:%x %X}, {:>5}, {:>5.3f}, {:>5.2f}"
			print( format_string.format(r.timestamp,
																	r.raw,
																	r.voltage,
																	r.pressure))
		# Pause
		time.sleep(time_delta)
##------------------------------------------------------------------------------
## If we run this directly, default to the monitor function
if __name__ == '__main__':
	monitor(DEFAULT_FILENAME, DEFAULT_DELTAT)

# while True:
# 	# Open the Monitoring File to append a reading
# 	# Print Current Reading
# 	with open(output_filename, mode='a', newline='', encoding='utf-8') as file:
# 		writer = csv.writer(file)

# 		# get Tiemstamp
# 		ct = datetime.datetime.now()

# 		## Convert the read voltage to pressure
# 		#pressure = (voltage - 0.5) / 0.04
# 		pressure = ((channel0.voltage / supply_voltage) - 0.1) * 125
# 		# Do not report negative pressure values
# 		if pressure < 0: pressure = 0

# 		# Write this reading to the file
# 		writer.writerow([ct.strftime('%x %X'),
# 										 channel0.value,
# 										 channel0.voltage,
# 										 pressure ])

# 		# Print to stdout preferred
# 		if DEBUG:
# 			format_string = "{:%x %X}, {:>5}, {:>5.3f}, {:>5.2f}"
# 			print( format_string.format(ct,
# 																	channel0.value,
# 																	channel0.voltage,
# 																	pressure))

# 	# Pause for half a second between each reading
# 	time.sleep(DEFAULT_DELTAT)

