# This is the code that interfaces with the hardware to take readings
# cyberdork33 <cyberdork33@gmail.com>

import time, datetime
import board, busio
import csv, json
from collections import namedtuple
from os import path

# Modules to interface with the ADC
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

##------------------------------------------------------------------------------
## Global Vars
DEBUG = True
SUPPLY_VOLTAGE = 3.3# Volts. This is the supply voltage to the Pressure Sensor.
DEFAULT_FILENAME = 'monitor.csv' # This is the default location to write out data for constant monitoring.
DEFAULT_DELTAT = 60*15# Seconds
I2C_ADDRESS = 0x48 # 0x48 is the default
CAL_SLOPE = 0.004717125278 # Line Slope from calibration
CAL_INTERCEPT = -2.129835157 # Intercept from calibration

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
Reading = namedtuple("Reading", "datetime rawvalue voltage pressure")

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
		# This function gets the current UTC date and time. However, it does not include any timezone information.
		#ct = datetime.datetime.utcnow()
		# This method should get the current UTC date and time, and include timezone info.
		ct = datetime.datetime.now(datetime.timezone.utc)

		# Convert the read voltage to pressure
		# This is my calibration cuve data:
		pressure = CAL_SLOPE * raw_value + CAL_INTERCEPT

		# Do not report negative pressure values
		if pressure < 0: pressure = 0

		this_reading = Reading(datetime=ct.strftime('%Y-%m-%d %H:%M:%S %Z'),
													rawvalue=raw_value,
													voltage=voltage,
													pressure=pressure)

		return this_reading
	except:
		print("There was an error while taking the reading.")
		return False

##------------------------------------------------------------------------------
## Returns reading data as a JSON string
def reading_json() -> str:
	r = take_reading()
	return json.dumps(r)

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
			print(f"{r.timestamp:25}, {r.raw:5}, {r.voltage:5.3f}, {r.pressure:5.2f}")

		# Pause
		time.sleep(time_delta)

##------------------------------------------------------------------------------
## If we run this directly, default to the monitor function
if __name__ == '__main__':
	monitor(DEFAULT_FILENAME, DEFAULT_DELTAT)
