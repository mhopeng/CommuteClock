from __future__ import division
# use the "requests" package for URL handling: sudo pip install requests
import requests
# use standard package ElementTree for XML parsing
import xml.etree.ElementTree as ET
import sys
import time

# Method:
#-Request all data for 280S and CA1N, and then filter out the relevant parts (600 kb per request).
#http://api.511.org/traffic/traffic_segments?api_key=fec28ef2-4986-43ba-85b4-9cff2420bb3c&road=511.org/8269,511.org/27775&limit=10000&format=xml

# The 511 Developer token to use for requesting data:
#  Request a token (free registration) at: http://511.org/developers/list/tokens/create
api_token='fec28ef2-4986-43ba-85b4-9cff2420bb3c'
estOther = 14 + 8
# Baseline value (no traffic, middle of the night)
baseTime = 22

###########

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


# r.content contains the reply XML string
# parse the XML into a tree
root = ET.fromstring(r.content)
#print(r.content)

# for testing from xml file on disk
#tree = ET.parse('traffic_segments_280S_CA1N.xml')
#root = tree.getroot()


# the xml tree contains "paths", i.e. possible routes
#  in this case there should be only one path
#paths = root.findall('path')
traffic_segments = root.find('traffic_segments')
segments = traffic_segments.findall('traffic_segment')

print('Found {0} traffic segments.'.format(len(segments)) )
if len(segments) == 0:
	print('ERROR: no segments found')
	sys.exit(1)

#target_route = ['I-280 S']
#target_route = ['CA-35']
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

print('Find matching segments...')
# get roads in path, match to target
seg_names = []
travel_times = []
hist_travel_times = []
for pdx, segment in enumerate(segments):
	segment_id = segment.find('id').text
	if segment_id in seg_list:
		print(' Segment {0}'.format(segment_id))
		seg_names.append(segment_id)
		travel_times.append(int(segment.find('current_travel_time').text))
		hist_travel_times.append(int(segment.find('historical_travel_time').text))

print(' Found {0} matching segments'.format(len(seg_names)))
print(' Total travel time is {0:.1f} minutes'.format(sum(travel_times)/60))
print(' Typical travel time is {0:.1f} minutes'.format(sum(hist_travel_times)/60))
#
#
# print('{0}\nEstimated travel time for route {2}: {1}'.format(time.strftime('%A, %d %b %Y, %H:%M',nowTime),target_route,route_index) )
#
#
# # get Travel Times
# curTime = int(paths[route_index].find('currentTravelTime').text)
# print(' Current Travel Time with traffic: {0} min'.format(curTime) )
# typTime = int(paths[route_index].find('typicalTravelTime').text)
# print(' Typical Travel Time at this time: {0} min'.format(typTime) )
#
# # get traffic incidents
# incidents = paths[route_index].findall('incidents')
# incident_list = incidents[0].findall('incident')
# if len(incident_list) > 0:
# 	print(' Traffic incidents:')
# 	for incident in incident_list:
# 		print('  {0}'.format(incident.text) )
# else:
# 	print(' No traffic incidents reported at this time')
