from datetime import datetime, timedelta
from dateutil import tz
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
DATA_SOURCE_URL = 'http://pressure-pi/json'
READING_DELTA = 15# minutes
MIN_PRESSURE_FOR_ON = 30#psi
# TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S %Z'
TIMESTAMP_FORMAT = '%b %d, %Y %-I:%M:%S %p %Z'

views = Blueprint('views', __name__)

##------------------------------------------------------------------------------
## ROUTES
@views.route('/')
def home():
  # Get data common to home and admin page
  page_data = common_page_data()

  ## Query database for data to plot and generate the plot
  # First get the reading dates
  # TODO od these queries to only grab the last week's worth of data
  date_data = [reading.datetime for reading in MonitorReading.query.all()]

  # Timestamps from database are in UTC.
  # make sure dates are timezone aware
  dates = []

  for date in date_data:
    dates.append(date.replace(tzinfo=tz.tzutc()))
  date_data = dates

  # Format last timestamp for display
  current_timestamp = utc2local(page_data.reading.datetime)
  printable_timestamp = current_timestamp.strftime(TIMESTAMP_FORMAT)
  # print(f"Formatted Current Timestamp: {printable_timestamp}")

  # Now get the pressures
  pressure_data = [reading.pressure for reading in MonitorReading.query.all()]

  # generate the plots with this data
  plot_elements = generate_plots(date_data, pressure_data)

  return render_template("home.html.j2",
                         user=current_user,
                         on_now=page_data.on_now,
                         current_pressure=page_data.printable_pressure,
                         current_timestamp=printable_timestamp,
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
      print('Forcing a reading.')
      record_new_reading(DATA_SOURCE_URL)
      # Notify the user that the reading was taken
      flash(f"A reading was taken. The pressure is "
            f"{page_data.printable_pressure} psi.", category='success')
            #TODO This uses the pressure that was previously passed in
            # instead of the newly read presssure. Need to fix this.
    # ----- Handle the "Calibration Reading" Button
    elif button_clicked == 'calibrateReading':
      # Call the calibrate-reading method
      flash('A calibration reading was taken.', category='success')
    elif button_clicked == 'pruneDatabase':
      cutoff_date = datetime.strptime(request.form['pruneBefore'], '%Y-%m-%d')
      MonitorReading.query.filter(MonitorReading.datetime < cutoff_date).delete()
      db.session.commit()
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
  now = datetime.utcnow().replace(tzinfo=tz.tzutc())

  # TODO: Improve later.
  # The following is very duplicative. It can probably be done
  # better. I force the database data into the structure to make
  # sure the timestamp is treated as a datetime object. It works for now.

  if not last_reading:
    # There was no reading. Force one.
    last_reading = record_new_reading(DATA_SOURCE_URL)

  # Put the last reading into the Structure
  r = MonitorReading(	datetime=last_reading.datetime,
                      rawvalue=last_reading.rawvalue,
                      voltage=last_reading.voltage,
                      pressure=last_reading.pressure)

  # Was the reading recent?
  if r.datetime.replace(tzinfo=tz.tzutc()) < (now - timedelta(minutes=READING_DELTA)):
    # Take a new reading if not.
    last_reading = record_new_reading(DATA_SOURCE_URL)

  # Put the last reading into the Structure
  r = MonitorReading(	datetime=last_reading.datetime,
                      rawvalue=last_reading.rawvalue,
                      voltage=last_reading.voltage,
                      pressure=last_reading.pressure)

  ## Prepare everything to go into the page templates.
  # Format the pressure value
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
## standalone though and will require that the using page include the plotly js
## script to display.

def generate_plots(dates, pressures) -> str:

# Reference
# https://plotly.com/python/time-series/

# TODO Explore possiblity of making the set ticks dynamic based on zoom level.
# For example, when zoomed in close, the labels should be every hour instead of 4.
# fig.update_layout(
#     xaxis_tickformatstops = [
#         dict(dtickrange=[None, 1000], value="%H:%M:%S.%L ms"),
#         dict(dtickrange=[1000, 60000], value="%H:%M:%S s"),
#         dict(dtickrange=[60000, 3600000], value="%H:%M m"),
#         dict(dtickrange=[3600000, 86400000], value="%H:%M h"),
#         dict(dtickrange=[86400000, 604800000], value="%e. %b d"),
#         dict(dtickrange=[604800000, "M1"], value="%e. %b w"),
#         dict(dtickrange=["M1", "M12"], value="%b '%y M"),
#         dict(dtickrange=["M12", None], value="%Y Y")
#     ]
# )

  ## Setup data
  # Convert objects to local timezone
  dates = list(map(utc2local, dates))
  # get the current time and localize it
  now = utc2local(datetime.utcnow().replace(tzinfo=tz.tzutc()))

  # initialize the string to put in the page
  plot_elements = ''

  ## PLOT1: For the 1st plot, plot only the last 24 hours
  # Instead of filtering, I could just set the plot range:
  # https://plotly.com/python/time-series/#time-series-plot-with-custom-date-range
  cutoff_date = now - timedelta(hours=24)

  # Filter the data
  new_list = [[j,i] for i, j in zip(pressures, dates) if j > cutoff_date]
  if len(new_list) > 0:
    filtered_dates, filtered_pressures = list(zip(*new_list))
  else:
    # Don't fail if there isn't data from the filtered time period.
    # This shouldn't happen now since I built protection into the
    # common page data function.
    filtered_dates, filtered_pressures = [now], [0]

  # setup the figure
  fig = go.Figure()
  fig.update_layout(height=500,
                    title="Data for the last 24 hrs.")
  fig.update_layout(yaxis=dict(title="Pressure [psi]",
                               fixedrange=True),
                    xaxis=dict(tickangle = 80,
                               dtick=60*60*4*1000)) # Time in milliseconds
  fig.update_xaxes(tickformat="%-I:%M %p\n%m/%d/%Y")

  fig.add_scatter(x=filtered_dates, y=filtered_pressures,
                  name="Measured Pressure",
                  mode="lines+markers",
                  # mode="markers",
                  line_color="#17B897",
                  hovertemplate="Time: %{x|%I:%M %p}<br>"
                                "Pressure: %{y:.2f} psi"
                                "<extra></extra>",
                  )
  fig.add_scatter(x=filtered_dates, y=[MIN_PRESSURE_FOR_ON]*len(filtered_dates),
                  name="Minimum Pressure Needed",
                  mode="lines")

  fig.update_layout(legend=dict(
                            yanchor="top",
                            y=1.2,
                            xanchor="left",
                            x=0.7))

  plot_elements = plot_elements+pio.to_html(fig,
                              include_plotlyjs=False,
                              full_html=False)

  ## PLOT2: For the 2nd plot, show data for the last week
  cutoff_date = now - timedelta(weeks=1)

  new_list = [[j,i] for i, j in zip(pressures, dates) if j > cutoff_date]
  if len(new_list) > 0:
    filtered_dates, filtered_pressures = list(zip(*new_list))
  else:
    # Don't fail if there isn't data from the filtered time period.
    # This shouldn't happen now since I built protection into the
    # common page data function.
    filtered_dates, filtered_pressures = [now], [0]

  fig = go.Figure()
  fig.update_layout(height=500, title="Data for the last week.")
  fig.update_layout(yaxis=dict(title="Pressure [psi]",
                              fixedrange=True),
                    xaxis=dict(tickangle = 80,
                              dtick=24*60*60*1000)) # Time in milliseconds
  fig.update_xaxes(tickformat="%b %d, %Y")

  fig.add_scatter(x=filtered_dates, y=filtered_pressures,
                  name="Measured Pressure",
                  mode="lines+markers",
                  # mode="markers",
                  line_color="#17B897",
                  hovertemplate="%{x| %m/%d/%Y %I:%M %p}<br>"
                                "Pressure: %{y:.2f} psi"
                                "<extra></extra>",
                  )
  fig.add_scatter(x=filtered_dates, y=[MIN_PRESSURE_FOR_ON]*len(filtered_dates),
                  name="Minimum Pressure Needed",
                  mode="lines")

  fig.update_layout(legend=dict(
                            yanchor="top",
                            y=1.2,
                            xanchor="left",
                            x=0.7))

  plot_elements = plot_elements+pio.to_html(fig,
                              include_plotlyjs=False,
                              full_html=False)

  ## PLOT3: For the 3rd show the last month, but only pick the peak from each day...?

  return plot_elements

# This depends on the dateutil library
def utc2local(utc:datetime) -> datetime:

  # Force readings to be in UTC
  current_timestamp = utc.replace(tzinfo=tz.tzutc())
  # now convert to local
  # current_timestamp = current_timestamp.astimezone(tz.tzlocal())
  # The above is reliable since the server's local time is often UTC...
  # Force it to the timezone we want.
  to_zone = tz.gettz('America/New_York')
  current_timestamp = current_timestamp.astimezone(to_zone)
  return current_timestamp
