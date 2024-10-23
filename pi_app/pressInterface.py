import board, busio # Modules to interface with I2C
import datetime, json # Modules for handling readings
from collections import namedtuple

# Modules to interface with the ADC
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

##------------------------------------------------------------------------------
## Global Vars
I2C_ADDRESS = 0x48 # 0x48 is the default
CAL_READINGS = 10

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
Reading = namedtuple("Reading", "datetime rawvalue voltage")

##------------------------------------------------------------------------------
## Every reading taken should report
##		1. When it was taken
##		2. Raw ADC value
##		2. The voltage read
def get_reading() -> Reading:
	try:
		# read raw data from from ADC
		raw_value = channel0.value
		voltage = channel0.voltage

		# Get the current UTC date and time, and include timezone info.
		ct = datetime.datetime.now(datetime.timezone.utc)

		this_reading = Reading(datetime=ct.strftime('%Y-%m-%d %H:%M:%S %Z'),
													 rawvalue=raw_value,
													 voltage=voltage)

		return this_reading
	except:
		print("There was an error while taking the reading.")
		return False

##------------------------------------------------------------------------------
## Returns reading data as a JSON string
def reading_json() -> str:
	r = get_reading()
	return json.dumps(r)

def reading_string() -> str:
	r = get_reading()
	result = f"{r.datetime:25}, {r.rawvalue:5}, {r.voltage:7.5f}"
	return result

def reading_calibration() -> str:
	print("Timestamp, Raw Value, Voltage [V]")
	for i in range(CAL_READINGS):
		r = get_reading()
		print(f"{r.datetime:25}{r.rawvalue:5} {r.voltage:7.5f}")


if __name__ == "__main__":
	# print("Timestamp, Raw Value, Voltage [V]")
	# print(reading_string())
	# print(reading_json())
	reading_calibration()


# Convert the read voltage to pressure
# This would be the equation to change due to any calibration
# P = ((V_read / Vcc) - 0.1) * 125
# pressure = ((voltage / SUPPLY_VOLTAGE) - 0.1) * 125
