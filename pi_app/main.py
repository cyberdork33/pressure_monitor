from flask import Flask, render_template, request
from os import path
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
	# Determine if water is "on"
	on_now = False
	if r.pressure > 30:
		on_now = True

	return render_template("home.html.j2",
													on_now=on_now,
													current_pressure=printable_pressure,
													reading=r
												)

@app.route('/json')
def json():
	return monitor.reading_json()

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
