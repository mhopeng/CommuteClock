#!/usr/bin/python
#
# Script to process the traffic info from Google for the 280S commute
#  API info at: https://developers.google.com/maps/documentation/distance-matrix/
#
# Matthew Hopcroft
#   mhopeng@gmail.com
#
# v1.0 Jan2017
#   Uses google traffic data
#   based on previous version using 511 data
#
# Example URL:
# wget -O drivetime1.xml "https://maps.googleapis.com/maps/api/distancematrix/xml?units=imperial&origins=37.778727,-122.513979&destinations=37.426855,-122.181333&mode=driving&departure_time=now&key=YOUR_API_KEY"
#
# Example Response:
#
# <DistanceMatrixResponse>
#   <status>OK</status>
#   <origin_address>725-825 Point Lobos Ave, San Francisco, CA 94121, USA</origin_address>
#   <destination_address>121 Campus Drive, Stanford, CA 94305, USA</destination_address>
#   <row>
#     <element>
#       <status>OK</status>
#       <duration>
#         <value>2680</value>
#         <text>45 mins</text>
#       </duration>
#       <distance>
#         <value>59758</value>
#         <text>37.1 mi</text>
#       </distance>
#       <duration_in_traffic>
#         <value>2686</value>
#         <text>45 mins</text>
#       </duration_in_traffic>
#     </element>
#   </row>
# </DistanceMatrixResponse>
#

from __future__ import division
# use the "requests" package for URL handling: sudo pip install requests
import requests
# use standard package ElementTree for XML parsing
import xml.etree.ElementTree as ET
import sys
import time

# The Google Developer API Key to use for requesting data:
#  Request a API Key (free registration) at: https://developers.google.com/maps/documentation/distance-matrix/start#get-a-key
api_token='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' # July 2023
# Start point: "725-825 Point Lobos Ave, San Francisco, CA 94121, USA" (Cliff House)
startpoint='37.778727,-122.513979'
# End point: "121 Campus Drive, Stanford, CA 94305, USA" (Lyman)
endpoint='37.426855,-122.181333'


# get the traffic info
print('Requesting traffic data from Google... ({0} -> {1})'.format(startpoint,endpoint) )
r = requests.get('https://maps.googleapis.com/maps/api/distancematrix/xml?units=imperial&origins={0}&destinations={1}&departure_time=now&key={2}'.format(startpoint,endpoint,api_token))

if r.status_code != 200:
	print('ERROR: Problem with Google request')
	print('Response status code {0}'.format(r.status_code) )
	sys.exit(r.status_code)
elif r.text.find('Error') >= 0:
	print('WARNING: Google server returned an error\n')
	print(r.content)
	print('')
	sys.exit(1)

# establish time of data
nowTime = time.localtime()

# r.content contains the reply XML string
# parse the XML into a tree
root = ET.fromstring(r.content)
#print(r.content)


# the xml tree contains routes between the destinations
#  arranged in rows of elements. In this case there should
#  be only one route, so one row with one element
rows = root.findall('row')
if len(rows) > 1:
	print('WARNING {0} rows.'.format(len(rows)) )
if len(rows) == 0:
	print('ERROR: no routes found (0 rows)')
	sys.exit(1)

elements = rows[0].findall('element')
if len(elements) > 1:
	print('WARNING {0} elements.'.format(len(elements)) )
if len(elements) == 0:
	print('ERROR: no routes found (0 elements)')
	sys.exit(1)


# get Travel Time
#curTime = int(elements[0].find('duration_in_traffic').value)
durTraf = elements[0].find('duration_in_traffic')
curTime = int(durTraf.find('value').text)
print(' Current Travel Time with traffic: {0:.1f} min'.format(curTime/60) )
durTyp = elements[0].find('duration')
typTime = int(durTyp.find('value').text)
print(' Typical Travel Time at this time: {0:.1f} min'.format(typTime/60) )


# estimate arrival time
estDrive = curTime/60
print(' Estimated time of Arrival: {0}'.format(time.strftime('%A, %d %b %Y, %H:%M',time.localtime(time.mktime(nowTime) + (60 * estDrive)))) )
print('    [data provided by Google: https://developers.google.com/maps/documentation/distance-matrix]\n')
