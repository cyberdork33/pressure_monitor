# Script to constantly monitor the pressure
# cyberdork33 <cyberdork33@gmail.com>

import time
import datetime
import csv

# Import the ADS1x15 module.
from ADS1x15 import ADS1115

# Create an ADS1115 ADC (16-bit) instance.
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
TIME_BETWEEN_READINGS = 0.5
VCC = 3.3

## MAIN CODE

print('Ctrl+C to quit')
print("Timestamp", "Read Value")

while True:

	# Get the Current Timestamp
	ct = datetime.datetime.now()
	
	# Read the specified ADC channel using the previously set gain value.
	# Values read will be a 16-bit signed integer value
	rawvalue = adc.read_adc(CHANNEL, gain=GAIN)

	## Convert the raw value to engineering units according to calibration
	# Frist convert to Voltage
	voltage = (rawvalue - 31.2871626669657) / 7976.04146337744
	# Then to psi
	#pressure = (voltage - 0.5) / 0.04
	pressure = ((voltage / VCC) - 0.1) * 125

	# Print the ADC values.
	print(ct, "{0:8.2f} ".format(pressure))

	# Pause for half a second between each reading
	time.sleep(TIME_BETWEEN_READINGS)
