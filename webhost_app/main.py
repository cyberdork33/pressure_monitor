import atexit
from website import create_app, create_scheduler

app = create_app()
scheduler = create_scheduler(app)

if __name__ == '__main__':
  scheduler.start()
  # 0.0.0.0 host allows connections from everwhere
  # debug mode loads Flask app twice for some reason, and this
  # causes issues with flask_apscheduler so, disable relaoder.
  app.run(host='0.0.0.0', debug=True, use_reloader=False)

  # Shut down the scheduler when exiting the app
  atexit.register(lambda: scheduler.shutdown())
