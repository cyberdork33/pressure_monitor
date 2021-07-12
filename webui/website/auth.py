from flask import Blueprint, request, flash
from flask.templating import render_template

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
  data = request.form
  print(data)
  return render_template("login.html")

@auth.route('/logout')
def logout():
  return "<p>Logout</p>"

@auth.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    email = request.form.get('email')
    name = request.form.get('name')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    # Can do some validation on on these if desired
    if len(password1) < 8:
      flash('Passwords must be at least 8 characters!', category='error')
    elif password1 != password2:
      flash('Passwords did not match!', category='error')
    else:
      # add user to database
      flash('Creating Account.', category='success')

  return render_template('register.html')