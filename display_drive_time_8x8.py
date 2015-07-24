#!/usr/bin/python
#
## display_drive_time_8x8.py
#
# Script to display the estimated arrival time and recent history for a car commute
#  on a 7-segment LED and a multicolor 8x8 LED matrix controlled by a Raspberry Pi.
#  Uses the traffic data from 511 (Caltrans), and requires a 511 developer token.
# Uses configuration file "CommuteClock.cfg" in same directory, or give location as first
#  command line argument.
#
#  511 API info at: http://511.org/developer-resources_driving-times-api.asp
#  Hardware info at: https://learn.adafruit.com/matrix-7-segment-led-backpack-with-the-raspberry-pi/hooking-everything-up
#
# Matt Hopcroft
#  mhopeng@gmail.com
#
# v1.5 Jul2015
#   add EST_OTHER to config file
#   add PREF_ROUTE to config file
#	update 7-segment display more often than matrix display (bar graph)
# v1.4 Jun2015
#   use config file
#   better error checking for response
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
# wget -O drivetime1.xml "http://services.my511.org/traffic/getpathlist.aspx?token=xxxxxxxx-yyyy-zzzz-wwww-vvvvvvvvvvvv&o=88&d=1061"
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

# Use a config file (v1.4)
import ConfigParser
if len(sys.argv) < 2:
	config_file = os.path.dirname(os.path.abspath(__file__) )
	config_file = os.path.join(config_file,'CommuteClock.cfg')
else:
	config_file = sys.argv[1]
	

##
verstring = "CommuteClock v1.5"
##

# User credentials for the 511.org Driving Times API. Register at:
#  http://www.511.org/developer-resources_driving-times-api.asp
#USER_CRED = 'xxxxxxxx-yyyy-zzzz-wwww-vvvvvvvvvvvv'
# Start point: Daly city I-280 / CA 1 intersection
#START_POINT='1473'
# Endpoint: Menlo Park, Sandhill Rd. exit from I-280 S
#END_POINT='1061'
# Time between updates ("x axis") in minutes
#UPDATE_INTERVAL = 3
# Commute time per pixel ("y axis") in minutes
#COMMUTE_PIXEL = 2
# estOther is the drive time for the segments 511 does not include
#  14 min to get to 280, 8 min to get from 280 to Stanford
#estOther = 14 + 8 # v1.5 move to config file
# Baseline value (no traffic, middle of the night)
#baseTime = 22	# v1.2 not used
# bar graph color levels (in minutes)
#baselvl = 22 # v1.2 use reported typical time for baseline
greenlvl = 2
yellowlvl = 4
redlvl = 7

numRetries = 5 # number of retries before failing when 511 replies are malformed



def main(config_file):

	print('{0}\n{1}: Display Commute data\n'.format(time.strftime('%A, %d %b %Y, %H:%M:%S',time.localtime()),verstring) )
	data_file='commute_data.csv'
	
	# open the configuration file
	print('Reading Config file ' + config_file)
	config = ConfigParser.SafeConfigParser()
	try:
		config_info = config.read(config_file)
		if not config_info:
			print('ERROR: config file not found ("{0}")'.format(config_file) )
			sys.exit(1)
	except:
		print('ERROR: Problem with config file (missing, bad format, etc)')
		print('    (Config file "{0}")'.format(config_file) )
		print("{0}".format(sys.exc_info()) )
		sys.exit(1)
		
	# get the config values
	try:
		USER_CRED = config.get('USER','USER_CRED')
		START_POINT = config.get('COMMUTE','START_POINT')
		END_POINT = config.get('COMMUTE','END_POINT')
		PREF_ROUTE = config.get('COMMUTE','PREF_ROUTE').split(',')
		EST_OTHER = int(config.get('COMMUTE','EST_OTHER'))
		UPDATE_INTERVAL = int(config.get('DISPLAY','UPDATE_INTERVAL'))
		COMMUTE_PIXEL = int(config.get('DISPLAY','COMMUTE_PIXEL'))
	except:
		print("ERROR: Unable to read from config file")
		print(" Unexpected error: {0}".format(sys.exc_info()) )
		sys.exit(1)
		

	# initialize LED displays
	print('Initializing LED displays')
	# Create display instance with I2C address (eg 0x70).
	display = BicolorMatrix8x8.BicolorMatrix8x8(address=0x70)
	sevenseg = SevenSegment.SevenSegment(address=0x72)

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
	startup_splash(display,sevenseg)

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

	##
	# main loop
	print('')
	try:
		retries = 0			# for retrying when errors are received
		update_count = 0	# for updating LED matrix
		
		while retries < numRetries:

			# blank colon to show update in progress
			sevenseg.set_colon(False)
			sevenseg.write_display()
			print('Requesting traffic data from CalTrans...')

			# get the traffic info
			r = requests.get('http://services.my511.org/traffic/getpathlist.aspx?token={2}&o={0}&d={1}'.format(START_POINT,END_POINT,USER_CRED))

			if r.status_code != 200:
				print('ERROR: Problem with URL request')
				print('Response status code {0}'.format(r.status_code) )
				retries += 1
			
			elif r.content.find('Error') >= 0:
				print('WARNING: 511 server returned an error ({0})\n'.format(retries) )
				print(r.content)
				retries += 1 # quit after trying a few times
			else: retries = 0

			nowTime = time.localtime()
			
			# blank colon to show update in progress
			sevenseg.set_colon(True)
			sevenseg.write_display()

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
			if len(paths) > 1 and len(PREF_ROUTE) == 0:
				print('WARNING: received {0} possible paths. Using first in list.'.format(len(paths)) )
			if len(paths) == 0:
				print('ERROR: no routes found')
				sys.exit(1)

			# get roads in possible routes ("paths"), match a route to preferred route
			route_index = []
			for pdx, path in enumerate(paths):
				road_list = []
				#print(' Path {0}:'.format(pdx) )
				segments = paths[pdx].find('segments')
				segment_list = segments.findall('segment')
				for seg in segment_list:
					road = seg.find('road')
					#print('  {0}'.format(road.text) )
					road_list.append(road.text)
				if road_list == PREF_ROUTE:
					#print('Using Route {0}'.format(pdx) )
					route_index = pdx
					break

			if route_index==[]:
				route_index = 0
				road_list = []
				print('WARNING: Preferred route not found. Using first route in list.')
				segments = paths[route_index].find('segments')
				segment_list = segments.findall('segment')
				for seg in segment_list:
					road = seg.find('road')
					#print('  {0}'.format(road.text) )
					road_list.append(road.text)

			print('{0}\nCaltrans/511 travel time for route on {1} ({2})'.format(time.strftime('%A, %d %b %Y, %H:%M',nowTime),road_list,route_index) )

			# get Travel Times
			curTime = int(paths[route_index].find('currentTravelTime').text)
			print(' Current Travel Time with traffic: {0} min'.format(curTime) )
			typTime = int(paths[route_index].find('typicalTravelTime').text)
			print(' Typical Travel Time at this time: {0} min'.format(typTime) )

			# get traffic incidents
			incidents = paths[route_index].findall('incidents')
			incident_list = incidents[0].findall('incident')
			if len(incident_list) > 0:
				print(' Traffic incidents:')
				for incident in incident_list:
					print('  {0}'.format(incident.text) )
			else:
				print(' No traffic incidents reported at this time')
				
			# estimate arrival time
			estDrive = EST_OTHER + curTime
			estDriveTime = time.localtime(time.mktime(nowTime) + (60 * estDrive))
			print(' Estimated time of Arrival: {0}'.format(time.strftime('%A, %d %b %Y, %H:%M',estDriveTime)) )

			# show arrival time estimate on 7-segment display
			#print(time.strftime('%H%M',estDriveTime))
			sevenseg.print_number_str(time.strftime('%H%M',estDriveTime))
			sevenseg.write_display()

			f=open(data_file,'a')
			#f.write('{0},{1},{2},{3:.0f}\n'.format(time.mktime(nowTime),curTime,typTime,commScore) )
			f.write('{0},{1},{2}\n'.format(time.mktime(nowTime),curTime,typTime) )
			f.close()


			## Update LED display
			#   update at startup, and then at a multiple of data updates
			if update_count == 0 or update_count > UPDATE_INTERVAL:
				#print('Update LED matrix')
				update_matrix(display,pxArray,curTime,typTime,incident_list,tiArray,COMMUTE_PIXEL)
				
				# reset update count
				update_count = 1


			# update the LED matrix display less often than the 7-segment display
			update_count += 1

			# wait for the "whole minute" between updates
			#print(60-time.localtime()[5])
			#time.sleep((UPDATE_INTERVAL*60)-time.localtime()[5])
			# v1.5: update time display every minute. Update LED matrix less often.
			time.sleep(60-time.localtime()[5])
			print('')


	except KeyboardInterrupt:
		print('\n** Program Stopped (INT signal) ** ' + time.strftime("%Y/%m/%d-%H:%M:%S",time.localtime()) )
		streamEndTime=time.time() # time of stream end, unix epoch seconds
		print('')
	except:
		print('* Other Exception * ' + time.strftime("%Y/%m/%d-%H:%M:%S",time.localtime()) )
		print("Unexpected error: {0}".format(sys.exc_info()) )


	if retries > 0:
		print('\nCommuteClock: Exit after {0} retries\n'.format(retries) )
		# show error on display
		display.set_image(errorImage)
		display.write_display()
	else:
		display.clear()
		display.write_display()
		sevenseg.clear()
		sevenseg.write_display()
		print('CommuteClock: Program Exit\n')


####
# a function to update the LED matrix display
def update_matrix(display,pxArray,curTime,typTime,incident_list,tiArray,COMMUTE_PIXEL):
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

	return pxArray,tiArray

				
####
# a function for animated "splash screen" at startup
def startup_splash(display,sevenseg):
	# show an animation of the axes on the 8x8 bicolor display

	# Clear the display buffer.
	display.clear()
	
	# turn on colon
	colonset = True
	sevenseg.set_colon(colonset)
	sevenseg.write_display()

	# axes appear
	for k in range (8):
		display.set_pixel(0, k, BicolorMatrix8x8.YELLOW)
		display.set_pixel(k, 0, BicolorMatrix8x8.YELLOW)
		colonset = not(colonset)
		sevenseg.set_colon(colonset)
		sevenseg.write_display()
		display.write_display()
		time.sleep(0.2)

	# axes disappear
	for k in range (8):
		display.set_pixel(0, k, 0)
		display.set_pixel(k, 0, 0)
		colonset = not(colonset)
		sevenseg.set_colon(colonset)
		sevenseg.write_display()
		display.write_display()
		time.sleep(0.2)



if __name__ == "__main__":
    main(config_file)
