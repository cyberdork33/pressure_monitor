# Script to take a reading from the ADS1115
# cyberdork33 <cyberdork33@gmail.com>

import time

# Import the ADS1x15 module.
#from ADS1x15 import ADS1015
from ADS1x15 import ADS1115
# import ADS1x15

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
CHANNEL = 0
DATA_RATE = 128
READINGS = 10

## MAIN CODE
print('Reading ADS1x15 values.')

for i in range(READINGS):
	# array to hold read values
	# Values read will be a 16-bit signed integer value
	# values = [0]

	# Read the specified ADC channel using the previously set gain value.
	values = adc.read_adc(CHANNEL, gain=GAIN)
	# Note you can also pass in an optional data_rate parameter that controls
	# the ADC conversion time (in samples/second). See datasheet Table 9 config 
	# register DR bit values.
	#values = adc.read_adc(CHANNEL, gain=GAIN, data_rate=DATA_RATE)

	# Print the ADC values.
	print(' {0:>6} '.format(values))
	# Pause for half a second.
	time.sleep(0.5)
