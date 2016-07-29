function [curTime, typTime, incidents] = get_drive_time(startpt,endpt,sec_token)
%GET_DRIVE_TIME returns the current traffic conditions from 511.org
%
%M. Hopcroft
% Dec2014
%
%#ok<*ST2NM>

if nargin < 1 || isempty(startpt)
    startpt='88';
end
if nargin < 2 || isempty(endpt)
    endpt='1061';
end
if nargin < 2 || isempty(sec_token)
    sec_token='1d19c537-9bf7-4687-bc8f-1e6e13c22ba7';
end


% estDrive is the total estimated drive time including the segments the 511 does not cover
%  14 min to get to 280, 8 min to get from 280 to Stanford
estOther = 14 + 8;
% Baseline value (no traffic, middle of the night)
baseTime = 22; % minutes

fprintf(1,'%s Caltrans/511 travel time for 280 S:\n',datestr(now));
% get data from server. Query returns XML
trafxml = urlread(['http://services.my511.org/traffic/getpathlist.aspx?token=' sec_token '&o=' startpt '&d=' endpt]);

% parse the XML into DOM
root = javax.xml.parsers.DocumentBuilderFactory.newInstance().newDocumentBuilder.parse(java.io.StringBufferInputStream(trafxml));

% "paths" represents possible routes between endpoints
paths = root.getElementsByTagName('path');
% For this case, should be only one route
firstpath = paths.item(0);

% get driving times
curTimeObj = firstpath.getElementsByTagName('currentTravelTime');
curTime = str2num(curTimeObj.item(0).getTextContent);
fprintf(1,' Current Travel Time with traffic: %d minutes\n',curTime);
typTimeObj = firstpath.getElementsByTagName('typicalTravelTime');
typTime = str2num(typTimeObj.item(0).getTextContent);
fprintf(1,' Typical Travel Time at this time: %d minutes\n',typTime);

% get reported incidents
incidentsObj = firstpath.getElementsByTagName('incidents');
incident_list = incidentsObj.item(0).getElementsByTagName('incident');
incidents={};
if incident_list.getLength==0
    fprintf(1,' No traffic incidents reported at this time\n');
else
    fprintf(1,' %d traffic incidents reported at this time\n',incident_list.getLength);
    for k = 1:incident_list.getLength
        incidents(k)=incident_list.item(k-1).getTextContent;                    %#ok<AGROW>
        fprintf(1,' %s\n',incidents{k});
    end
end
