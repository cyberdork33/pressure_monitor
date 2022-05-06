import requests
from datetime import datetime
from . import db
from .models import MonitorReading

## GLOBALS
DATA_SOURCE_URL = 'http://pressure-pi/json'
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S %Z'


def cron_reading(app):
  app.app_context().push()
  record_new_reading(DATA_SOURCE_URL)
  print("Recorded a new reading through cron.")

##------------------------------------------------------------------------------
## Acquire data from the remote system via web request
def get_new_reading(address: str) -> MonitorReading:
  r = requests.get(address)
  theJSON = r.json()
  # TODO Test for no response!
  print(f"Time String from JSON: {theJSON[0]}")
  timestamp_string = theJSON[0].split('.')[0]
  datetime_object = datetime.strptime(timestamp_string, TIMESTAMP_FORMAT)
  print(f"datetime object: {datetime_object}")
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
