# CommuteClock
A software + hardware project for predicting car commute times in the San Francisco Bay area. 

CommuteClock is a hardware project to create a "clock" which displays the projected arrival time when traveling by car.
The project is designed for car commuters in the San Francisco Bay area and it makes use of the traffic data provided by 511.org.

![cclock_1](https://cloud.githubusercontent.com/assets/13460989/8977347/2ea9ce9e-364d-11e5-900f-bea73bebcab5.jpg)

The software portion of the project is a basically a simple example of using the 511.org API for Driving Times Services.

The hardware portion of the project uses a Raspberry Pi with two LED displays to display two things:  

1. A constantly updated estimate of the predicted arrival time for a given driving route.
2. The recent history of the traffic conditions on the driving route.

Software:  
The shell script "get_drive_time.sh" illustrates the use of the three 511.org Driving Times API functions.
The python script "get_drive_time.py" requests current driving times data from 511.org and displays the result.

Hardware:  
The hardware design uses a Raspberry Pi with two LED displays:

1. Seven-segment display with I2C controller:
	https://www.adafruit.com/products/879
2. 8x8 multicolor LED matrix display with I2C controller:
	http://www.adafruit.com/products/902
	
Documentation for connecting the displays and using the appropriate python libraries is here:  
https://learn.adafruit.com/matrix-7-segment-led-backpack-with-the-raspberry-pi/hooking-everything-up	

![cclock_pi](https://cloud.githubusercontent.com/assets/13460989/8977349/326b9292-364d-11e5-8cb1-61277df2e736.jpg)

The python script "display_drive_time_8x8.py" will request the current driving times data and display the results on the LED displays.
Various parameters for operation are given in the configuration file "CommuteClock.cfg".	

NOTE: The process for specifying the start and end points of the commute is manual and not straightforward. 511.org has assigned ID numbers or "nodes" to each intersection in the network of roads covered by their sensors. For example, the intersection of I-80 and University Avenue in Berkeley is node 1222. You need to select node numbers for the start and end points for the commute and enter them into the configuration file for the Commute Clock.  
Suggested Procedure:  

1. Run the script "get_drive_time.sh" to retrieve an XML file that lists all of the nodes in the 511.org system. This file will be saved as "drive_origins1.xml".
2. Go to the 511.org Traffic website and use the drop-down menus to determine the intersection closest to the start of your commute.
3. Search the XML file (drive_origins1.xml) to find the intersection you selected in Step 1. Note the node number.
4. Modify the script "get_drive_time.sh" to use the node number from Step 2 as the value for the variable "START".
4. Go to the 511.org Traffic website and use the drop-down menus to determine the intersection closest to the end of your commute.
5. Search the XML file (drive_destinations1.xml) to find the intersection you selected in Step 4. Note the node number.
6. Modify the configuration file (CommuteClock.cfg) to include the numbers that you have determined in Steps 2 & 4.
In addition, the configuration file value "EST_OTHER" is a simple constant which is meant to encompass the parts of the commute that are not included in the 511.org data.
