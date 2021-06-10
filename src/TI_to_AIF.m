function [ t, Ca ] = TI_to_AIF( filename, SaO2, tHb, wv, inv, filt_method, savedata )
%TI_TO_AIF Summary of this function goes here
%   Detailed explanation goes here

% default input parameters
switch nargin 
    case 1 
        SaO2 = 0.98;
        tHb = 14;
        wv = [805 940];
        inv = 0;
        filt_method = 'upenn';
        savedata = 0;
    case 2
        tHb = 14;
        wv = [805 940];
        inv = 0;
        filt_method = 'upenn';
        savedata = 0;
    case 3
        wv = [805 940];
        inv = 0;
        filt_method = 'upenn';
        savedata = 0;
    case 4
        inv = 0;
        filt_method = 'upenn';
        savedata = 0;
    case 5
        filt_method = 'upenn';
        savedata = 0;
    case 6
        savedata = 0;
end

% open the Texas Instruments Volts output.
fid = fopen(filename);
X1 = textscan(fid,'%f %f %f %f %f %f','Headerlines',6);
fclose(fid);

fs = 500; %sampling rate
tbl = [10 60]; %reliable baseline data.

% red and ir channels (raw)
RED = X1{5}; 
IR = X1{6};

% RED = RED(245000:300000);
% IR = IR(245000:300000);


% if you're using the original Nihon Kohden probes, you'll want to flip
% these around.
if inv
    RED_t = RED;
    RED = IR;
    IR = RED_t;
end

% baseline signal from which to calculate heart-rate
RED_base = RED(1000:41000);
IR_base = IR(1000:41000);

% powerspectrum
[P,f] = pwelch([RED_base IR_base],[],[],[],fs);

bpm = f*60; 

% get heart-rate
figure;
plot(bpm,P);title('select the center of the heart-rate peak'); xlim([12 180]); xlabel('frequency (beats per min).');
[ghr,~]=ginput(1);
fhr = ghr/60;
close(gcf);


%% Demodulate signal and compute the flux ratio and concentration.

% get carrier signal from envelope
% % (could also apply a bandpass filter).
switch filt_method
    case 'demod'
        % fRED = demod(-log(RED),fhr,fs,'am');
        % fIR = demod(-log(IR),fhr,fs,'am');

        % FIX THE FILTERING HERE.. COMPARE WITH SIMPLE ...
         fRED = demod(-log(RED),fhr,fs,'amdsb-tc');
         fIR = demod(-log(IR),fhr,fs,'amdsb-tc');
        % 
    % % or just smooth
    case 'simple'
        fRED = smooth(-log(RED),20,'sgolay',3);
        fIR = smooth(-log(IR),20,'sgolay',3);

    % % 
    case 'butter'
    % bhi = fir2(50, [0 fhr/fs.*0.95 fhr/fs.*1.05 1], [0 0 1 1]);
    % fRED = filter(bhi, 1, RED);
    % fIR = filter(bhi, 1, IR);

% CUSTOM FILTER - UPENN METHOD (SLOW)
    case 'upenn'
        fhwid = 0.10;
        fl = (1-fhwid)*fhr;
        fh = (1+fhwid)*fhr;
        bpfilter = designfilt('bandpassfir', ...
            'StopbandFrequency1', fl-0.2, ...
            'PassbandFrequency1', fl, ...
            'PassbandFrequency2', fh, ...
            'StopbandFrequency2', fh+0.2, ...
            'StopbandAttenuation1', 60, ...
            'PassbandRipple', 1, ...
            'StopbandAttenuation2', 60, ...
            'SampleRate', fs, ...
            'DesignMethod', 'equiripple');

        fRED = filter(bpfilter,-log(RED));
        fIR = filter(bpfilter,-log(IR));
end
                 
% find the peaks - min peak distance is defined as half the heart-rate
[pksir,locsir] = findpeaks(fIR,'minpeakdistance',round((0.5/fhr)*fs));

% find the troughs
tir = zeros(1,length(locsir)-1);
minir = tir;
locsirmin = tir;
pksir = pksir(1:end-1)';
tmpt = (1:length(fIR))/fs;
for k = 1:length(locsir)-1
    tir(k) = mean(tmpt(locsir(k):locsir(k+1)));
    [minir(k), loctmp] = min(fIR(locsir(k):locsir(k+1)));
    locsirmin(k) = locsir(k) + loctmp - 1;
end

% interpolate red from IR peaks and troughs.
pksred = interp1(tmpt,fRED,tmpt(locsir(1:end-1)));
minred = interp1(tmpt,fRED,tmpt(locsirmin));

% truncate in case some channels are shorter than others (by usually 1 or
% 2)
trunc = min([length(pksred(:)) length(minred(:)) length(pksir(:)) length(minir(:))]);
pksred = pksred(1:trunc);
pksir = pksir(1:trunc);
minred = minred(1:trunc);
minir = minir(1:trunc);

% amplitude.
Ared = 0.5 * (pksred(:) - minred(:));
Air = 0.5 * (pksir(:) - minir(:));

[eHbO2red,eHbred,~,eicg] = getextinctioncoef(wv(1));
[eHbO2ir,eHbir] = getextinctioncoef(wv(2));

% flux of light. 
phi = Air ./ Ared;
I = (tir > tbl(1)) & (tir < tbl(2));
phi0 = mean(phi(I)); %choose a baseline Phi for d calculation.

% distance of expansion, which is converted to concentration.
d = phi0 * (eHbO2ir*SaO2 + eHbir*(1-SaO2)) / (eHbO2red*SaO2 + eHbred*(1-SaO2)); %find a d value to bring Ci to zero.
Ci = (phi/d*(eHbO2ir*SaO2 + eHbir*(1-SaO2)) - eHbO2red*SaO2 - eHbred*(1-SaO2))* tHb /eicg;

% iterpolate t and ca to the current temporal resolution of the SPY Elite,
% which is fast enough preserve any features. sgolay filtering 51 x 3.
t = linspace(tir(1),tir(end),tir(end)./0.267);
Ca = smooth(t,interp1(tir,Ci,t,'pchip'),51,'sgolay',3);
plot(t, Ca); xlabel('time (sec)'); ylabel('Concentration (uM)');

if savedata == 1
    xout = [t(:) Ca(:)]
    
    % parse the filename of the input file to suggest where to save the
    % output and what to call it.
    slashloc = strfind(filename,filesep);
    sugpath = filename(1:slashloc(end));
    fnamein = filename(slashloc(end)+1:end);
    emdashloc = strfind(fnamein,'_');
    fnameout = ['AIF_' fnamein(emdashloc(2)+1:strfind(fnamein,'.xls')-1) '.csv'];
    
    % open dialog for saving.
    [fname, fpath] = uiputfile({'*.csv'}, 'Save AIF as CSV file', [sugpath fnameout] )
    csvwrite([fpath fname],xout);
end

end

