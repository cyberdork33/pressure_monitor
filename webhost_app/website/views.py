from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
import requests, json
from datetime import datetime, timedelta
from collections import namedtuple
# import plotly
# import plotly.express as px
from . import db
from .models import MonitorReading

## Define a named tuple to hold data for a particular reading
Reading = namedtuple("Reading", "timestamp raw voltage pressure")
## Define a named tuple to hold data for display on page
DisplayData = namedtuple("DisplayData", "printable_pressure on_now reading")

## GLOBALS
DATA_SOURCE_URL = 'http://raspberrypi/json'
READING_DELTA = 15# minutes

views = Blueprint('views', __name__)

##------------------------------------------------------------------------------
## ROUTES
@views.route('/')
def home():
	# Get data common to home and admin page
	page_data = common_page_data()
	return render_template("home.html.j2",
													user=current_user,
													on_now=page_data.on_now,
													current_pressure=page_data.printable_pressure,
													reading=page_data.reading)

# # https://towardsdatascience.com/an-interactive-web-dashboard-with-plotly-and-flask-c365cdec5e3f
# @views.route('/chart1')
# def chart1():
# 	return render_template('chart1.html', graphJSON=create_plot_data())

@views.route('/about')
def about():
	# Just route to the page. Simple and plain.
	return render_template("about.html.j2",
													user=current_user)

@views.route('/admin', methods=['GET','POST'])
@login_required
def admin():
	# Get data common to home and admin page
	page_data = common_page_data()

	# If a POST request is made, handle the button clicked
	if request.method == 'POST':
		button_clicked = request.form['submit_button']
		# ----- Handle the "Force Reading" Button
		if button_clicked == 'forceReading':
			# Force a reading
			record_new_reading(DATA_SOURCE_URL)
			# Notify the user that the reading was taken
			flash(f"A reading was taken. The pressure is {page_data.printable_pressure} psi.", category='success')
		# ----- Handle the "Calibration Reading" Button
		elif button_clicked == 'calibrateReading':
			# Call the calibrate-reading method
			flash('A calibration reading was taken.', category='success')
		# ----- Unidentified Button...
		else:
			flash('Unsure what reading to take.', category='error')

	return render_template("admin.html.j2",
													user=current_user,
													on_now=page_data.on_now,
													current_pressure=page_data.printable_pressure,
													reading=page_data.reading)

# def create_plot_data():
# 	fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
# 	graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
# 	return graphJSON

##------------------------------------------------------------------------------
## Acquire data from the remote system via web request
def get_new_reading(address: str) -> Reading:
	r = requests.get(address)
	theJSON = r.json()
	reading = Reading(timestamp=theJSON[0],
										raw=theJSON[1],
										voltage=theJSON[2],
										pressure=theJSON[3])
	return reading

def record_new_reading(address: str) -> Reading:
	r = get_new_reading(address)
	# Create object and commit to DB
	new_reading = MonitorReading(	rawvalue=r.raw,
																voltage=r.voltage,
																pressure=r.pressure)
	db.session.add(new_reading)
	db.session.commit()
	return r

##------------------------------------------------------------------------------
## Package common data elements needed for page display
## This will provide the last reading in the database if it was
## taken within the last 15 min. This will prevent hammering the
## Data Acquisition System. This won't be needed if I get the DAQ
## taking measurements regularly
def common_page_data() -> DisplayData:
	# Check when last database point was
	last_reading = MonitorReading.query.order_by(MonitorReading.datetime.desc()).first()
	print(f'         Now: {datetime.utcnow()}')
	print(f'Last Reading: {last_reading.datetime}')

	# Determine how long ago the last reading was made
	time_passed = datetime.utcnow() - last_reading.datetime
	print(f"Last Reading was {time_passed.total_seconds()/60} minutes ago.")

	# If the last reading was within the valid window,
	# just use what is in the database.
	if time_passed <= timedelta(minutes=READING_DELTA):
		r = Reading(timestamp=last_reading.datetime,
								raw=last_reading.rawvalue,
								voltage=last_reading.voltage,
								pressure=last_reading.pressure)
	else:
		# get current pressure from external system
		print("Getting a new reading...")
		r = get_new_reading(DATA_SOURCE_URL)

	# Prepare everything to go into the page templates.
	printable_pressure = f"{r.pressure:5.2f}"
	# Determine if water is "on"
	on_now = False
	if r.pressure > 30:
		on_now = True
	# Package everything up
	data = DisplayData(	printable_pressure=printable_pressure,
											on_now=on_now,
											reading=r)
	return data
