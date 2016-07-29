from __future__ import division
# use the "requests" package for URL handling: sudo pip install requests
import requests
# use standard package ElementTree for XML parsing
import xml.etree.ElementTree as ET
import sys
import time




# r.content contains the reply XML string
# parse the XML into a tree
#root = ET.fromstring(r.content)
#print(r.content)

tree = ET.parse('traffic_segments.xml')
root = tree.getroot()


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
target_route = ['CA-35']
print('Find segments for road "{0}"'.format(target_route[0]))
# get roads in path, match to target
route_index = []
for pdx, segment in enumerate(segments):
	#print(' Segment {0}, id {1}'.format(pdx,segment.find('id').text) )
	road_names = []
	#print(' Path {0}:'.format(pdx) )
	roads = segment.find('roads')
	segment_id = segment.find('id').text

	road_list = roads.findall('road')
	#print('  Found {0} roads.'.format(len(road_list)) )
	for road in road_list:
		#print('  {0} from {1} to {2}'.format(rd.find('name').text,rd.find('from').text,rd.find('to').text) )
		road_names.append(road.find('name').text)
	if road_names == target_route:
		print(' {3}: {0} from {1} to {2}'.format(road.find('name').text,road.find('from').text,road.find('to').text,segment_id) )
		route_index.append(pdx)
print(' Found {0} matching segments'.format(len(route_index)))
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
