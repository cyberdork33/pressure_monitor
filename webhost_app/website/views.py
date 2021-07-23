import requests, json
from datetime import datetime, timedelta
from collections import namedtuple

from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import db
from .models import MonitorReading

## Define a named tuple to hold data for display on page
DisplayData = namedtuple("DisplayData", "printable_pressure on_now reading")

## GLOBALS
DATA_SOURCE_URL = 'http://raspberrypi/json'
READING_DELTA = 15# minutes
MIN_PRESSURE_FOR_ON = 30#psi

views = Blueprint('views', __name__)

##------------------------------------------------------------------------------
## ROUTES
@views.route('/')
def home():
	# Get data common to home and admin page
	page_data = common_page_data()

	# Plot stuff
	#https://stackoverflow.com/questions/37683147/getting-script-and-div-tags-from-plotly-using-python

	date_data = [reading.datetime for reading in MonitorReading.query.all()]
	pressure_data = [reading.pressure for reading in MonitorReading.query.all()]

	fig = go.Figure()
	fig.update_layout(height=500)
	# fig.update_layout(yaxis={"title":"Pressure [psi]", "fixedrange":True})
	fig.update_layout(yaxis=dict(	title="Pressure [psi]",
																fixedrange=True),
										xaxis=dict(	tickangle = 90,
																dtick=60*60*2*1000))

	# fig = make_subplots(rows=2, cols=1)

	fig.add_scatter(x=date_data, y=pressure_data,
									# row=1, col=1,
									name="Measured Pressure",
									mode="lines+markers",
									line_color="#17B897",
									hovertemplate="Time: %{x|%H:%M} UTC<br>"
																"Pressure: %{y:.2f} psi"
																"<extra></extra>",
									)
	fig.add_scatter(x=date_data, y=[MIN_PRESSURE_FOR_ON]*100,
									# row=1, col=1,
									name="Minimum Pressure Needed")


	fig.update_layout(legend=dict(
			yanchor="top",
			y=1.2,
			xanchor="left",
			x=0.01
	))

	plot_elements = pio.to_html(fig,
															include_plotlyjs=False,
															full_html=False)

	return render_template("home.html.j2",
													user=current_user,
													on_now=page_data.on_now,
													current_pressure=page_data.printable_pressure,
													reading=page_data.reading,
													plotData=plot_elements)

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

##------------------------------------------------------------------------------
## Acquire data from the remote system via web request
def get_new_reading(address: str) -> MonitorReading:
	r = requests.get(address)
	theJSON = r.json()
	print(f"Time String from JSON: {theJSON[0]}")
	without_fracional_seconds = theJSON[0].split('.')[0]
	datetime_object = datetime.strptime(without_fracional_seconds, '%Y-%m-%d %H:%M:%S')
	print(f"Time from datetime: {datetime_object}")
	reading = MonitorReading(datetime=theJSON[0],
										rawvalue=theJSON[1],
										voltage=theJSON[2],
										pressure=theJSON[3])
	return reading

##------------------------------------------------------------------------------
## Acquire data from the remote system via web request and record in DB
def record_new_reading(address: str) -> MonitorReading:
	r = get_new_reading(address)
	# Create object and commit to DB
	new_reading = MonitorReading(	rawvalue=r.rawvalue,
																voltage=r.voltage,
																pressure=r.pressure)
	db.session.add(new_reading)
	db.session.commit()
	return new_reading

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
		r = MonitorReading(datetime=last_reading.datetime,
								rawvalue=last_reading.rawvalue,
								voltage=last_reading.voltage,
								pressure=last_reading.pressure)
	else:
		# get current pressure from external system
		print("Getting a new reading...")
		r = record_new_reading(DATA_SOURCE_URL)

	# Prepare everything to go into the page templates.
	printable_pressure = f"{r.pressure:5.2f}"
	# Determine if water is "on"
	on_now = False
	if r.pressure > MIN_PRESSURE_FOR_ON:
		on_now = True
	# Package everything up
	data = DisplayData(	printable_pressure=printable_pressure,
											on_now=on_now,
											reading=r)
	return data
