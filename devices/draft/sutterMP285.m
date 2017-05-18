% SUTTERMP285 A class for using the Sutter MP-285 positioner
% 
% SUTTERMP285 implements a class for working with a Sutter MP-285
%   micro-positioner. The Sutter must be connected with a USB-to-Serial
%   converter if the computer does not have a serial port.
%
% This class is a subclass of "serial", so you can use the usual commands
%   for serial objects: get, set, fopen, fclose, fprintf, fscanf, fread.
%   The same properties exist as well: BaudRate, Terminator, etc. The
%   properties are set the appropriate values for the MP-285 by default.
%   However, to run the SIO test program, you may need to change the
%   BaudRate to 1200 (See Sutter Reference manual p23).
%
% Methods:
%   Create the object. The object is opened with FOPEN and the connection
%     is tested to verify that the Sutter is responding.
%       obj = sutterMP285(USBport)
%
%   Update the position display on the instrument panel (VFD)
%       updatePanel(obj)
%
%   Get the status information (step multiplier, velocity, resolution)
%       [stepMult, currentVelocity, vScaleFactor] = getStatus(obj)
%
%   Get the current absolute position in um
%       xyz_um = getPosition(obj)
%
%   Set the move velocity in steps/sec. vScaleFactor = 10|50 (default 10).
%       setVelocity(obj, velocity, vScaleFactor)
%
%   Move to a specified position in um [x y z]. Returns the elapsed time
%     for the move (command sent and acknowledged) in seconds.
%       moveTime = moveTo(obj,xyz)
%
%   Move to a position relative to the current position in um [x y z].
%     Returns the elapsed time for the move (command sent and acknowledged)
%     in seconds.
%       moveTime = translate(obj,xyz)
%
%   Set the current position to be the new origin (0,0,0)
%       setOrigin(obj)
%
%   Reset the instrument
%       sendReset(obj)
%
%   Close the connection to the instrument
%       fclose(obj)
%
%   Open the connection to the instrument
%       fopen(obj)
%
%
% Properties:
%   verbose - The level of messages displayed (0 - 2). Default 2.
%
%
% Example:
%
% >> sutter=sutterMP285('/dev/tty.usbserial-AE016TW4');
% sutterMP285: version 1.0
% sutterMP285: Sutter ready.
% >> sutter.verbose=1;
% >> p=getPosition(sutter)
% 
% p =
% 
%        -9600
%          100
%           10
% 
% >> translate(sutter,[100 50 -20]);
% >> updatePanel(sutter);
% >> fclose(sutter);
% >> clear sutter;
%
%
% M. Hopcroft
% mhopeng@gmail.com
% v1.1
%

% Jul2012
% v1.1  include setOrigin, sendReset
%       remove delete (serial destructor is better)
% v1.0
%

classdef sutterMP285 < serial
	
	properties
		% level of messages 
		verbose = 2;
	end
	
	properties (SetAccess = private, GetAccess = public)
        % version of this classdef file
        versionStr = 'version 1.1'
        % the step multiplier (usteps/step?) default for instrument is 25
        stepMult = 25;
        isOpen = 0;
	end
	
	properties (SetAccess = private, GetAccess = private)
        % long timeout to allow long travel commands to complete
        defaultTimeout = 60
    end
	

	%% PUBLIC METHODS
	methods
                
        %% Constructor
        % return instance of sutterMP285 class.
        % creates a serial port object
		function obj = sutterMP285(varargin)
            if nargin < 1
                fprintf(1,'sutterMP285: ERROR you must supply a USB port name\n');
                if ispc, fprintf(1,'    e.g., "s=sutterMP285(''COM4'')"\n');
                else fprintf(1,'    e.g., "s=sutterMP285(''/dev/tty.usbXXXX'')"\n');
                end
                if ~ispc
                    disp(ls('/dev/tty.*'))
                end
            end
            obj = obj@serial(varargin{1});
            if nargin > 1
                try
                    set(obj, varargin{2:end});
                catch aException
                    delete(obj);
                    localFixError(aException);
                end
            end
            % Explicitly set the correct properties for the Sutter serial port
            set(obj, 'BaudRate', 9600); %set to 9600 for programmed control, 1200 for SIO test (p23)
            set(obj, 'DataBits', 8);
            set(obj, 'DataTerminalReady', 'on');
            set(obj, 'FlowControl', 'none');
            set(obj, 'Parity', 'none');
            set(obj, 'ReadAsyncMode', 'continuous');
            set(obj, 'RequestToSend', 'on');
            set(obj, 'StopBits', 1);
            set(obj, 'Terminator', 'CR'); % set terminator to CR
            set(obj, 'Timeout',60); % long timeout allows large move commands to complete
            set(obj, 'Tag','SutterMP285');            
            set(obj,'Timeout',60);
            set(obj,'Tag','sutterMP285');
            if obj.verbose >= 1, fprintf(1,'sutterMP285: %s\n',obj.versionStr); end
            
            % verify Sutter connection/operation
            fopen(obj);
            % There appears to be some voodoo that requires a "setVelocity"
            %  call when the Sutter is first turned on. After that, the
            %  velocity can be set to any valid value.
            setVelocity(obj, 777, 10);
            [obj.stepMult, currentVelocity]=getStatus(obj);
            if currentVelocity==777
                fprintf(1,'sutterMP285: Sutter ready.\n');
                setVelocity(obj, 1000, 10);
                updatePanel(obj);
            else
                fprintf(1,'sutterMP285: WARNING Sutter did not respond at startup.\n');
            end
            
        end
        		
        
        %% Update Panel
        function updatePanel(obj)
        % causes the Sutter to display the XYZ info on the front panel
            fprintf(obj,'n'); % Sutter replies with a CR
            fread(obj,1,'int8'); % read and ignore the carriage return
        end % showPanel


        %% Get Status
        function [stepMult, currentVelocity, vScaleFactor]=getStatus(obj)
            % Sends the 'status' query to the Sutter and interprets the response.
            % Returns the current settings for step multiplier and velocity.

            if obj.verbose >= 2, fprintf(1,'sutterMP285: get status info:\n'); end
            fprintf(obj, 's'); % send status command
            statusbytes=fread(obj,32,'uint8');  % read the binary data
            fread(obj,1,'int8');  % read and ignore the carriage return at the end

            % the value of STEP_MUL ("Multiplier yields msteps/nm") is at bytes 25 & 26
            stepMult=double(statusbytes(26))*256+double(statusbytes(25));
            
            % the value of "XSPEED"  and scale factor is at bytes 29 & 30
            if statusbytes(30) > 127
                vScaleFactor = 50;
            else
                vScaleFactor = 10;
            end
            %disp(statusbytes(27:30))
            currentVelocity=double(bitand(127,statusbytes(30)))*256+double(statusbytes(29)); % mm/s?
            
            if obj.verbose >= 2,
                fprintf(1,' "step_mul" (usteps/um): %g\n',stepMult);
                fprintf(1,' "xspeed" [velocity] (usteps/sec): %g\n',currentVelocity);
                fprintf(1,' velocity scale factor (usteps/step): %g\n',vScaleFactor);
            end

        end % getStatus

        
        %% Get position
        function xyz_um=getPosition(obj)
            % Read the current position of the Sutter MP-285

            % The Sutter sends binary data in units = 25usteps.um, i.e., *0.04 microns, & carriage return
            % (e.g. 'c' returns xxxxyyyyzzzz as 3 signed long ints, and ASCII 13 for CR)

            fprintf(obj, 'c'); % send "c" command to get current position
            xyz=fread(obj,3,'int32');  % read the binary data
            fread(obj,1,'int8');  % read and ignore the carriage return at the end
            % use the step multiplier to get units
            % Are these units "um" or "nm"? Manual p67 says "nm", but front panel says "um"
            xyz_um=xyz./obj.stepMult;

            if obj.verbose >= 2
                % display the result
                fprintf(1,'sutterMP285: Stage Position:\n');
                fprintf(1,'  X: %g um\n  Y: %g um\n  Z: %g um\n',xyz_um(1),xyz_um(2),xyz_um(3));
            end
        end
        
        
        %% Translate
        function moveTime=translate(obj,xyz)
        % This function translates the sutter stage by distances [x;y;z] in um
        %  MOVETIME is the time between sending the command and receiving the
        %  response from the Sutter, which [should] indicate how long it took to
        %  complete the move.
        
            % ensure columns
            xyz=xyz(:);

            if obj.verbose >= 2, fprintf(1,'sutterMP285: Sutter translating %g %g %g um...\n',xyz); end

            here = getPosition(obj);

            moveTime=moveTo(obj,(here+xyz));
        end
        
        
        %% Move To Position
        function moveTime=moveTo(obj,xyz)
        % this function moves the sutter stage to [x;y;z] in um,
        %  origin in setup 6 at axes travel center

        % create a composite command, such as "move to position"
        %    "mxxxxyyyyzzzzCR", where x y z are signed long ints, units = steps 
        % send "m" command to get move to a position, ascii m=109
        % stepMult queried in status, should be 25 steps/um step resolution = 0.04 um

            % ensure that we have a column input
            xyz=xyz(:);
            
            % This section is commented out because the coordinates are
            %  relative to the origin set with setOrigin, so fixed limt
            %  checking is not appropriate. But its here if you want it.
            % % enforce travel limits
            % posLimit=12500; negLimit=-12500;
            % if any(xyz~=min(xyz,posLimit)) || any(xyz~=max(xyz,negLimit))
            %     fprintf(1,'sutterMP285: WARNING: movement restricted to travel limits %d,%d um\n',posLimit,negLimit);
            %     xyz=min(xyz,posLimit);
            %     xyz=max(xyz,negLimit);
            % end

            if obj.verbose >= 2, fprintf(1,'sutterMP285: Sutter moving to %g %g %g um...\n',xyz); end
            % convert to steps, and then convert to binary bytes
            %  (in a row instead of column)
            xyz_bytes = typecast(int32(xyz .* obj.stepMult),'uint8')';
            % add the "m" and the CR to create the move command
            move = [uint8(109) xyz_bytes uint8(13)];
            % send binary result to Sutter and measure time until move is acknowledged            
            fwrite(obj,move,'uint8'); tic
            % Sutter replies with a CR after move finishes
            cr=[]; %#ok<NASGU>
            cr=fread(obj,1,'uint8'); % The carriage return is sent after move completes
            moveTime=toc; % stop timer
            if isempty(cr)
                fprintf(1,'Sutter did not finish moving before timeout (%d sec).\n',get(obj,'Timeout'));
            else
                if obj.verbose >= 2, fprintf(1,'sutterMP285: Sutter move complete. (%.2f sec)\n',moveTime); end
            end

        end %sutterGoTo
        
        
        %% Set Origin
        function setOrigin(obj)
        % sets the origin of the coordinate system to the current position
            fprintf(obj,'o'); % Sutter replies with a CR
            fread(obj,1,'int8'); % read and ignore the carriage return       
        end % setOrigin
        
        
        %% Set Velocity
        function setVelocity(obj, velocity, vScaleFactor)
        % this function changes the velocity of the sutter motions

        % Change velocity command 'V'xxCR where xx= unsigned short (16bit) int velocity
        % set by bits 14 to 0, and bit 15 indicates ustep resolution  0=10, 1=50 uSteps/step
        % V is ascii 86
        
            if nargin < 3, vScaleFactor = 10; end

            % velocity units still unclear, seems to be steps/sec? 
            vv=typecast(uint16(velocity),'uint8');
            if vScaleFactor == 50
                vv(2)=vv(2)+128; % change MSB of 2nd byte to 1 for ustep resolution = 50
            end
            %dec2bin(vv)
            cmd=[uint8(86) vv uint8(13)];
            fwrite(obj,cmd,'uint8');
            % Sutter replies with a CR
            fread(obj,1,'int8');  % read and ignore the carriage return
        end % setVelocity
        
        
        %% Reset
        function sendReset(obj)
        % sets the origin of the coordinate system to the current position
            fprintf(obj,'r'); % Sutter does not reply
        end % setOrigin        
        

    end
        
end