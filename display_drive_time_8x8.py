#!/usr/bin/python
#
# Script to display the traffic info from 511 (Caltrans) for the 280S commute
#  on a multicolor 8x8 LED matrix
#  API info at: http://511.org/developer-resources_driving-times-api.asp
#  Hardware info at: https://learn.adafruit.com/matrix-7-segment-led-backpack-with-the-raspberry-pi/hooking-everything-up
#
# Matthew Hopcroft
#   mhopeng@gmail.com
#
# v1.3 Jun2015
#	startup animation
# v1.2 Jun2015
#	incident display coincides with time
# v1.1 Jun2015
#	added constants for update time
#	startup splash is now the xy axes
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

# NOTE: The 8x8 Bi-Color LED Matrix display is intended to be installed/viewed upside down
#  from the orientation assumed by the interface library. This makes the code easier.

from __future__ import division
import os, sys, time
# use the "requests" package for URL handling: sudo pip install requests
import requests
# use standard package ElementTree for XML parsing
import xml.etree.ElementTree as ET
# use PIL for image manipulation
import Image
import ImageDraw
# use AdaFruit libraries for hardware
from Adafruit_LED_Backpack import BicolorMatrix8x8
from Adafruit_LED_Backpack import SevenSegment
# Note: pixel color values are globals:
#   BicolorMatrix8x8.RED, BicolorMatrix8x8.GREEN, BicolorMatrix8x8.YELLOW

verstring = "CommuteClock v1.3"
# Start point: Daly city I-280 / CA 1 intersection
START_POINT='1473'
# Endpoint: Menlo Park, Sandhill Rd. exit from I-280 S
END_POINT='1061'
# Time between updates ("x axis") in minutes
UPDATE_INTERVAL = 3
# Commute time per pixel ("y axis") in minutes
COMMUTE_PIXEL = 2
# estOther is the drive time for the segments 511 does not include
#  14 min to get to 280, 8 min to get from 280 to Stanford
estOther = 14 + 8
# Baseline value (no traffic, middle of the night)
#baseTime = 22	# v1.2 not used
# bar graph color levels (in minutes)
#baselvl = 22 # v1.2 use reported typical time for baseline
greenlvl = 2
yellowlvl = 4
redlvl = 7

print('{0}\n{1}: Display Commute data\n'.format(time.strftime('%A, %d %b %Y, %H:%M:%S',time.localtime()),verstring) )
data_file='commute_data.csv'

def main():

	# initialize LED displays
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

	# show startup animation
	startup_splash(display)

	## Create 2D arrays for pixel values
	# array for traffic intensity
	pxArray=[[0 for y in range(8)] for x in range(8)]
	# array for traffic incidents (top line of display)
	tiArray=[0 for x in range(8)]

	# create image for "error message"
	errorImage = Image.new('RGB', (8, 8))
	edraw = ImageDraw.Draw(errorImage)
	# Draw an X with two red lines:
	edraw.line((1,1,6,6), fill=(255,0,0))
	edraw.line((1,6,6,1), fill=(255,0,0))

	# main loop
	try:
		while 1:

			# blank colon to show update in progress
			sevenseg.set_colon(False)
			sevenseg.write_display()
			print('Requesting traffic data from CalTrans...')

			# get the traffic info
			r = requests.get('http://services.my511.org/traffic/getpathlist.aspx?token=1d19c537-9bf7-4687-bc8f-1e6e13c22ba7&o={0}&d={1}'.format(START_POINT,END_POINT))

			if r.status_code != 200:
				print('ERROR: Problem with URL request')
				print('Response status code {0}'.format(r.status_code) )
				# show error on display
				display.set_image(errorImage)
				display.write_display()
				sys.exit(r.status_code)

			# blank colon to show update in progress
			sevenseg.set_colon(True)
			sevenseg.write_display()

			nowTime = time.localtime()

			# r.content contains the reply XML string
			# parse the XML into a tree
			try:
				root = ET.fromstring(r.content)
			except:
				print('ERROR: XML parse error.')
				continue

			# the xml tree contains "paths", i.e. possible routes
			#  in this case there should be only one path
			paths = root.findall('path')
			if len(paths) > 1:
				print('WARNING: received {0} possible paths. Using first in list.'.format(len(paths)) )
			if len(paths) == 0:
				print('ERROR: no routes found')
				sys.exit(1)

			# get roads in path
			road_list = []
			segments = paths[0].find('segments')
			segment_list = segments.findall('segment')
			for seg in segment_list:
				road = seg.find('road')
				#print('  {0}'.format(road.text) )
				road_list.append(road.text)


			print('{0}\nCaltrans/511 travel time for route on {1}'.format(time.strftime('%A, %d %b %Y, %H:%M',nowTime),road_list) )

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

			# Clear the display buffer.
			display.clear()

			# shift the display pixel array
			pxArray.insert(0,pxArray.pop())
			# clear old values
			pxArray[0] = [0 for k in range(8)]
			# insert new values in pixel array
			#  v1.2 - use reported typical value for baseline
			#dispTime = int(max(0,curTime - baselvl)/COMMUTE_PIXEL)
			dispTime = int(max(0,curTime - typTime)/COMMUTE_PIXEL)
			#print('[dispTime: {0}]'.format(dispTime) )
			# fill in values in the pixel array according to the "color levels"
			if dispTime > 0:
				pxArray[0][0:dispTime] = [BicolorMatrix8x8.GREEN] * (dispTime)
			if dispTime > greenlvl:
				pxArray[0][greenlvl:dispTime] = [BicolorMatrix8x8.YELLOW] * (dispTime - greenlvl)
			if dispTime > yellowlvl:
				pxArray[0][yellowlvl:dispTime] = [BicolorMatrix8x8.RED] * (dispTime - yellowlvl)

			# write new pixel array
			# Set pixel at position i, j to appropriate color.
			for x in range(8):
				for y in range(8):
					display.set_pixel(x, y, pxArray[x][y])

			# put a yellow box on a display if traffic incident
			if len(incident_list) > 0:
				tiArray.insert(0,tiArray.pop())
				tiArray[0] = BicolorMatrix8x8.YELLOW
			else:
				tiArray.insert(0,tiArray.pop())
				tiArray[0]=0
			#print(tiArray)
			for x in range(8): display.set_pixel(x, 7, tiArray[x])

			# Write the display buffer to the hardware. This must be called to
			#  update the actual display LEDs.
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
			time.sleep((UPDATE_INTERVAL*60)-time.localtime()[5])
			print(' ')


	except KeyboardInterrupt:
		print('\n** Program Stopped (INT signal) ** ' + time.strftime("%Y/%m/%d-%H:%M:%S",time.localtime()) )
		streamEndTime=time.time() # time of stream end, unix epoch seconds
		print('')
	#except:
	#	print('* Other Exception * ' + time.strftime("%Y/%m/%d-%H:%M:%S",time.localtime()) )
	#	print("Unexpected error: {0}".format(sys.exc_info()) )


	#time.sleep(10)
	display.clear()
	display.write_display()
	sevenseg.clear()
	sevenseg.write_display()
	print('Program Exit')


# a function for a "splash screen" at startup
def startup_splash(display):
	# show an animation of the axes on the 8x8 bicolor display

	# Clear the display buffer.
	display.clear()

	# axes appear
	for k in range (8):
		display.set_pixel(0, k, BicolorMatrix8x8.YELLOW)
		display.set_pixel(k, 0, BicolorMatrix8x8.YELLOW)
		display.write_display()
		time.sleep(0.2)

	# axes disappear
	for k in range (8):
		display.set_pixel(0, k, 0)
		display.set_pixel(k, 0, 0)
		display.write_display()
		time.sleep(0.2)



if __name__ == "__main__":
    main()
