from flask import Blueprint, request, flash, render_template, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

##------------------------------------------------------------------------------
## ROUTES
@auth.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    email = request.form.get('email')
    password = request.form.get('password')

    # Get all users in db that have this email address
    user = User.query.filter_by(email=email).first()
    if user:
      if check_password_hash(user.password, password):
        flash('Logged in successfully!', category='success')
        login_user(user, remember=True)
        return redirect(url_for('views.admin'))
      else:
        flash('Password was incorrect. Try Again.', category='error')
    else:
      flash('Email not found.', category='error')

  return render_template("login.html.j2", user=current_user)

@auth.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('views.home'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    email = request.form.get('email')
    name = request.form.get('name')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    # Get all users in db that have this email address
    user = User.query.filter_by(email=email).first()
    if user:
      flash('Email already exists.', category='error')
    elif len(password1) < 8:
      flash('Passwords must be at least 8 characters!', category='error')
    elif password1 != password2:
      flash('Passwords did not match!', category='error')
    else:
      # add user to database
      flash('Creating Account.', category='success')
      new_user = User(email=email,
                      name=name,
                      password=generate_password_hash(password1,
                                                      method='sha256'
                                                      )
                      )
      db.session.add(new_user)
      db.session.commit()
      return redirect(url_for('auth.login'))

  return render_template('register.html.j2', user=current_user)
