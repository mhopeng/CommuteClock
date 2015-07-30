# CommuteClock
A software + hardware project for predicting car commute times in the San Francisco Bay area. 

CommuteClock is a hardware project to create a "clock" which displays the projected arrival time when traveling by car.
The time shown on the clock is the time you should expect to arrive at your destination if you leave immediately.
In addition, the recent traffic history is shown, so that you can see if conditions are getting better or worse.
The project is designed for car commuters in the San Francisco Bay area and it makes use of the traffic data provided by 511.org.

![cclock_1](https://cloud.githubusercontent.com/assets/13460989/8977347/2ea9ce9e-364d-11e5-900f-bea73bebcab5.jpg)

The software portion of the project is a basically a simple example of using the 511.org API for Driving Times Services (http://511.org/developer-resources_driving-times-api.asp).

The hardware portion of the project uses a Raspberry Pi with two LED displays to display two things:

1. A regularly updated estimate of the predicted arrival time for a given driving route.
2. The recent history of the traffic conditions on the driving route so that the trend can be seen.

Software:  
The shell script "get_drive_time.sh" illustrates the use of the three 511.org Driving Times API functions.
The python script "get_drive_time.py" requests current driving times data from 511.org and displays the result.

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
