function d = o_loadAIF( d, saveflag )
%O_LOADAIF This will load the AIF from the volts file (if unprocessed) or
%the AIF file (if available).
%   Detailed explanation goes here

% d - the DCE-FI datastructure. Fields critical for this function are:
%       d.dir, d.fname

% saveflag:
    %0 - attempt to load .aif, use volts but don't save as .aif
    %1 - attempt to load .aif, use volts and save if it doesn't exist (default)
    %2 - use volts and overwrite .aif if it exists

if nargin == 1
    saveflag = 1;
end
    
% first, check to see whether .aif is there
pred_file = [d.fname(1:max(strfind(d.fname,'_'))-1) '.aif'];

% if the .aif file exists, load it.

if (exist([d.dir pred_file]) == 2) && (saveflag ~= 2)
    
    % load the aif file
    M = csvread([d.dir pred_file]);
    
else %if there is no 'aif file' or if saveflag indicates it should be overwritten (opt 2).
    
    % first, check to see whether volts_file is there
    aif_path = [];
    files = dir(d.dir);
    for i = 3:length(files)
        if ~isempty(strfind(files(i).name, 'Volts'))
            aif_path = [d.dir files(i).name];
        end
    end
    
    if isempty(aif_path) %if a file couldn't be found
        %dlg "Could not locate the AIF file"
        hw1 = warndlg('Could not locate a .aif file or a Volts file','File Not Found');
    
    else %file was found with 'Volts' in it.
        filename = aif_path; 
        
        % input dialog to get physiological parameters.
        prompt = {'Enter SpO2 (%):','Enter total hemoglobin (g/dL):'};
        dlgtitle = 'Input'; dims = [1 35]; definput = {'97','14'};
        answer = inputdlg(prompt,dlgtitle,dims,definput);

        d.SaO2 = str2num(answer{1})./100; 
        d.tHb = str2num(answer{2}); %convert to num.
        wv = [804 938]; %wavelength of probe LEDs.

        % run TI_to_AIF and save
        filt_method = 'upenn'; % upenn is best, simple is faster.
        [ t, Ca ] = TI_to_AIF( filename, d.SaO2, d.tHb, wv, 0, filt_method, 0 );

        %select relevant portion of the curve
        h = imrect; 
        pos = getPosition(h);
        
        % crop to the approprate part.
        x1 = find(t>pos(1),1,'first');
        x2 = find(t>pos(3),1,'first');
        
        d_aif = interp1(t(x1:x2)-t(x1),Ca(x1:x2),d.t(:), 'linear', NaN );
        
        % if option 0 was chosen, do not save a .aif file, otherwise do.
        if saveflag ~= 0
            csvwrite([d.dir pred_file], [d.t(:) d_aif(:)]);
        end
    end
end

