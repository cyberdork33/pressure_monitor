# Script to take a reading from the ADS1115
# cyberdork33 <cyberdork33@gmail.com>

import time
import datetime
import csv

# Import the ADS1x15 module.
from ADS1x15 import ADS1115

# Create an ADS1115 ADC (16-bit) instance.
# adc = ADS1x15.ADS1115()
adc = ADS1115()

## GLOBAL SETTINGS

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 1
CHANNEL = 0 # which channel to read from
DATA_RATE = 128 # what data rate to use. 128 is default.
READINGS = 10 # how many readings to take.

## MAIN CODE

with open('readings.csv', 'w', newline='', encoding='utf-8') as file:
	writer = csv.writer(file)
	writer.writerow(["Read Count", "Timestamp", "Voltage [V]", "Read Value"])

	while True:
		# Prompt for input voltage
		print('Ctrl+C to quit')
		print('What Voltage Level? >')
		voltage = input()

		for i in range(READINGS):

			# Get the Current Timestamp
			ct = datetime.datetime.now()
			
			# Read the specified ADC channel using the previously set gain value.
			# Values read will be a 16-bit signed integer value
			value = adc.read_adc(CHANNEL, gain=GAIN)
			
			# Print the ADC values.
			print(' {0:>6} '.format(value))

			# Write the read values.
			writer.writerow([i, ct, voltage, '{0:>6} '.format(value)])

			# Pause for half a second between each reading
			time.sleep(0.5)
