from flask import Flask, render_template, request
from os import path
from dateutil import tz, parser
import monitor

# General App Setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'I7JYZmBVX610l15tkv5Ldc7Vnak347auzeXm8tECJS4'

@app.route('/')
def home():
	# Read current pressure from sensor
	r = monitor.take_reading()

	# Make it pretty
	printable_pressure = f"{r.pressure:5.2f}"

	# get the timestamp from the reading include tz info
	utc = parser.parse(r.datetime)

	# Convert the object to the local timezone
	# local = utc.astimezone(tz.gettz('America/New_York'))
	local = utc.astimezone(tz.tzlocal())

	# Format it back to a sting.
	printable_timestamp = local.strftime('%Y-%m-%d %H:%M:%S %Z')

	# Determine if water is "on"
	on_now = False
	if r.pressure > 30:
		on_now = True

	return render_template("home.html.j2",
													on_now=on_now,
													current_pressure=printable_pressure,
													printable_timestamp=printable_timestamp
												)

@app.route('/json')
def json():
	return monitor.reading_json()

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
