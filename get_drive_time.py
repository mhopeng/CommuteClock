#!/usr/bin/python
#
# Script to process the traffic info from 511 (Caltrans) for the 280S commute
#  API info at: http://511.org/developer-resources_driving-times-api.asp
#
# Matthew Hopcroft
#   mhopeng@gmail.com
#
# v2.0 Jul2016
#   update to use new 511.org API
# v1.0 Jul2015
#   added route selection
# v0.9 Nov2014
#
# Example URL:
# wget -O drivetime1.xml "http://api.511.org/traffic/traffic_segments?api_key=xxxx-yyyy&road=511.org/8269,511.org/27775&limit=10000&format=xml"

# Example Response contains a <traffic_segments> object:
# 	<traffic_segments>
# 		<traffic_segment>
# 			<link rel="self" href="/traffic/traffic_segments/511.org/104020"/>
# 			<link rel="jurisdiction" href="http://api.511.org/jurisdictions/511.org/"/>
# 			<id>511.org/104020</id>
# 			<updated>2014-03-10T22:33Z</updated>
# 			<roads>
# 				<road>
# 					<link rel="self" href="/traffic/roads/511.org/27775"/>
# 					<name>I-280 S</name>
# 					<direction>S</direction>
# 					<from>I-280 S @ 25TH ST</from>
# 					<to>I-280 S @ CESAR CHAVEZ ST</to>
# 				</road>
# 			</roads>
# 			<geography>
# 				<gml:LineString srsName="urn:ogc:def:crs:EPSG::4326">
# 					<gml:posList>37.7525629990864 -122.391579000316938 37.752457000329684 -122.391579000316938 37.752276999796671 -122.391587999639469 37.752098000304194 -122.391605000256206 37.751941000281775 -122.391625000347702 37.751742000145619 -122.391657999959648 37.751587000207735 -122.391688999921783 37.75140999989074 -122.39172999992968 37.75127900020609 -122.391765999914682 37.751127000221778 -122.391815000318502 37.750975999998239 -122.391869999671769 37.750847999769704 -122.391922000448616 37.750683000030747 -122.391996999893365 37.750588999834143 -122.39204499957394 37.750317000058502 -122.392175999993512 37.750260000336532 -122.392205000305822 37.750092999826791 -122.392284999773466 37.750065000282852 -122.392299999842066 37.750061773508413 -122.392301589172547</gml:posList>
# 				</gml:LineString>
# 			</geography>
# 			<current_speed>102</current_speed>
# 			<current_travel_time>11</current_travel_time>
# 			<historical_speed>88</historical_speed>
# 			<historical_travel_time>12</historical_travel_time>
# 			<link rel="historical_traffic_conditions" href="/traffic/traffic_segments/511.org/104020/historical_conditions"/>
# 		</traffic_segment>
# 	</traffic_segments>
#

from __future__ import division
# use the "requests" package for URL handling: sudo pip install requests
import requests
# use standard package ElementTree for XML parsing
import xml.etree.ElementTree as ET
import sys
import time

# The 511 Developer token to use for requesting data:
#  Request a token (free registration) at: http://511.org/developers/list/tokens/create
api_token='xxxxxxxx-yyyy-zzzz-wwww-vvvvvvvvvvvv'
# The new API does not support destination routing, so the route is hardcoded.
# seg_list is the list of segment ID numbers which are part of the route.
# The first two segment are CA-1 N, and the rest are 280S between CA-1 and Alpine Rd.
seg_list = [
'511.org/151100',
'511.org/151110',
'511.org/104130',
'511.org/104140',
'511.org/104150',
'511.org/104160',
'511.org/104170',
'511.org/104180',
'511.org/104190',
'511.org/104200',
'511.org/104210',
'511.org/104220',
'511.org/104230',
'511.org/104240',
'511.org/104250',
'511.org/104260',
'511.org/104270',
'511.org/104280',
'511.org/104290',
'511.org/104300',
'511.org/104310',
'511.org/104320',
'511.org/104330',
]
# estOther is the drive time for the segments the 511 does not cover
#  14 min to get to 280, 8 min to get from 280 to Stanford
estOther = 14 + 8
# Baseline value (no traffic, middle of the night)
baseTime = 22


print('get_drive_time.py\n' )

# get the traffic info
print('Requesting traffic data from 511.org...' )
r = requests.get('http://api.511.org/traffic/traffic_segments?api_key={0}&road=511.org/8269,511.org/27775&limit=10000&format=xml'.format(api_token))

if r.status_code != 200:
	print('ERROR: Problem with URL request')
	print('Response status code {0}'.format(r.status_code) )
	sys.exit(r.status_code)
elif r.content.find('Error') >= 0:
	print('WARNING: 511 server returned an error\n')
	print(r.content)
	print('')
	sys.exit(1)

# establish time of data
nowTime = time.localtime()
print(' Local time is ' + time.strftime("%Y/%m/%d-%H:%M:%S",nowTime))

# r.content contains the reply XML string
# parse the XML into a tree
root = ET.fromstring(r.content)
#print(r.content)


# the xml tree contains "segments", i.e portions of roads.
traffic_segments = root.find('traffic_segments')
segments = traffic_segments.findall('traffic_segment')

# Scan the entire xml tree and pull out the segments that match the list of segments on our route.
print('Find matching segments...')
# get roads in path, match to target list
seg_names = []
travel_times = []
hist_travel_times = []
for pdx, segment in enumerate(segments):
	segment_id = segment.find('id').text
	if segment_id in seg_list:
		#print(' Segment {0}'.format(segment_id))
		seg_names.append(segment_id)
		# travel time values are in seconds
		travel_times.append(int(segment.find('current_travel_time').text))
		hist_travel_times.append(int(segment.find('historical_travel_time').text))

print(' Found {0} matching segments'.format(len(seg_names)))
curTime = sum(travel_times)/60
histTime = sum(hist_travel_times)/60
print(' Current travel time is {0:.1f} minutes'.format(curTime) )
print(' Typical travel time is {0:.1f} minutes'.format(histTime) )

# get traffic incidents
# incidents = paths[route_index].findall('incidents')
# incident_list = incidents[0].findall('incident')
# if len(incident_list) > 0:
# 	print(' Traffic incidents:')
# 	for incident in incident_list:
# 		print('  {0}'.format(incident.text) )
# else:
# 	print(' No traffic incidents reported at this time')


# estimate arrival time
estDrive = estOther + curTime
print(' Estimated time of Arrival: {0}'.format(time.strftime('%A, %d %b %Y, %H:%M',time.localtime(time.mktime(nowTime) + (60 * estDrive)))) )
print('    [data provided by 511.org: http://www.511.org]\n')
