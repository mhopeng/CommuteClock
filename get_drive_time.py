#!/usr/bin/python
#
# Script to process the traffic info from 511 (Caltrans) for the 280S commute
#  API info at: http://511.org/developer-resources_driving-times-api.asp
#
# mhopeng@gmail.com
# v0.9 Nov2014
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
# use the "requests" package for URL handling
import requests
# use standard package ElementTree for XML parsing
import xml.etree.ElementTree as ET
import sys
import time

# Start point: Daly city 280 S / CA 1 intersection
startpoint='88'
# Endpoint: Portola Valley, Sandhill Rd. ext from 280 S
endpoint='1061'
# estDrive is the total estimated drive time including the segments the 511 does not cover
#  14 min to get to 280, 8 min to get from 280 to Stanford
estOther = 14 + 8
# Baseline value (no traffic, middle of the night)
baseTime = 22

# get the traffic info
r = requests.get('http://services.my511.org/traffic/getpathlist.aspx?token=1d19c537-9bf7-4687-bc8f-1e6e13c22ba7&o={0}&d={1}'.format(startpoint,endpoint))

if r.status_code != 200:
	print('ERROR: Problem with URL request')
	print('Response status code {0}'.format(r.status_code) )
	sys.exit(r.status_code)

# r.content contains the reply XML string
# parse the XML into a tree
root = ET.fromstring(r.content)
#print(r.content)

# the xml tree contains "paths", i.e. possible routes
#  in this case there should be only one path
paths = root.findall('path')
if len(paths) > 1: print('WARNING: expected only 1 path, but found {0}'.format(len(paths)) )
if len(paths) == 0:
	print('ERROR: no routes found')
	sys.exit(1)
	
nowTime = time.localtime()

print('{0}\nCaltrans/511 travel time for 280 S:'.format(time.strftime('%A, %d %b %Y, %H:%M',nowTime)) )

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
	
# estimate arrival
estDrive = estOther + curTime
print(' Estimated time of Arrival: {0}'.format(time.strftime('%A, %d %b %Y, %H:%M',time.localtime(time.mktime(nowTime) + (60 * estDrive)))) )
commScore = (1 - ((curTime - baseTime) / baseTime))*100
if commScore >= 90:
	commCondition = 'green'
elif commScore >= 80:
	commCondition = 'yellow'
elif commScore >= 70:
	commCondition = 'red'
else:
	commCondition = 'black'

print(' Commute Condition {0} ({1:.0f}%)'.format(commCondition,commScore) )


	