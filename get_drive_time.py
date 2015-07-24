#!/usr/bin/python
#
# Script to process the traffic info from 511 (Caltrans) for the 280S commute
#  API info at: http://511.org/developer-resources_driving-times-api.asp
#
# Matthew Hopcroft
#   mhopeng@gmail.com
#
# v1.0 Jul2015
#   added route selection
# v0.9 Nov2014
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

from __future__ import division
# use the "requests" package for URL handling: sudo pip install requests
import requests
# use standard package ElementTree for XML parsing
import xml.etree.ElementTree as ET
import sys
import time

# The 511 Developer token to use for requesting data:
api_token='1d19c537-9bf7-4687-bc8f-1e6e13c22ba7'
# Start point: Daly city 280 S / CA 1 intersection
startpoint='88'
# End point: Portola Valley, Sandhill Rd. exit from 280 S
endpoint='1061'
# Target route (there may be more than one route between the Start and End points)
#  Route specified as a list of road names, in order of travel
target_route = ['I-280 S']
# estOther is the drive time for the segments the 511 does not cover
#  14 min to get to 280, 8 min to get from 280 to Stanford
estOther = 14 + 8
# Baseline value (no traffic, middle of the night)
baseTime = 22

# get the traffic info
print('Requesting traffic data from CalTrans...')
r = requests.get('http://services.my511.org/traffic/getpathlist.aspx?token={2}&o={0}&d={1}'.format(startpoint,endpoint,api_token))

if r.status_code != 200:
	print('ERROR: Problem with URL request')
	print('Response status code {0}'.format(r.status_code) )
	sys.exit(r.status_code)
	
# establish time of data
nowTime = time.localtime()

# r.content contains the reply XML string
# parse the XML into a tree
root = ET.fromstring(r.content)
#print(r.content)


# the xml tree contains "paths", i.e. possible routes
#  in this case there should be only one path
paths = root.findall('path')
if len(paths) > 1:
	print('Received {0} possible paths.'.format(len(paths)) )
if len(paths) == 0:
	print('ERROR: no routes found')
	sys.exit(1)

# get roads in path, match to target
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
	if road_list == target_route:
		#print('  [Target Route]')
		route_index = pdx


print('{0}\nCaltrans/511 travel time for route {1} ({2})'.format(time.strftime('%A, %d %b %Y, %H:%M',nowTime),target_route,route_index) )


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
estDrive = estOther + curTime
print(' Estimated time of Arrival: {0}'.format(time.strftime('%A, %d %b %Y, %H:%M',time.localtime(time.mktime(nowTime) + (60 * estDrive)))) )
print('')