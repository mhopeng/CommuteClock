#!/usr/bin/python
#
# Script to display the traffic info from 511 (Caltrans) for the 280S commute
#  on a multicolor 8x8 LED matrix
#  API info at: http://511.org/developer-resources_driving-times-api.asp
#  Hardware info at: https://learn.adafruit.com/matrix-7-segment-led-backpack-with-the-raspberry-pi/hooking-everything-up
#
# mhopeng@gmail.com
# v1.0 Jan2015
#
# Example URL:
# wget -O drivetime1.xml "http://services.my511.org/traffic/getpathlist.aspx?token=1d19c537-9bf7-4687-bc8f-1e6e13c22ba7&o=88&d=1061"
#
# Example Response:
#
# <?xml version="1.0" encoding="UTF-8"?>
# <paths>
# 	<path>
# 		<currentTravelTime>22</currentTravelTime>
# 		<typicalTravelTime>22</typicalTravelTime>
# 		<miles>24.3</miles>
# 		<segments>
# 			<segment>
# 			<road>I-280 S</road>
# 			</segment>
# 		</segments>
# 		<incidents>
# 			<incident>CHP : Overturned vehicle on I-280 Southbound before Bunker Hill Dr (San Mateo). Center Divider blocked. Expect delays.</incident>
# 		</incidents>
# 	</path>
# </paths>
#

from __future__ import division
# use the "requests" package for URL handling: sudo pip install requests
import requests
# use standard package ElementTree for XML parsing
import xml.etree.ElementTree as ET
import sys
import time

from Adafruit_LED_Backpack import BicolorMatrix8x8
from Adafruit_LED_Backpack import SevenSegment

# Note: pixel color values are globals:
#   BicolorMatrix8x8.RED, BicolorMatrix8x8.GREEN, BicolorMatrix8x8.YELLOW

# Start point: Daly city 280 S / CA 1 intersection
startpoint='88'
# Endpoint: Portola Valley, Sandhill Rd. ext from 280 S
endpoint='1061'
# estDrive is the total estimated drive time including the segments the 511 does not cover
#  14 min to get to 280, 8 min to get from 280 to Stanford
estOther = 14 + 8
# Baseline value (no traffic, middle of the night)
baseTime = 22
# display color levels
baselvl = 22
greenlvl = 2
yellowlvl = 4
redlvl = 7

print('{0}\nDisplay Commute data\n'.format(time.strftime('%A, %d %b %Y, %H:%M:%S',time.localtime())) )
data_file='commute_data.csv'

# initialize LED display
# Create display instance on default I2C address (0x70) and bus number.
display = BicolorMatrix8x8.BicolorMatrix8x8(address=0x70)
sevenseg = SevenSegment.SevenSegment(address=0x72)

# Alternatively, create a display with a specific I2C address and/or bus.
# display = Matrix8x8.Matrix8x8(address=0x74, busnum=1)

# Initialize the display(s). Must be called once before using the display.
display.begin()
display.clear()
display.write_display()	
sevenseg.begin()
sevenseg.clear()
sevenseg.write_display()
# turn on the colon to show that we are working...
sevenseg.set_colon(True)
sevenseg.write_display()

# create 2D array for pixel values
pxArray=[[0 for y in range(8)] for x in range(8)]


try:
	while 1:
		# get the traffic info
		r = requests.get('http://services.my511.org/traffic/getpathlist.aspx?token=1d19c537-9bf7-4687-bc8f-1e6e13c22ba7&o={0}&d={1}'.format(startpoint,endpoint))

		if r.status_code != 200:
			print('ERROR: Problem with URL request')
			print('Response status code {0}'.format(r.status_code) )
			sys.exit(r.status_code)

		# r.content contains the reply XML string
		# parse the XML into a tree
		root = ET.fromstring(r.content)

		# the xml tree contains "paths", i.e. possible routes
		#  in this case there should be only one path
		paths = root.findall('path')
		if len(paths) > 1: print('WARNING: expected only 1 path, but found {0}'.format(len(paths)) )
		if len(paths) == 0:
			print('ERROR: no routes found')
			sys.exit(1)
	
		nowTime = time.localtime()

		print('{0}\nCaltrans/511 travel time for 280 S'.format(time.strftime('%A, %d %b %Y, %H:%M',nowTime)) )

		# get Travel Times
		curTime = int(paths[0].find('currentTravelTime').text)
		print(' Current Travel Time with traffic: {0} min'.format(curTime) )
		typTime = int(paths[0].find('typicalTravelTime').text)
		print(' Typical Travel Time at this time: {0} min'.format(typTime) )

		# get traffic incidents
		incidents = paths[0].findall('incidents')
		incident_list = incidents[0].findall('incident')
		if len(incident_list) > 0:
			print(' Traffic incidents:')
			for incident in incident_list:
				print('  {0}'.format(incident.text) )
		else:
			print(' No traffic incidents reported at this time')
		
		## Update LED display
		# shift the display pixel array
		pxArray.insert(0,pxArray.pop())
		# clear old values
		pxArray[0] = [0 for k in range(8)]
		# insert new values in pixel array
		dispTime = int(max(0,curTime - baselvl)/2)
		#print('[dispTime: {0}]'.format(dispTime) )
		if dispTime > 0:
			pxArray[0][0:dispTime] = [BicolorMatrix8x8.GREEN] * (dispTime)
		if dispTime > greenlvl:
			pxArray[0][greenlvl:dispTime] = [BicolorMatrix8x8.YELLOW] * (dispTime - greenlvl)
		if dispTime > yellowlvl:
			pxArray[0][yellowlvl:dispTime] = [BicolorMatrix8x8.RED] * (dispTime - yellowlvl)
			
		# write new pixel array
		# Clear the display buffer.
		display.clear()
		# Set pixel at position i, j to appropriate color.
		for x in range(8):
			for y in range(8):
				display.set_pixel(x, y, pxArray[x][y])
		# Write the display buffer to the hardware.  This must be called to
		# update the actual display LEDs.
		display.write_display()		
			
		
		# estimate arrival time
		estDrive = estOther + curTime
		estDriveTime = time.localtime(time.mktime(nowTime) + (60 * estDrive))
		print(' Estimated time of Arrival: {0}'.format(time.strftime('%A, %d %b %Y, %H:%M',estDriveTime)) )

		# show arrival time estimate
		#print(time.strftime('%H%M',estDriveTime))
		sevenseg.print_number_str(time.strftime('%H%M',estDriveTime))
		sevenseg.write_display()
		
		#commScore = (1 - ((curTime - baseTime) / baseTime))*100
		#if commScore >= 90:
		#	commCondition = 'green'
		#elif commScore >= 80:
		#	commCondition = 'yellow'
		#elif commScore >= 70:
		#	commCondition = 'red'
		#else:
		#	commCondition = 'black'

		#print(' Commute Condition {0} ({1:.0f}%)'.format(commCondition,commScore) )
		
		f=open(data_file,'a')
		#f.write('{0},{1},{2},{3:.0f}\n'.format(time.mktime(nowTime),curTime,typTime,commScore) )
		f.write('{0},{1},{2}\n'.format(time.mktime(nowTime),curTime,typTime) )
		f.close()
		
		# wait for the "whole minute" between updates
		#print(60-time.localtime()[5])
		time.sleep(120-time.localtime()[5]) # two minutes between updates


except KeyboardInterrupt:
	print('** Program Stopped (INT signal) ** ' + time.strftime("%Y/%m/%d-%H:%M:%S",time.localtime()) )
	streamEndTime=time.time() # time of stream end, unix epoch seconds
	print('\n')
#except:
#	print('* Other Exception * ' + time.strftime("%Y/%m/%d-%H:%M:%S",time.localtime()) )
#	print("Unexpected error: {0}".format(sys.exc_info()) )
	

#time.sleep(10)
display.clear()
display.write_display()	
sevenseg.clear()
sevenseg.write_display()	
print('Program Exit')

	