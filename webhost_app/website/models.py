from time import timezone
from flask_sqlalchemy.model import Model
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class MonitorReading(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	# This will add DateTime automatically when a record is added.
	datetime = db.Column(db.DateTime(timezone=True), default=func.now())
	rawvalue = db.Column(db.Integer)
	voltage = db.Column(db.Float)
	pressure = db.Column(db.Float)

class CalibrationReading(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	# This will add DateTime automatically when a record is added.
	datetime = db.Column(db.DateTime(timezone=True), default=func.now())
	rawvalue = db.Column(db.Integer)
	voltage = db.Column(db.Float)
	pressure = db.Column(db.Float)

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(150), unique=True)
	password = db.Column(db.String(150))
	name = db.Column(db.String(150))