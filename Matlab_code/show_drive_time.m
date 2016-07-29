function [curArray, typArray] = show_drive_time(buf_length)
%SHOW_DRIVE_TIME Displays a moving bar graph of the drive time data from
%  511.org.
%
% M. Hopcroft
% mhopeng@gmail.com
%

if nargin < 1 || isempty(buf_length)
    buf_length=20;
end

% estDrive is the total estimated drive time including the segments the 511 does not cover
%  14 min to get to 280, 8 min to get from 280 to Stanford
baseOther = 14 + 8;
% Baseline value (no traffic, middle of the night)
baseTime = 22; % minutes

curArray=zeros(buf_length,3);
typArray=zeros(buf_length,1);
time_axis=1:1:buf_length;

% for testing only
%curArray(2,1)=26.4;
%curArray(2,2)=4.4;
%curArray(2,3)=5.2;

% create figure
figure;
ax=axes;
% use keypress function to quit
global RUNLOOP
RUNLOOP = 1;
set(gcf,'KeyPressFcn',@exitLoop)
title('Driving Time on 280 S')


d = datevec(now);
fprintf('show_drive_time\n  %s\n\n',datestr(d))
%jPause(60-d(6));


while RUNLOOP

    d = datevec(now);
    failcount = 0;
    
    % check traffic every minute
    if mod(round(d(6)),60)==0
    
        % get drive time
        try
            [curTime,typTime,incidents]=get_drive_time;

            curArray = circshift(curArray,[1 0]);
            curArray(1,1) = min(26,curTime);
            estFac = 1.01;
            if curTime > 26
                curArray(1,2) = min(4,curTime-26);
                estFac = 1.05;
            else
                curArray(1,2) = 0;
            end
            if curTime > 30
                curArray(1,3) = curTime-30;
                estFac = 1.10;
            else
                curArray(1,3) = 0;
            end

            typArray = circshift(typArray,[1 0]);
            typArray(1) = typTime;

            % estimate arrival time
            estArrive = addtodate(now,curTime+round(baseOther*estFac),'minute');
            estArriveStr = [datestr(estArrive,'HH:MM') ' (' num2str(curTime+round(baseOther*estFac)) ' min.)'];

            % plot the results
            hb = bar(time_axis,curArray,1,'stacked');
            set(hb(1),'FaceColor','g')
            set(hb(2),'FaceColor','y')
            set(hb(3),'FaceColor','r')
            hold on;
            plot(time_axis,typArray,'.-b','MarkerSize',12,'LineWidth',1);
            xlim([0 buf_length+1]);
            ya = ylim;
            ylim([20 ya(2)]);
            text(1.5,curTime+0.2,num2str(curTime));
            set(gca,'XDir','reverse')
            title(['Estimated Arrival Time: ' estArriveStr],'FontSize',16,'FontWeight','bold')
            xlabel(sprintf('Time since %s [min.]',datestr(d,'HH:MM')),'FontSize',14)
            ylabel('280S Travel Time [min.]','FontSize',14)
            if any(size(incidents)>0)
                legend(incidents,'Location','SouthWest')
            end
            drawnow
            hold off;

            % get new data every minute
            %jPause(60-d(6));

        catch                                                                   %#ok<CTCH>
            % catch errors with received data, try again
            jPause(1);
            failcount = failcount +1;
            if failcount > 5
                fprintf(1,'ERROR: Too many failures\n');
                break;
            end
        end
        
    end % end if on the minute

    drawnow
    jPause(1);
end
    
    
end % end function    
    
function jPause(tPauseSec)
	th = java.lang.Thread.currentThread();  %Get current Thread
	th.sleep(1000*tPauseSec)                %Pause thread, conversion to milliseconds
    
    
end % end function


function exitLoop(hObject,event)

global RUNLOOP
    
%disp(event)
switch event.Key
    case 'space'
        fprintf(1,'Function exit (space bar pressed)\n');
        RUNLOOP = 0;
end


end % end function
