from flask import Flask

def create_app():
  app = Flask(__name__)
  app.config['SECRET_KEY'] = '78efdeeb9a6135ae65acf8a797ede88d775047cb36a7c80c9f17f3e3'

  from .views import views
  from .auth import auth

  app.register_blueprint(views, url_prefix='/')
  app.register_blueprint(auth, url_prefix='/')  

  return app