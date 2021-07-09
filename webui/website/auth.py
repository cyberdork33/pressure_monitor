from flask import Blueprint
from flask.templating import render_template

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
  # return "<p>Login</p>"
  return render_template("login.html", text="Testing",  user="Tim")

@auth.route('/logout')
def logout():
  return "<p>Logout</p>"

@auth.route('/register')
def register():
  return render_template('register.html')