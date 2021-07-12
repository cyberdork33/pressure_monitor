from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home():
  return render_template("home.html")

@views.route('/admin')
def admin():
  return render_template("admin.html", methods=['GET', 'POST'])