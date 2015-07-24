#!/bin/bash
#
# bash script which illustrates the basic use of the 511 Traffic Driving Times API.
#  More info and free registration for a API Token at:
#  http://www.511.org/developer-resources_driving-times-api.asp

API_TOKEN=xxxxxxxx-yyyy-zzzz-wwww-vvvvvvvvvvvv

START=1473
DEST=388

# Step 1: get list of all possible origin points in the network:
wget -O origins1.xml "http://services.my511.org/traffic/getoriginlist.aspx?token=$API_TOKEN"

# Step 2: Get list of all possible destination points for the selected origin:
wget -O destinations1.xml "http://services.my511.org/traffic/getdestinationlist.aspx?token=$API_TOKEN&o=$START"

# NOT SHOWN: Somehow select your start and endpoints from the xml files returned above.
#  For one-of uses, use the web page at 511.org to select intersections, then search the
#  xml files for these intersections to get the identifier for the intersection.

# Step 3: Request drive time data for the origin and destination selected from above
wget -O drivetime1.xml "http://services.my511.org/traffic/getpathlist.aspx?token=$API_TOKEN&o=$START&d=$DEST"