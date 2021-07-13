from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/')
def home():
	return render_template("home.html", user=current_user)

@views.route('/about')
def about():
	return render_template("about.html", user=current_user)

@views.route('/admin', methods=['GET','POST'])
@login_required
def admin():
	if request.method == 'POST':
		button_clicked = request.form['submit_button']
		if button_clicked == 'forceReading':
			# Call the take-reading method
			flash('A reading was taken.', category='success')
		elif button_clicked == 'calibrateReading':
			# Call the calibrate-reading method
			flash('A calibration reading was taken.', category='success')
		else:
			flash('Unsure what reading to take.', category='error')

	return render_template("admin.html", user=current_user)