# Water Pressure Monitoring System
cyberdork33/pressure_monitor

Code related to a simple raspberry pi water pressuring monitoring system.

### Hardware Used
* [Raspberry Pi 4 4GB Model B](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/)
* [Walfront 100 psi Pressure Transducer](https://www.amazon.com/gp/product/B0748BHLQL/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&th=1)
* [4-Channel 16-Bit ADC for Raspberry Pi (TI ADS1115)](https://www.seeedstudio.com/4-Channel-16-Bit-ADC-for-Raspberry-Pi-ADS1115.html)

## Dependencies
### To interface with the RaspberryPi hardware and ADC:
* adafruit-circuitpython-ads1x15

### For the webui
* Flask
* Flask-Login
* Flask-SQLAlchemy
* plotly
