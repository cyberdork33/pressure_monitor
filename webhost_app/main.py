import atexit
from website import create_app, create_scheduler

app = create_app()

scheduler = create_scheduler(app)
scheduler.start()
print("scheduler started...")

if __name__ == '__main__':
  # 0.0.0.0 host allows connections from everwhere
  # debug mode loads Flask app twice for some reason, and this
  # causes issues with flask_apscheduler so, disable reloader.
  # https://stackoverflow.com/questions/9449101/how-to-stop-flask-from-initialising-twice-in-debug-mode
  # app.run(host='0.0.0.0', debug=True, use_reloader=False)
  app.run(debug=True, use_reloader=False)

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
