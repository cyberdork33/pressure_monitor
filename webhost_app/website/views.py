from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from . import monitor
import json
import plotly
import plotly.express as px

views = Blueprint('views', __name__)

@views.route('/')
def home():
	# Read current pressure from sensor
	r = monitor.take_reading()
	# Make it pretty
	printable_pressure = "{}".format('{:>5.2f}'.format(r.pressure))
	# Determine if water is "on"
	on_now = False
	if r.pressure > 30:
		on_now = True

	return render_template("home.html",
													user=current_user,
													on_now=on_now,
													current_pressure=printable_pressure,
													graphJSON=create_plot_data())

# https://towardsdatascience.com/an-interactive-web-dashboard-with-plotly-and-flask-c365cdec5e3f
@views.route('/chart1')
def chart1():
	return render_template('chart1.html', graphJSON=create_plot_data())

@views.route('/about')
def about():
	return render_template("about.html",
													user=current_user)

@views.route('/admin', methods=['GET','POST'])
@login_required
def admin():

	r = monitor.take_reading()
	printable_pressure = "{}".format('{:>5.2f}'.format(r.pressure))
	on_now = False
	if r.pressure > 30:
		on_now = True

	if request.method == 'POST':
		button_clicked = request.form['submit_button']
		if button_clicked == 'forceReading':
			# Call the take-reading method
			r = monitor.take_reading()
			print(r)
			printable_pressure = "{}".format('{:>5.2f}'.format(r.pressure))
			flash(f"A reading was taken. The pressure is {printable_pressure} psi.", category='success')
		elif button_clicked == 'calibrateReading':
			# Call the calibrate-reading method
			flash('A calibration reading was taken.', category='success')
		else:
			flash('Unsure what reading to take.', category='error')

	return render_template("admin.html",
													user=current_user,
													on_now=on_now,
													current_pressure=printable_pressure)

def create_plot_data():
	fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
	graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	return graphJSON