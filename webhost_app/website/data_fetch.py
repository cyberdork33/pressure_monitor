import requests, time
from datetime import datetime, timedelta
from . import db
from .models import MonitorReading

## GLOBALS
DATA_SOURCE_URL = 'http://raspberrypi/json'
RECORD_LIFETIME = 1 #weeks


def cron_reading(app):
  app.app_context().push()
  record_new_reading(DATA_SOURCE_URL)
  print("Recorded a new reading through cron.")

# def monitor(app):
#   READING_DELTA = 15*60 #seconds

#   while True:
#     # Get a reading from the pi
#     # Insert into the DB
#     record_new_reading(DATA_SOURCE_URL)
#     print("Recorded a new reading.")
#     # pop old readings
#     for reading in MonitorReading.query.all():
#       time_passed = datetime.utcnow() - reading.datetime
#       if time_passed <= timedelta(weeks=RECORD_LIFETIME):
#         print(f"Removing record from {reading.datetime}")
#     # Pause
#     time.sleep(READING_DELTA)
#     # repeat

##------------------------------------------------------------------------------
## Acquire data from the remote system via web request
def get_new_reading(address: str) -> MonitorReading:
  r = requests.get(address)
  theJSON = r.json()
  print(f"Time String from JSON: {theJSON[0]}")
  without_fracional_seconds = theJSON[0].split('.')[0]
  datetime_object = datetime.strptime(without_fracional_seconds,
                                      '%Y-%m-%d %H:%M:%S')
  print(f"Time from datetime: {datetime_object}")
  reading = MonitorReading( datetime=datetime_object,
                            rawvalue=theJSON[1],
                            voltage=theJSON[2],
                            pressure=theJSON[3])
  return reading

##------------------------------------------------------------------------------
## Acquire data from the remote system via web request and record in DB
def record_new_reading(address: str) -> MonitorReading:
  r = get_new_reading(address)

  db.session.add(r)
  db.session.commit()
  return r

if __name__ == '__main__':
  pass
