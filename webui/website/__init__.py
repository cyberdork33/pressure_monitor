from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "site_db.sqlite3"

def create_app():
	app = Flask(__name__)
	app.config['SECRET_KEY'] = '78efdeeb9a6135ae65acf8a797ede88d775047cb36a7c80c9f17f3e3'
	app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
	# Suppress Deprecation Warning
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	db.init_app(app)

	from .views import views
	from .auth import auth

	app.register_blueprint(views, url_prefix='/')
	app.register_blueprint(auth, url_prefix='/')

	from .models import User, CalibrationReading, MonitorReading
	create_database(app)

	return app

def create_database(app):
	if not path.exists('website/' + DB_NAME):
		db.create_all(app=app)
		print("Created Database!")