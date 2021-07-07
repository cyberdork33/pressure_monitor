# Script to constantly monitor the pressure
# cyberdork33 <cyberdork33@gmail.com>

import time
import datetime
import board
import busio
import csv
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

## Global Vars
DEBUG = True
supply_voltage = 3.3# Volts. This is the supply voltage to the Pressure Sensor.
TIME_BETWEEN_READINGS = 0.5#60*15# Seconds

## Setup interface with ADC

# Create the I2C bus object
i2c = busio.I2C(board.SCL, board.SDA)
# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c, address=0x48)
# Create single-ended input on channel 0
channel0 = AnalogIn(ads, ADS.P0)

## Setup recording of data
output_filename = 'monitor.csv'

# writer.writerow(["Timestamp", "Raw Value", "Voltage [V]", "Pressure [psi]"])
if DEBUG:
	print("Timestamp, Raw Value, Voltage [V], Pressure [psi]")

while True:
		
		# Print Current Reading
	with open('monitor.csv', mode='a', newline='', encoding='utf-8') as file:
		writer = csv.writer(file)
		ct = datetime.datetime.now()

		#pressure = (voltage - 0.5) / 0.04
		pressure = ((channel0.voltage / supply_voltage) - 0.1) * 125

		writer.writerow([ct.strftime('%x %X'), channel0.value, channel0.voltage, pressure ])
		if DEBUG:
			print( "{:%x %X}, {:>5}, {:>5.3f}, {:>5.2f}".format(ct, channel0.value, 
																										channel0.voltage, 
																										pressure))

	# Pause for half a second between each reading
	time.sleep(TIME_BETWEEN_READINGS)
