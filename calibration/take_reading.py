# Script to take a reading from the ADS1115
# cyberdork33 <cyberdork33@gmail.com>

import time
import datetime
import csv
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Global Vars
supply_voltage = 3.3# Volts
TIME_BETWEEN_READINGS = 0.5

# Create the I2C bus object
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c, address=0x48)

# Create single-ended input on channel 0
channel0 = AnalogIn(ads, ADS.P0)

## GLOBAL VARS
READINGS = 10 # how many readings to take.

## MAIN CODE
# Prompt for input voltage
print('Ctrl+C to quit')
print('What Pressure [psi]? >')
pressure = input()

with open(pressure+'.csv', 'w', newline='', encoding='utf-8') as file:
	writer = csv.writer(file)
	writer.writerow(["Timestamp", "Read Count", "Read Value", "Pressure [psi]", "Voltage [V]"])

	for i in range(READINGS):

		# Get the Current Timestamp
		ct = datetime.datetime.now()
		
		# Read the specified ADC channel using the previously set gain value.
		# Values read will be a 16-bit signed integer value
		
		read_value = channel0.value
		read_voltage = channel0.voltage
		
		# Print the ADC values.
		print(' {:>5} '.format(read_value))

		# Write the read values.
		writer.writerow([ ct, i, read_value, pressure, read_voltage ])

		# Pause between readings
		time.sleep(0.1)
