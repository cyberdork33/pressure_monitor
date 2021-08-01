import requests, json, time
from datetime import datetime, timedelta
from collections import namedtuple

from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import db
from .models import MonitorReading
from .data_fetch import record_new_reading

## Define a named tuple to hold data for display on page
DisplayData = namedtuple("DisplayData", "printable_pressure on_now reading")

## GLOBALS
DATA_SOURCE_URL = 'http://raspberrypi/json'
READING_DELTA = 15# minutes
MIN_PRESSURE_FOR_ON = 30#psi
RECORD_LIFETIME = 1 #weeks

views = Blueprint('views', __name__)

##------------------------------------------------------------------------------
## ROUTES
@views.route('/')
def home():
  # Get data common to home and admin page
  page_data = common_page_data()

  ## Query database for data to plot and generate the plot
  # First get the reading dates
  date_data = [reading.datetime for reading in MonitorReading.query.all()]

  # Convert all the times to the local timezone
  local_dates = []
  for date in date_data:
    local_dates.append(utc2local(date))
  date_data = local_dates

  # Now get the pressures
  pressure_data = [reading.pressure for reading in MonitorReading.query.all()]

  # generate the plots with this data
  plot_elements = generate_plots(date_data, pressure_data)

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
      flash(f"A reading was taken. The pressure is "
            f"{page_data.printable_pressure} psi.", category='success')
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
## Package common data elements needed for page display
## This will provide the last reading in the database if it was
## taken within the last 15 min. This will prevent hammering the
## Data Acquisition System. This won't be needed if I get the DAQ
## taking measurements regularly
def common_page_data() -> DisplayData:
  # Get last reading from DB
  sort_field = MonitorReading.datetime.desc()
  last_reading = MonitorReading.query.order_by(sort_field).first()
  # If the last reading was within the valid window,
  # just use what is in the database.
  r = MonitorReading(	datetime=last_reading.datetime,
                      rawvalue=last_reading.rawvalue,
                      voltage=last_reading.voltage,
                      pressure=last_reading.pressure)

  ## Prepare everything to go into the page templates.

  # Convert time zone to local
  r.datetime = utc2local(r.datetime)

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

##------------------------------------------------------------------------------
## This is the function that uses plotly to generate the plot(s). It outputs
## a string of HTML that can be inserted in the final page. This is not
## standalone though and will require that hte using page include the plotly js
## script to display.
def generate_plots(dates, pressures) -> str:
  fig = go.Figure()
  fig.update_layout(height=500)
  fig.update_layout(yaxis=dict(title="Pressure [psi]",
                               fixedrange=True),
                    xaxis=dict(tickangle = 90,
                               dtick=60*60*4*1000)) # Time in milliseconds

  fig.add_scatter(x=dates, y=pressures,
                  name="Measured Pressure",
                  mode="lines+markers",
                  line_color="#17B897",
                  hovertemplate="Time: %{x|%H:%M}<br>"
                                "Pressure: %{y:.2f} psi"
                                "<extra></extra>",
                  )
  fig.add_scatter(x=dates, y=[MIN_PRESSURE_FOR_ON]*len(dates),
                  name="Minimum Pressure Needed")

  fig.update_layout(legend=dict(
                            yanchor="top",
                            y=1.2,
                            xanchor="left",
                            x=0.01))

  plot_elements = pio.to_html(fig,
                              include_plotlyjs=False,
                              full_html=False)

  return plot_elements

# https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime
def utc2local(utc:datetime) -> datetime:
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
    return utc + offset
