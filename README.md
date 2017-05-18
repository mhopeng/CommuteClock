# CommuteClock
NOTE: As of 2017, this project has been converted from 511.org APIs to Google Traffic APIs.

A software + hardware project for predicting car commute times in the San Francisco Bay area.

CommuteClock is a hardware project to create a "clock" which displays the projected arrival time when traveling by car.
The time shown on the clock is the time you should expect to arrive at your destination if you leave immediately.
In addition, the recent traffic history is shown, so that you can see if conditions are getting better or worse.
The project is designed for car commuters, and makes use of the data provided by Google.
It could be modified to support any other mode of transport supported by Google in your region.

![cclock_1](https://cloud.githubusercontent.com/assets/13460989/8977347/2ea9ce9e-364d-11e5-900f-bea73bebcab5.jpg)

The software portion of the project is a basically a simple example of using the [Google API for Traffic](https://developers.google.com/maps/documentation/distance-matrix/intro#traffic-model).

The hardware portion of the project uses a Raspberry Pi with two LED displays to display two things:

1. A regularly updated estimate of the predicted arrival time for a given driving route.
2. The recent history of the traffic conditions on the driving route so that the trend can be seen.

Software:  
The python script "get_drive_time.py" requests current driving times data from Google and displays the result.
The python script "display_drive_time_8x8.py" will request the current driving time and display the results on the LED displays (see below).

Hardware:  
The hardware design uses a Raspberry Pi with two LED displays:

1. Seven-segment display with I2C controller:
	https://www.adafruit.com/products/879
2. 8x8 multicolor LED matrix display with I2C controller:
	http://www.adafruit.com/products/902

The python script "display_drive_time_8x8.py" will request the current driving times data and display the results on the LED displays.
Various parameters for operation are given in the configuration file "CommuteClock.cfg". Sample configuration files for supervisord are included which will start the clock automatically when the RPi is booted.

Documentation for connecting the displays and using the appropriate python libraries is here:  
https://learn.adafruit.com/matrix-7-segment-led-backpack-with-the-raspberry-pi/hooking-everything-up

![cclock_pi](https://cloud.githubusercontent.com/assets/13460989/8977349/326b9292-364d-11e5-8cb1-61277df2e736.jpg)

See the included configuration file for details of the configuration options.
