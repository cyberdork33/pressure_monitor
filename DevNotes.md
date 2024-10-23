# Water Pressure Monitoring System Development

## Introduction
I set out to build a system that could constantly measure the water pressure available from my County-Provided Reclaimed Water Service since it is only available certain times of the day. Although it is supposed to follow a particular schedule for availability, I have not found that schedule to be reliable. In order to report the issues I am seeing as well as be able to make the measured pressure over time more available to users, I started trying to regularly check the water presure available with an analog meter. This got old quick, so I decided to develop a monitoring system. I went ahead and obtained items that should allow me to develop a pressure monitoring system that will regularly take measurements, record them, and publish them.

First looked for a cheap Pressure Sensor/Tranducer on Amazon. After a quick look around, it seems [these Walfront Pressure Tranducers](https://www.amazon.com/gp/product/B0748BHLQL/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&psc=1) are highly available, though the actual information for them is a bit limited. I have an analog meter on my water line currently, I have never seen it measure at or above 70 psi, so I decided that a 100 psi range sensor should work. The sensor worked on 5V (easily supplied by many USB power transormers these days), so I just ordered it as a starting point for further development.

Although, my envisioned system could have probably been more easily implemented with an Arduino, and I have been meaning to get my hands on a Raspberry Pi for other reasons anyway, so I chose to use that instead. I previously had previously purchased a Raspberry Pi several years ago, but it had a lot of problems with corrupting my SD Cards, so I returned it and haven't had one since. The Raspberry Pi has evolved quite a bit since then, so a lot of the other items I had on hand really would work with the current models, plus I would need cables and a case, so I just looked for a decent kit. I just searched Amazon and found a [decent looking kit from CanaKit](https://www.amazon.com/gp/product/B08QQ5KY1J/ref=ppx_yo_dt_b_asin_title_o06_s00?ie=UTF8&psc=1). As the Raspberry Pi does not have an analog input (at least of of the day of this writing), I needed an Analog to Digital Converter.

I did not want to have to do a lot of breadboading and circuit development, I looked specifically for ADCs that were specifically for the Raspberry Pi. I initially found the [8-Channel 12-Bit ADC for Raspberry Pi](https://www.seeedstudio.com/8-Channel-12-Bit-ADC-for-Raspberry-Pi-STM32F030.html), but it was not immediately available, so looking at other ADCs at their site led me to the [4-Channel 16-Bit ADC for Raspberry Pi (TI ADS1115)](https://www.seeedstudio.com/4-Channel-16-Bit-ADC-for-Raspberry-Pi-ADS1115.html). It seemed to be able to handle inputs up to 5V (which the pressure sensor could be capable of) and was only a dollar more, so...

### Hardware Used
* [Raspberry Pi 4 4GB Model B](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/)
* [Walfront 100 psi Pressure Transducer](https://www.amazon.com/gp/product/B0748BHLQL/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&th=1)
* [4-Channel 16-Bit ADC for Raspberry Pi (TI ADS1115)](https://www.seeedstudio.com/4-Channel-16-Bit-ADC-for-Raspberry-Pi-ADS1115.html)

## Development Notes

### Initial Setup and Checkout
Once I received all the components, I setup the Raspberry Pi with Raspian and confirmed that the pressure tranducer is indeed sending a varying analog signal with varying pressure.

### ADC Setup
I then set out to interface the ADC to the Raspberry Pi. I have not actually worked with hardware interfaces myself, though I have been exposed to instrumentation in engineering school though it was all generally pre-packaged data aquisition systems and I did not have to write and code. I generally understood that the pressure sensor that I selected was analog and would produce a varying voltage output based on the measured pressure and that the ADC should be able to read that and produce digital signals that can in turn be utilized by software. Reading the [information available from Seeed](https://wiki.seeedstudio.com/4-Channel_16-Bit_ADC_for_Raspberry_Pi-ADS1115/) on the device, I made sure the appropriate modules and settings were implemented on the Raspberry Pi to expose the ADC to the operating system. Specifically, this involved:
* Enabling the I2C kernel module
* Setting some `dtparam` and `dtoverlay` values in the Raspberry Pi `/boot/config.txt` file.

```
dtoverlay=ads1115
dtparam=i2c_arm_baudrate=400000
dtparam=cha_enable
dtparam=chb_enable
dtparam=chc_enable
dtparam=chd_enable
```
I can't say that I understand what specifically this is, but I can see that it is setting a communication datarate over the I2C bus and enabling 4 channels of input on the device. Once I did this though, I could see the I2C device exposed in the filesystem, though I had not idea how to utilze that exposure in software. There is an [Eagle file](https://files.seeedstudio.com/wiki/4-Channel_16-Bit_ADC_for_Raspberry_Pi-ADS1115/res/4-Channel%2016-Bit%20ADC%20for%20Raspberry%20Pi(ADS1115).zip) and a [Datasheet](https://files.seeedstudio.com/wiki/4-Channel_16-Bit_ADC_for_Raspberry_Pi-ADS1115/res/ADS1115.pdf) for the device available as well. There is also some [software available](https://github.com/Seeed-Studio/pi-hats/archive/master.zip) on the wiki page, though after downloading it and attempting to use it, I did not find it very helpful. I also found the [main repository for this software on GitHub](https://github.com/Seeed-Studio/pi-hats). It seemed to rely on the filesystem exposure, but was developed for a previous or other operating system setup.

In some quick additional research, I found that this particular ADC was a little more difficult to setup than some others as far as a software interface, but I eventually found a [ADS1x15 Python Library](http://www.python-exemplary.com/download/ADS1x15.zip) (`ADS1x15.py`) written by Tony DiCola of Adafruit Industries and contributed to the Public Domain. I am not very experienced with Python, but I know that it is pretty easy to use. There was some example code provided to use the library, and I used this to verify that it was indeed working.

## Coding up Software for Calibration
The sample code provided with the library included a 'simpletest' script. I utilized this as a starting point to develop a script for making batch readings at setpoints in anticipation for performing a full system calibration in the future.

## Reference

Original Link
[Walfront 100 psi Pressure Transducer](https://www.amazon.com/gp/product/B0748BHLQL/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&th=1)

Data Table from Amazon

|                |               |
| :---           | :---          |
| EAN            | 0736691391294 |
| Model Number   | LEPAZA60120   |
| Part Number    | 9687283011    |
| UNSPSC Code    | 41110000      |
| Input          | 0-100 psi     |
| Output | 0.5V~4.5V linear voltage output. 0 psi outputs 0.5V, 50 psi outputs 2.5V, 100 psi outputs 4.5V. |
| Accuracy | within 2% of reading (full scale). |
| Thread | 1/8"-27 NPT |
| Wiring Connector | Water sealed quick disconnect. Mating connector and wire harness (pigtail) is included. |
| Wiring | Red for +5V; Black for ground; Blue for signal output. |

Unfortunately, this information does not seem correct as the data points they list for a linear output between 0.5 V and 4.5 V does not make sense. Some discussion on using these with Raspberry Pi is here: https://raspberrypi.stackexchange.com/questions/54155/connect-a-pressure-sensor-with-raspberry-pi-2

> However, the output of the device is really just a function of voltage in and you can also run in on 3.3v if it makes you feel more comfortable.
>
> All that said, similar-looking sensors run at also much lower pressures (0-10 psi, for instance) and their performance will be very different. Regardless it is necessary to locate the vendor-specific piece of info for your device that explains the transfer function.
>
> In the case of what I think is this sensor, the function is `Vout = Vcc(.66667 * P + .1)` This info is also embedded in a few python examples that are floating around out there for reading this sensor.
>
> For example, at 100psi (.69 mPa) and 5v Vcc, you should see something like:
>
> `5 * (.66667 * .69 + .1) = 2.8v`
>
> Note that if you used 3.3v as Vcc you would get something more like 1.848v out reported to your ADC.

[Texas Instruments ADS1115](https://www.ti.com/product/ADS1115)

|                |               |
| :---           | :---          |
| Resolution | 16 bits |
| Number of input channels | 4 |
| Sample rate (Max) | 0.86 kSPS |
| Interface type | I2C |
| Architecture | Delta-Sigma |
| Input type | Differential, Single-Ended |
| Multi-channel configuration | Multiplexed |
| Reference mode | Int |
| Input range (Max)* | 5.5 V |
| Input range (Min)	| 0 V |
| Features | Comparator, Oscillator, PGA |
| Power consumption (Typ) | 0.3 mW |
| Analog voltage AVDD (Min) | 2 V |
| Analog voltage AVDD (Max) | 5.5 V |

Must `sudo apt-get install libatlas-base-dev` to install the libblas library


## Dev Environment

Use a python virtual environment:
```
python3 -m venv venv
source venv/bin/activate
```

Install dependencies
```
pip install -r requirements.txt
```

RPi source voltage is pretty much exactly 3.3 V as measured at the sensor connector.

## Rpi running server

supervisor service

config file `/etc/supervisor/conf.d/supervisor.conf`:
```
[supervisord]
nodaemon=true

[program:nginx]
command=/usr/sbin/nginx -g 'daemon off;'
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:uwsgi]
command=/usr/bin/uwsgi --ini /etc/uwsgi/uwsgi-common.ini --ini /app/uwsgi-app.ini
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

```

https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-22-04
