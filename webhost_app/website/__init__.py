from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database/site_db.sqlite3"
READING_DELTA = 15 #minutes

def create_app():

  # General App Setup
  app = Flask(__name__)
  app.config.from_pyfile('.env.py')
  app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #Suppress Deprecation Warning
  db.init_app(app)

  # Setup the site Blueprints
  from .views import views
  from .auth import auth

  app.register_blueprint(views, url_prefix='/')
  app.register_blueprint(auth, url_prefix='/')

  # Setup the site databse
  from .models import User, CalibrationReading, MonitorReading
  create_database(app)

  # Setup the Login Manager
  login_manager = LoginManager()
  login_manager.login_view = 'auth.login'
  login_manager.init_app(app)

  @login_manager.user_loader
  def load_user(id):
    return User.query.get(int(id))

  return app

def create_scheduler(app):
  from .data_fetch import cron_reading
  scheduler = APScheduler()
  scheduler.add_job(id='Scheduled Task',
                    func=cron_reading,
                    kwargs={'app':app},
                    trigger="interval",
                    minutes=READING_DELTA)
  return scheduler

def create_database(app):
  if not path.exists('website/' + DB_NAME):
    db.create_all(app=app)
    # TODO Inject fake data if creatng new?
    print("Created Database!")
