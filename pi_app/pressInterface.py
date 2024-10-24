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
CAL_SLOPE = 0.00471823169 # Line Slope from calibration
CAL_INTERCEPT = -2.117998617 # Intercept from calibration

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
													voltage=voltage,
													pressure=getPressure(raw_value))

		return this_reading
	except:
		print("There was an error while taking the reading.")
		return False

def get_reading_ave(count:int) -> Reading:
	valuesTotal = 0
	voltagesTotal = 0
	ct = datetime.datetime.now(datetime.timezone.utc)
	for i in range(count):
		r = get_reading()
		valuesTotal += r.rawvalue
		voltagesTotal += r.voltage
	this_reading = Reading(datetime=ct.strftime('%Y-%m-%d %H:%M:%S %Z'),
												rawvalue=valuesTotal/count,
												voltage=voltagesTotal/count,
												pressure=getPressure(valuesTotal/count))
	return this_reading

##------------------------------------------------------------------------------
## Returns reading data as a JSON string
def reading_json() -> str:
	# r = get_reading()
	r = get_reading_ave(CAL_READINGS)
	return json.dumps(r)

##------------------------------------------------------------------------------
## Returns reading data as a printable string
def reading_string() -> str:
	r = get_reading()
	result = f"{r.datetime:25}, {r.rawvalue:5}, {r.voltage:7.5f}"
	return result

##------------------------------------------------------------------------------
## Returns several reading in a format that can be used for calibration
def reading_calibration() -> str:
	# print("Timestamp, Raw Value, Voltage [V]")
	result = ''
	for i in range(CAL_READINGS):
		r = get_reading()
		result += f"{r.datetime:25}{r.rawvalue:5} {r.voltage:7.5f}<br />\n"
	return result

##------------------------------------------------------------------------------
## The linear curve fit to convert the raw integer to pressure.
def getPressure(rawvalue) -> float:
	return CAL_SLOPE*rawvalue+CAL_INTERCEPT

if __name__ == "__main__":
	# print("Timestamp, Raw Value, Voltage [V]")
	# print(reading_string())
	# print(reading_json())
	# print(reading_calibration())
	print(get_reading_ave(CAL_READINGS))
