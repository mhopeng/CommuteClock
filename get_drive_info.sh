#!/bin/bash
#
# bash script which illustrates the basic use of the 511 Traffic Driving Times API.
#  More info and free registration for a API Token at:
#  http://511.org/developers/list/resources/
#
# These examples use XML data, but you can use JSON by changing the "format" parameter.
#
# Matthew Hopcroft
#   mhopeng@gmail.com

API_TOKEN=xxxxxxxx-yyyy-zzzz-wwww-vvvvvvvvvvvv

URL_BASE="http://api.511.org"

# Step 1: Get list of all "roads" included in the 511 data set:
echo "wget -O roads.xml $URL_BASE/traffic/roads?api_key=$API_TOKEN&limit=10000&format=xml"
wget -O roads.xml "$URL_BASE/traffic/roads?api_key=$API_TOKEN&limit=10000&format=xml"

# Step 2: Get list of all "traffic segments" on the road of interest:
#  This example uses 280 S
echo "wget -O segments.xml http://services.my511.org/traffic/traffic_segments?api_key=$API_TOKEN&road=511.org/27775&limit=10000&format=xml"
wget -O segments.xml "http://services.my511.org/traffic/traffic_segments?api_key=$API_TOKEN&road=511.org/27775&limit=10000&format=xml"

# NOT SHOWN: Somehow select your traffic segments from the xml files returned above.
#  The segments are returned in order, North to South, with ascending id numbers.
